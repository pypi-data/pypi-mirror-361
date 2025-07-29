def analyze_file(path: Path, project_root: Path):
    try:
        print(f"  {Style.BRIGHT}{path.relative_to(project_root)}{RESET}\n")

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        used_names = get_used_names(tree)
        imports = extract_imports(tree)

        if VERBOSE:
            print_verbose_debug(imports, used_names)

        alias_occurrences, conflict_aliases = detect_conflicts(imports)

        checked_aliases = []
        checked_fulls = []
        results_for_summary = defaultdict(list)

        import_line_code = extract_import_blocks(imports, source)

        for node, full, alias, lineno in imports:
            status, color, pre, post, module, conflictmarker = analyze_single_import(
                node, full, alias, lineno, used_names, checked_aliases,
                checked_fulls, alias_occurrences, conflict_aliases,
                path, project_root
            )

            checked_aliases.append(alias)
            checked_fulls.append(full)
            global_summary[str(path.name)]["total"] += 1
            print(f"{pre}    Line {lineno:>4} - {color}{status:<27}{RESET} {module} {conflictmarker}{post}")

            results_for_summary[lineno].append((alias, full, status, color))

        if VERBOSE:
            print_line_summary(results_for_summary)

        print_colored_import_lines(imports, results_for_summary, import_line_code)

    except SyntaxError as e:
        print(f"{Fore.RED}[ERR] Syntax error in {path}: {e}{RESET}")
    except Exception as e:
        print(f"{Fore.RED}[ERR] Failed to analyze {path}: {e}{RESET}")



def analyze_single_import(node, full, alias, lineno, used_names, checked_aliases, checked_fulls,
                          alias_occurrences, conflict_aliases, path, project_root):
    status = ""
    module = ""
    color = ""
    pre = ""
    post = ""
    conflictmarker = ""

    if alias in used_names:
        if full not in checked_fulls:
            status = "[OK]   used"
            color = Fore.GREEN
            if is_local_module(full, project_root):
                status = f"{Style.BRIGHT}{status}{Style.NORMAL} local module   "
                global_summary[str(path.name)]["used local"] += 1
            else:
                global_summary[str(path.name)]["used"] += 1
        else:
            if alias not in checked_aliases:
                pre, status, color, post = render_hidden_duplicate(alias, full, lineno, alias_occurrences)
                global_summary[str(path.name)]["hidden duplicate"] += 1
            else:
                status = "[!]    duplicate (" + str(checked_aliases.count(alias)) + ")"
                global_summary[str(path.name)]["duplicate"] += 1
                color = Fore.MAGENTA

    elif alias not in used_names:
        if is_local_module(full, project_root):
            status = f"[SKIP] {Style.BRIGHT}unused{Style.NORMAL} local module "
            color = Fore.CYAN
            global_summary[str(path.name)]["unused local"] += 1
        elif alias in checked_aliases or len(alias_occurrences[alias]) > 1:
            status = f"{Style.BRIGHT}[!!!]  unused & duplicate{RESET:<27}"
            color = Fore.RED
            global_summary[str(path.name)]["unused & duplicate"] += 1
        else:
            status = "[!!]   unused"
            global_summary[str(path.name)]["unused"] += 1
            color = Fore.RED
    else:
        status = f"{Style.BRIGHT}[!!!!] Rest (this should never happen!!!){Style.RESET}"
        color = Fore.RED

    if alias in conflict_aliases:
        conflictmarker = f" {Fore.YELLOW}{Style.BRIGHT}[conflict !!!]{RESET}"

    module = module or f"{alias} {color}from{RESET} {full}"
    return status, color, pre, post, module, conflictmarker


