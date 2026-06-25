#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notes — Technical Arts MTY · student chapter

Terminal tool for the chapter. Cross-platform (Windows/macOS/Linux), only needs
Python 3 and git. Built to be fast: you write and it publishes.

Quick use:
    notes                      interactive interface (banner + menu)
    notes "what I did today"   save a note and publish it instantly
    notes projects             status of the active projects
    notes github               common git/GitHub commands
    notes cite                 log a measurement (physics standard) or a reference
    notes session              close a work session and push it to the wiki
    notes tasks                task board (also: notes tasks new | done <id>)
    notes --help               help

Tip: set your name so your notes are signed:
    Windows :  set TA_AUTHOR=German
    Unix    :  export TA_AUTHOR=German
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Chapter configuration
# --------------------------------------------------------------------------- #

ROSTER = ["Alfred RS", "Aaron Dir", "German GH", "Edgar Mth", "—", "—", "—"]

PROJECTS = {
    "DT-HRES": "projects/DT-HRES",
    "Michelson Interferometer": "projects/Michelson_Interferometer",
}

WIDTH = 64  # interface width

# --------------------------------------------------------------------------- #
#  Color / terminal
# --------------------------------------------------------------------------- #

def _enable_ansi():
    """Enable ANSI escape codes on Windows consoles."""
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass

_enable_ansi()

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
def _c(code):
    return code if _COLOR else ""

CYAN  = _c("\033[36m")
GREEN = _c("\033[32m")
DIM   = _c("\033[2m")
BOLD  = _c("\033[1m")
RESET = _c("\033[0m")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def _write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

# --------------------------------------------------------------------------- #
#  git helpers
# --------------------------------------------------------------------------- #

