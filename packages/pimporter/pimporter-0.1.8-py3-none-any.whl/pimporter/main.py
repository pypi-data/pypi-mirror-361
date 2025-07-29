from pathlib import Path
import argparse

import ast
from typing import List, Tuple, Set
from collections import defaultdict, Counter
from colorama import init, Fore, Style
import re
import textwrap

init(autoreset=True)
RESET = Style.RESET_ALL
VERBOSE = 0

# Globales Statistik-Dictionary
global_summary = defaultdict(Counter)

def find_py_files(root: Path) -> List[Path]:
    # Verzeichnisse, die ausgeschlossen werden sollen
    EXCLUDED_DIRS = {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".venv",
        "venv",
        "env",
        "build",
        "dist",
        ".eggs",
        ".tox",
        ".idea",
        ".vscode",
        ".coverage",
        ".pylint.d",
    }

    return [
        p for p in root.rglob("*.py")
        if not any(part in EXCLUDED_DIRS for part in p.parts)    
    ]

def extract_imports(tree: ast.AST) -> List[Tuple[ast.AST, str, str, int]]:
        # Analysiert ein Python-AST (tree) und extrahiert daraus alle Importanweisungen
        #    gibt dabei strukturierte Informationen zu jedem einzelnen importierten Namen zurück
        #       node: vollständiges ast.Import oder ast.ImportFrom Objekt
        #       full_name: voller Modulname, z.B. "os.path" oder "numpy.array"
        #       local_name: Name, unter dem das importierte Objekt im lokalen Code verfügbar ist (z.B. "np" bei import numpy as np)
        #       lineno: Die Zeilennummer im Originalcode

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = getattr(node, "module", "")
            for alias in node.names:
                local_name = alias.asname or alias.name
                full_name = f"{module}.{alias.name}" if module else alias.name
                imports.append((node, full_name, local_name, node.lineno))
    return imports

def get_used_names(tree: ast.AST) -> Set[str]:
        # Analysiert Code als AST tree und gibt eine Menge (set) aller Variablennamen
        #    (und einiger Objektverwendungen) zurück, die im Code verwendet werden
        # Extrahiert alle verwendeten Bezeichnernamen und berücksichtigt auch Attributzugriffe,
        #    aber nur den linken Teil (obj aus obj.attr)
        # Ist nützlich, z.B. um tote (unbenutzte) Importe zu finden, zu analysieren, ob bestimmte
        #    Variablen im Code verwendet werden, oder einfache statische Code-Checks durchzuführen
    used = set()
    class UsageVisitor(ast.NodeVisitor):
        def visit_Name(self, node): used.add(node.id)
        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name):
                used.add(node.value.id)
            self.generic_visit(node)
    UsageVisitor().visit(tree)

    return used

def is_local_module(full_name: str, project_root: Path) -> bool:
    parts = full_name.split(".")
    for i in range(len(parts), 0, -1):
        candidate = project_root.joinpath(*parts[:i]).with_suffix(".py")
        if candidate.exists():
            return True
    return False

def print_verbose_debug(imports, used_names):
    full_names = [i[1] for i in imports]
    local_names = [i[2] for i in imports]
    message = (
        "--------------------------------------------------------------------------------\n"
        f"used names in code:\n  {used_names}\n"
        "--------------------------------------------------------------------------------\n"
        f"full_name:\n {full_names}\n"
        "--------------------------------------------------------------------------------\n"
        f"local_names:\n {local_names}\n"
        "--------------------------------------------------------------------------------\n"
    )
    for line in message.splitlines():
        print(textwrap.indent(textwrap.fill(line, width=80), prefix="    "))

def extract_import_blocks(imports, source):
    import_line_code = {}
    lines = source.splitlines()
    for node, *_ in imports:
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        if start not in import_line_code:
            block = "\n".join(lines[i - 1] for i in range(start, end + 1))
            import_line_code[start] = block
    return import_line_code

def detect_conflicts(imports):
    # Voranalyse: Zähle, wie oft ein Alias verwendet wird (egal woher)
    alias_occurrences = defaultdict(list)
    conflict_aliases = set()

    for node, full, alias, lineno in imports:
        alias_occurrences[alias].append((full, alias, lineno))

    for alias, occurrences in alias_occurrences.items():
        full_names = {f for f, _, _ in occurrences}
        if len(full_names) > 1:
            print(f"  {Fore.RED}[!!!] Conflict:{Fore.YELLOW}{Style.BRIGHT} Alias '{alias}' is used for multiple modules:{RESET}")
            for full, _, lineno in occurrences:
                print(f"    {Style.DIM}Line {lineno:<4}{RESET} -> {Fore.YELLOW}{Style.BRIGHT}{full}{RESET} as {Fore.YELLOW}{Style.BRIGHT}{alias}{RESET}")
            print()
            conflict_aliases.add(alias)

    return alias_occurrences, conflict_aliases