def run(cmd, cwd=None):
    """Run a command and return (code, stdout, stderr)."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"

def repo_root():
    """Root path of the 'notas' repo if we are inside it, else None."""
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"])
    return out.strip() if code == 0 else None

def author():
    return (os.environ.get("TA_AUTHOR")
            or os.environ.get("USERNAME")
            or os.environ.get("USER")
            or "anonymous")

def publish(paths, message):
    """add + commit + push. If push fails, the note is still saved locally."""
    root = repo_root()
    if not root:
        print(f"{DIM}You are not inside the 'notas' repo.{RESET}")
        print("  git clone https://github.com/Technical-Arts-MTY/notas.git")
        print("  cd notas")
        return False
    run(["git", "pull", "--quiet", "--no-rebase"], cwd=root)  # best effort
    run(["git", "add"] + paths, cwd=root)
    code, out, err = run(["git", "commit", "-m", message], cwd=root)
    if code != 0 and "nothing to commit" in (out + err):
        print(f"{DIM}Nothing new to publish.{RESET}")
        return True
    code, out, err = run(["git", "push"], cwd=root)
    if code != 0:
        print(f"{DIM}Saved and committed locally, but the push failed:{RESET}")
        last = (err or out).strip().splitlines()[-1] if (err or out).strip() else ""
        print("  " + last)
        print(f"  Check your session:  {BOLD}gh auth login{RESET}  (or push manually)")
        return False
    print(f"{GREEN}Published \u2713{RESET}")
    return True

# --------------------------------------------------------------------------- #
#  ASCII art: dancers and animated diagonal
# --------------------------------------------------------------------------- #

# Five little humans. Two frames that alternate -> they look like they dance.
_DANCE_A = [
    " \\o/    o     \\o/    o     \\o/ ",
    "  |    /|\\     |    /|\\     |  ",
    " / \\   / \\    / \\   / \\    / \\ ",
]
_DANCE_B = [
    "  o    \\o/     o    \\o/     o  ",
    " /|\\    |     /|\\    |     /|\\ ",
    " / \\   / \\    / \\   / \\    / \\ ",
]
_W = max(len(l) for l in _DANCE_A + _DANCE_B)

def _dance_frame(i):
    return [l.ljust(_W) for l in (_DANCE_A if i % 2 == 0 else _DANCE_B)]

def _center(line, width=WIDTH):
    return line.center(width)

# --------------------------------------------------------------------------- #
#  Interface
# --------------------------------------------------------------------------- #

def _roster_bar():
    names = " · ".join(ROSTER)
    return f"{DIM}{_center(names)}{RESET}"

def _dancers_static(frame=0):
    return "\n".join(f"{CYAN}{_center(l)}{RESET}" for l in _dance_frame(frame))

def intro():
    """Startup animation: first 'notes', then Technical Arts with the animated
    diagonal / | \\ , and the dancers moving."""
    clear()
    print()
    print(_roster_bar())
    print()
    # 1) first it says notes
    title = "n o t e s"
    _write("\n" + " " * ((WIDTH - len(title)) // 2))
    for ch in title:
        _write(BOLD + ch + RESET)
        time.sleep(0.045)
    print("\n")
    # 2) Technical Arts with the spinning diagonal next to it
    spins = ["/", "|", "\\"]
    left = "Technical Arts "
    base = (WIDTH - (len(left) + 1)) // 2
    for i in range(12):
        line = " " * base + left + CYAN + spins[i % 3] + RESET
        _write("\r" + line)
        time.sleep(0.085)
    print("\n")
    # 3) the little humans dance a few frames
    for l in _dance_frame(0):
        print(f"{CYAN}{_center(l)}{RESET}")
    for i in range(1, 7):
        _write("\033[3A")  # move up 3 lines
        for l in _dance_frame(i):
            _write("\r\033[K" + f"{CYAN}{_center(l)}{RESET}" + "\n")
        time.sleep(0.16)
    time.sleep(0.2)

def static_menu():
    clear()
    rule = "─" * WIDTH
    print()
    print(_roster_bar())
    print(f"{DIM}{rule}{RESET}")
    print()
    print(f"{BOLD}{_center('n o t e s')}{RESET}")
    print(f"{_center('Technical Arts ' + CYAN + '/' + RESET)}")
    print()
    options = [
        ("1", "Write note", "4", "Cite (physics standard)"),
        ("2", "Active projects", "5", "End session \u2192 wiki"),
        ("3", "GitHub guide", "6", "Tasks"),
        ("q", "Quit", " ", ""),
    ]
    for a, ta, b, tb in options:
        left = f"  {CYAN}[{a}]{RESET} {ta}"
        right = f"{CYAN}[{b}]{RESET} {tb}" if tb else ""
        print(f"{left:<38}{right}")
    print()
    print(_dancers_static(0))
    print()

def pause():
    try:
        input(f"\n{DIM}  Press Enter to go back to the menu...{RESET}")
    except EOFError:
        pass

# --------------------------------------------------------------------------- #
#  Action: write note
# --------------------------------------------------------------------------- #

def write_note(text=None):
    if text is None:
        print(f"\n{BOLD}Write your note.{RESET} {DIM}(empty line to finish){RESET}\n")
        lines = []
        while True:
            try:
                l = input("  ")
            except EOFError:
                break
            if l == "" and lines:
                break
            if l == "" and not lines:
                continue
            lines.append(l)
        text = "\n".join(lines).strip()
    if not text:
        print(f"{DIM}Empty, nothing is published.{RESET}")
        return
    root = repo_root() or "."
    folder = os.path.join(root, "log")
    os.makedirs(folder, exist_ok=True)
    now = datetime.now()
    file = os.path.join(folder, now.strftime("%Y-%m") + ".md")
    fresh = not os.path.exists(file)
    with open(file, "a", encoding="utf-8") as f:
        if fresh:
            f.write(f"# Logbook {now.strftime('%Y-%m')}\n")
        f.write(f"\n### {now.strftime('%Y-%m-%d %H:%M')} · {author()}\n{text}\n")
    summary = " ".join(text.split())[:50]
    publish([file], f"note: {summary}")

# --------------------------------------------------------------------------- #
#  Action: show projects
# --------------------------------------------------------------------------- #

def show_projects():
    root = repo_root() or "."
    print()
    for name, path in PROJECTS.items():
        print(f"{BOLD}{CYAN}▌ {name}{RESET}")
        p = os.path.join(root, path, "PROGRESS.md")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                lines = [l.rstrip() for l in f.readlines()]
            shown = 0
            for l in lines:
                if l.startswith("# "):
                    continue
                print("  " + l)
                shown += 1
                if shown >= 22:
                    print(f"  {DIM}... (open {path}/PROGRESS.md for the details){RESET}")
                    break
        else:
            print(f"  {DIM}(no PROGRESS.md yet){RESET}")
        print()

# --------------------------------------------------------------------------- #
#  Action: GitHub guide
# --------------------------------------------------------------------------- #

GUIDE = """
QUICK GIT / GitHub GUIDE  ·  Technical Arts MTY

  FIRST TIME (clone the repo)
    gh repo clone Technical-Arts-MTY/notas      clone with GitHub CLI
    cd notas                                    enter the folder
    gh auth login                               sign in (if asked)

  THE EVERYDAY CYCLE
    git pull                                    get the latest before you work
    ...you work...
    git status                                  see what changed
    git add .                                   stage all changes
    git commit -m "what I did"                   save a checkpoint with a message
    git push                                    upload it to GitHub

  EDIT THE README (or any file)
    1. open README.md and edit it
    2. git add README.md
    3. git commit -m "update README"
    4. git push

  REVIEW
    git log --oneline                           short history
    git diff                                     see uncommitted changes

  BRANCHES (for big changes without breaking the rest)
    git switch -c my-branch                      create and switch to a branch
    git switch main                             go back to the main branch
    git merge my-branch                          merge into where you are

  IF THE PUSH IS REJECTED (someone pushed first)
    git pull                                     fetch and merge their work
    (resolve conflicts if any, then)
    git add .  &&  git commit  &&  git push

  CREATE A NEW REPO
    gh repo create Technical-Arts-MTY/NAME --private --clone

  Chapter shortcut: instead of the 4 steps above, use
    notes "what I did"       <- saves to the logbook and pushes on its own
"""

def github_guide():
    root = repo_root() or "."
    p = os.path.join(root, "guides", "github.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            print("\n" + f.read())
    else:
        print(GUIDE)

# --------------------------------------------------------------------------- #
#  Action: cite (physics standard) / reference
# --------------------------------------------------------------------------- #

def _ask(label, default=""):
    extra = f" {DIM}[{default}]{RESET}" if default else ""
    try:
        r = input(f"  {label}{extra}: ").strip()
    except EOFError:
        r = ""
    return r or default

def cite():
    print(f"\n{BOLD}Log{RESET}  [{CYAN}m{RESET}] measurement (physics standard)   "
          f"[{CYAN}r{RESET}] bibliographic reference")
    try:
        kind = input("  > ").strip().lower()
    except EOFError:
        kind = "m"

    if kind.startswith("r"):
        _cite_reference()
    else:
        _cite_measurement()

def _cite_measurement():
    print(f"\n{DIM}Document the measurement with SI units, uncertainty and calibration.{RESET}\n")
    quantity = _ask("Quantity (e.g. wavelength)")
    symbol   = _ask("Symbol", "x")
    value    = _ask("Value")
    uncert   = _ask("Uncertainty (±)", "—")
    unit     = _ask("SI unit (m, s, V, nm, ...)")
    instr    = _ask("Instrument")
    calib    = _ask("Calibration (yes/no)", "no")
    calref   = _ask("  Calibration reference/date", "—") if calib.lower().startswith("y") else "—"
    cond     = _ask("Conditions (T, humidity, setup...)", "—")
    method   = _ask("Method", "—")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = (
        f"\n### Measurement: {quantity} ({symbol})\n"
        f"- **Value:** {value} ± {uncert} {unit}\n"
        f"- **Instrument:** {instr}\n"
        f"- **Calibration:** {calib} — {calref}\n"
        f"- **Conditions:** {cond}\n"
        f"- **Method:** {method}\n"
        f"- **Recorded:** {now} · {author()}\n"
    )
    print(f"\n{GREEN}Generated block:{RESET}")
    print(block)
    _save_to_project(block, "measurements.md", f"measurement: {quantity} ({symbol})")

def _cite_reference():
    print(f"\n{DIM}Generate a BibTeX entry for your LaTeX reports.{RESET}\n")
    kind   = _ask("Type (article/book/misc)", "article")
    key    = _ask("Cite key (e.g. born1999principles)")
    auth   = _ask("Author(s)")
    title  = _ask("Title")
    year   = _ask("Year")
    source = _ask("Journal / publisher", "—")

    bib = (
        f"@{kind}{{{key or 'ref'},\n"
        f"  author  = {{{auth}}},\n"
        f"  title   = {{{title}}},\n"
        f"  journal = {{{source}}},\n"
        f"  year    = {{{year}}}\n"
        f"}}\n"
    )
    print(f"\n{GREEN}BibTeX entry:{RESET}")
    print(bib)
    root = repo_root() or "."
    file = os.path.join(root, "references.bib")
    with open(file, "a", encoding="utf-8") as f:
        f.write("\n" + bib)
    print(f"{DIM}Added to references.bib{RESET}")
    publish([file], f"ref: {key or title[:40]}")

def _save_to_project(block, dest_file, message):
    print(f"{DIM}Which project?{RESET}")
    projects = list(PROJECTS.items())
    for i, (name, _) in enumerate(projects, 1):
        print(f"  [{i}] {name}")
    print("  [0] just show it (don't save)")
    try:
        sel = input("  > ").strip()
    except EOFError:
        sel = "0"
    if sel in ("", "0"):
        print(f"{DIM}Not saved. Copy it from above if you need it.{RESET}")
        return
    try:
        path = projects[int(sel) - 1][1]
    except (ValueError, IndexError):
        print(f"{DIM}Invalid option.{RESET}")
        return
    root = repo_root() or "."
    dest = os.path.join(root, path, dest_file)
    fresh = not os.path.exists(dest)
    with open(dest, "a", encoding="utf-8") as f:
        if fresh:
            f.write(f"# Measurements — {projects[int(sel)-1][0]}\n")
        f.write(block)
    publish([dest], message)

# --------------------------------------------------------------------------- #
#  Action: end session -> wiki
# --------------------------------------------------------------------------- #

def _origin_url():
    code, out, _ = run(["git", "remote", "get-url", "origin"])
    return out.strip() if code == 0 else None

def _wiki_url(origin):
    return (origin[:-4] + ".wiki.git") if origin.endswith(".git") else origin + ".wiki.git"

def _wiki_dir(origin):
    name = origin.rstrip("/").split("/")[-1].replace(".git", "")
    return Path.home() / ".technical-arts" / (name + ".wiki")

def _ensure_wiki(origin):
    """Clone or update the wiki repo. Returns (Path, ok)."""
    wdir = _wiki_dir(origin)
    wurl = _wiki_url(origin)
    if (wdir / ".git").exists():
        run(["git", "pull", "--quiet", "--no-rebase"], cwd=str(wdir))
        return wdir, True
    wdir.parent.mkdir(parents=True, exist_ok=True)
    code, out, err = run(["git", "clone", wurl, str(wdir)])
    if code != 0:
        return None, False
    return wdir, True

def _wiki_page(project_name):
    return project_name.replace(" ", "-") + ".md"

def end_session():
    root = repo_root()
    if not root:
        print(f"{DIM}Enter the repo first: cd notas{RESET}")
        return
    origin = _origin_url()
    if not origin:
        print(f"{DIM}This repo has no 'origin' configured.{RESET}")
        return

    print(f"\n{BOLD}End work session{RESET}  →  documented and pushed to the wiki\n")
    projects = list(PROJECTS.items())
    for i, (name, _) in enumerate(projects, 1):
        print(f"  [{i}] {name}")
    try:
        sel = input("  Project > ").strip()
        project = projects[int(sel) - 1][0]
    except (EOFError, ValueError, IndexError):
        print(f"{DIM}Invalid option.{RESET}")
        return

    participants = _ask("Participants (comma-separated)", author())
    print(f"\n{DIM}What was done (empty line to finish):{RESET}")
    done = []
    while True:
        try:
            l = input("  - ")
        except EOFError:
            break
        if l == "":
            break
        done.append(f"- {l}")
    measurements = _ask("Measurements / key data (or reference)", "—")
    pending = _ask("Pending / next step", "—")

    date = datetime.now().strftime("%Y-%m-%d")
    section = (
        f"\n---\n\n## Session {date}\n\n"
        f"**Participants:** {participants}\n\n"
        f"**Done:**\n" + ("\n".join(done) if done else "- —") + "\n\n"
        f"**Measurements / data:** {measurements}\n\n"
        f"**Pending:** {pending}\n\n"
        f"*Standard: SI units · value ± uncertainty · calibration state stated.*\n"
    )

    print(f"\n{DIM}Connecting to the wiki...{RESET}")
    wdir, ok = _ensure_wiki(origin)
    if not ok:
        print(f"{DIM}The wiki does not exist yet.{RESET}")
        print(f"  Open it ONCE on GitHub:  {origin.replace('.git','')}/wiki")
        print(f"  ('Create the first page', save) and run {BOLD}notes session{RESET} again.")
        return

    page = wdir / _wiki_page(project)
    fresh = not page.exists()
    with open(page, "a", encoding="utf-8") as f:
        if fresh:
            f.write(f"# {project} — Session log\n")
        f.write(section)

    run(["git", "add", "."], cwd=str(wdir))
    run(["git", "commit", "-m", f"session {project} {date}"], cwd=str(wdir))
    code, out, err = run(["git", "push"], cwd=str(wdir))
    if code == 0:
        print(f"{GREEN}Session published to the wiki \u2713{RESET}")
        print(f"  {origin.replace('.git','')}/wiki/{_wiki_page(project)[:-3]}")
    else:
        print(f"{DIM}Written locally but the push to the wiki failed:{RESET}")
        last = (err or out).strip().splitlines()[-1] if (err or out).strip() else ""
        print("  " + last)

# --------------------------------------------------------------------------- #
#  Interactive menu and main
# --------------------------------------------------------------------------- #

def _tasks_menu():
    """Task board inside notes, with quick add and close."""
    try:
        import tasks
    except Exception:
        print(f"  {DIM}tasks.py not found in the repo.{RESET}")
        return
    tasks.show()
    try:
        sub = input(f"  {DIM}[n] new  ·  [d] done <id>  ·  [Enter] back{RESET} > ").strip().lower()
    except EOFError:
        return
    if sub.startswith("n"):
        tasks.new()
    elif sub.startswith("d"):
        parts = sub.split()
        if len(parts) >= 2:
            tasks.done(parts[1])
        else:
            idd = input("  ID to mark done: ").strip()
            if idd:
                tasks.done(idd)

def menu():
    intro()
    while True:
        static_menu()
        try:
            op = input(f"  {CYAN}>{RESET} ").strip().lower()
        except EOFError:
            print()
            break
        if op in ("1", "n", "note"):
            write_note(); pause()
        elif op in ("2", "p", "projects"):
            show_projects(); pause()
        elif op in ("3", "g", "github"):
            github_guide(); pause()
        elif op in ("4", "c", "cite"):
            cite(); pause()
        elif op in ("5", "s", "session"):
            end_session(); pause()
        elif op in ("6", "t", "tasks", "task"):
            _tasks_menu(); pause()
        elif op in ("q", "quit", "exit"):
            print(f"  {DIM}See you.{RESET}")
            break
        else:
            print(f"  {DIM}Invalid option.{RESET}")
            time.sleep(0.6)

def help_text():
    print(__doc__)

def main():
    args = sys.argv[1:]
    if not args:
        menu()
        return
    kw = args[0].lower()
    if kw in ("projects", "p"):
        show_projects()
    elif kw in ("github", "g", "guide"):
        github_guide()
    elif kw in ("cite", "c"):
        cite()
    elif kw in ("session", "s"):
        end_session()
    elif kw in ("tasks", "task", "t"):
        import tasks
        sub = args[1].lower() if len(args) >= 2 else ""
        if sub in ("new", "add", "n"):
            tasks.new()
        elif sub in ("done", "d"):
            if len(args) >= 3:
                tasks.done(args[2])
            else:
                print("Usage: notes tasks done <id>")
        else:
            tasks.show()
    elif kw in ("-h", "--help", "help"):
        help_text()
    else:
        write_note(" ".join(args))  # quick note

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
    except BrokenPipeError:
        # happens when piping output (e.g. | head); not a real error
        try:
            sys.stdout.close()
        except Exception:
            pass