def analyze_file(path: Path, project_root: Path):
    try:
        print(f"  {Style.BRIGHT}{path.relative_to(project_root)}{RESET}\n")

        source = path.read_text(encoding="utf-8") # Source Code
        tree = ast.parse(source)
        # AST (Abstract Syntax Tree) erzeugen und zeichnen 
        #    strukturierte Darstellung des Codes als Baum verschachtelter Objekte
        
        used_names = get_used_names(tree) # Menge von Variablennamen und Objektverwendungen aus dem Code
        imports = extract_imports(tree) # Liste der imports als [(node, full_name, local_name(name/asname), lineno), ...]

        if VERBOSE:
            print_verbose_debug(imports, used_names)

        alias_occurrences, conflict_aliases = detect_conflicts(imports)

        checked_aliases = []  # speichern geprüften aliases als Liste
        checked_fulls = []  # speichern geprüften fulls als Liste
        results_for_summary = defaultdict(list)

        import_line_code = extract_import_blocks(imports, source)

        for node, full, alias, lineno in imports:
            status = ""
            module = ""
            color = ""
            pre = ""
            post = ""
            conflictmarker = ""

            if alias in used_names:
                # wird im Code verwendet
                if full not in checked_fulls:
                    # wurde noch nicht hier geprüft
                    status = f"[OK]   used"
                    color = Fore.GREEN
                    if is_local_module(full, project_root):
                            status = f"{Style.BRIGHT}{status}{Style.NORMAL} local module   "
                            global_summary[str(path.name)]["used local"] += 1
                    else:
                        global_summary[str(path.name)]["used"] += 1
                else:
                    # wurde bereits hier geprüft
                    if alias not in checked_aliases:
                        # full kam schon vor, aber alias noch nicht -> hidden duplicate!
                        pre, status, color, post, module = render_hidden_duplicate(alias, full, lineno, alias_occurrences, module)
                        global_summary[str(path.name)]["hidden duplicate"] += 1
                    else:
                        # full kam schon vor, und alias auch -> normales duplicate!
                        status = "[!]    duplicate (" + str(checked_aliases.count(alias)) + ")"
                        global_summary[str(path.name)]["duplicate"] += 1
                        color = Fore.MAGENTA

            elif alias not in used_names:
                if is_local_module(full, project_root):
                    status = f"[SKIP] {Style.BRIGHT}unused{Style.NORMAL} local module "
                    color = Fore.CYAN
                    global_summary[str(path.name)]["unused local"] += 1
                elif alias in checked_aliases or len(alias_occurrences[alias]) > 1:
                    status = f"[!!!]  unused & duplicate"
                    status = f"{status:<27}"
                    status = f"{Style.BRIGHT}{status}{RESET}"
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

            checked_aliases.append(alias)  # Anhängen statt add()
            checked_fulls.append(full)  # Anhängen statt add()
            global_summary[str(path.name)]["total"] += 1

            print(f"{pre}    Line {lineno:>4} - {color}{status:<27}{RESET} {module} {conflictmarker}{post}")
            
            results_for_summary[lineno].append((alias, full, status, color))


        if VERBOSE: # Zusammenfassung: Gruppiert nach Zeile, farbig markiert
            print_line_summary(results_for_summary)
       
        print_colored_original_import_lines(imports, results_for_summary, import_line_code)

    except SyntaxError as e:
        print(f"{Fore.RED}[ERR] Syntax error in {path}: {e}{RESET}")
    except Exception as e:
        print(f"{Fore.RED}[ERR] Failed to analyze {path}: {e}{RESET}")


def render_hidden_duplicate(alias, full, lineno, alias_occurrences, module):
    pre = "    ________________________________________________________________________________\n"
    status = f"[!]    hidden duplicate "
    status = f"{status:<27}"
    status = f"{Style.BRIGHT}{status}{RESET}"
    color = Fore.MAGENTA
    
    module = f"{alias} {color}{Style.BRIGHT}from{RESET} {full}"
    post = f"\n        |  {color}{Style.BRIGHT}Full name:{RESET} {full}{color}{Style.BRIGHT} -> imported here as:{RESET} {alias}\n"
    
    matches = [
        (a, f, n, l)
        for a, occurrences in alias_occurrences.items()
        for f, n, l in occurrences
        if f == full and lineno != l # exclude the same line
    ]
    for n, f, a, l in matches:
        post += f"        |    {Style.BRIGHT}{color}also imported{RESET} {f} {Style.BRIGHT}{color}in Line {l} as{RESET} {a}\n"
    post += "    ____________________________________________________________________________\n"
    return pre, status, color, post, module


def print_module_summary(results_for_summary):
    print(f"\n{Style.DIM}Module Summary:{RESET}")
    for lineno in sorted(results_for_summary):
        items = results_for_summary[lineno]
        modules_formatted = ", ".join(
            f"{color}{alias}{RESET}" for alias, _, _, color in items
        )
        print(f"  Line {lineno}: {modules_formatted}")

def print_colored_original_import_lines(imports, results_for_summary, import_line_code):
    print(f"\n{Style.DIM}Detected Import Summary:{RESET}")
    for lineno in sorted(results_for_summary):
        first_node = next((node for node, *_ in imports if node.lineno == lineno), None)
        if not first_node:
            continue

        start = first_node.lineno
        end = getattr(first_node, "end_lineno", start)
        orig_lines = "\n".join(import_line_code.get(i, "") for i in range(start, end + 1))

        colored_line = orig_lines

        # Ergebnis wird Zeichen für Zeichen aufgebaut
        offset = 0
        for alias, _, _, color in results_for_summary[lineno]:
            # Suche nächstes Vorkommen von alias hinter dem aktuellen Offset
            match = re.search(rf'\b{re.escape(alias)}\b', colored_line[offset:])
            if not match:
                continue
            start_idx = offset + match.start()
            end_idx = offset + match.end()

            # Ersetze mit Farbe
            colored_alias = f"{color}{alias}{RESET}"
            colored_line = colored_line[:start_idx] + colored_alias + colored_line[end_idx:]

            # Aktualisiere Offset, damit nachfolgende Treffer nicht doppelt matchen
            offset = start_idx + len(colored_alias)

        print(f"L{start:<2} {colored_line}")

def print_summary():
    spacer=1
    lengths = [32, 5, 4+spacer, 5+spacer, 9+spacer, 9+spacer, 9+spacer, 6+spacer, 6+spacer]
    header = (
        " {:<{w0}}{:>{w1}}{:>{w2}}{:>{w3}}{:>{w4}}{:>{w5}}{:>{w6}}{:>{w7}}{:>{w8}}\n"
        " {:<{w0}}{:>{w1}}{:>{w2}}{:>{w3}}{:>{w4}}{:>{w5}}{:>{w6}}{:>{w7}}{:>{w8}}").format(
             "",      "",     "",  "Used",    "Hidden",   "Regular",    "Unused",       "", "Unused",
        "Datei", "Total", "Used", "Local", "Duplicate", "Duplicate", "Duplicate", "Unused", "Local",
        w0=lengths[0], w1=lengths[1], w2=lengths[2], w3=lengths[3],
        w4=lengths[4], w5=lengths[5], w6=lengths[6], w7=lengths[7], w8=lengths[8]
    )

    print(f"\n\n{Style.BRIGHT} Summary of Analysis:{RESET}")
    print(header)
    print(" " + "=" * round((len(header)/2)-1))
    
    for filename, stats in global_summary.items():
        print((
            " {:<{w0}}{:>{w1}}{:>{w2}}{:>{w3}}{:>{w4}}{:>{w5}}{:>{w6}}{:>{w7}}{:>{w8}}").format(
            filename, stats["total"], stats["used"], stats["used local"], stats["hidden duplicate"],
            stats["duplicate"], stats["unused & duplicate"], stats["unused"], stats["unused local"],
            w0=lengths[0], w1=lengths[1], w2=lengths[2], w3=lengths[3],
            w4=lengths[4], w5=lengths[5], w6=lengths[6], w7=lengths[7], w8=lengths[8]
        ))

def analyze_project(root):
    files = find_py_files(root)
    print(" ")
    print(f"{Style.BRIGHT}>>> Scanning {len(files)} Python files in '{root.name}'...\n")
    
    for f in files:
        if 'main_window.py' in f.name:
            analyze_file(f, root)
    print_summary()

def main():
    parser = argparse.ArgumentParser(description="Analyze Python imports for alias issues.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the directory to scan (default: current directory)"
    )
    args = parser.parse_args()

    project_root = Path(args.path).resolve()
    analyze_project(project_root)


if __name__ == "__main__":
    main()


