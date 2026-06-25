#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tasks — task board for the chapter (part of `notes`).

Usage:
    tasks                  show the task board (pending tasks by due date)
    tasks new              add a task (interactive)
    tasks done <id>        mark a task as finished
    tasks --help

The 'assignee' column of tasks.csv can be:
    - a GitHub username (e.g. Aaron-Cuevas)
    - or a role with the prefix role:  (e.g. role:Dir) -> resolved to whoever
      holds that role in team.csv.

The GitHub Action (.github/workflows/tasks.yml) reads these same files and sends
reminders mentioning the person based on the due date and the role.
"""

import os
import sys
import csv
from datetime import datetime, timedelta

# Reuse color, git and publish from notes.py (same folder)
try:
    import notes as N
    CYAN, GREEN, DIM, BOLD, RESET = N.CYAN, N.GREEN, N.DIM, N.BOLD, N.RESET
    repo_root, publish = N.repo_root, N.publish
except Exception:  # minimal fallback if run standalone
    CYAN = GREEN = DIM = BOLD = RESET = ""
    def repo_root():
        return os.getcwd()
    def publish(paths, message):
        print("(not published: notes.py not found)")
        return False

LEAD_DAYS = 3          # how many days ahead counts as "upcoming"
FIELDS = ["id", "task", "assignee", "due", "status"]

# --------------------------------------------------------------------------- #
#  Data loading
# --------------------------------------------------------------------------- #

def _path(name):
    return os.path.join(repo_root() or ".", name)

def load_team():
    """Returns (by_github, by_role). by_github[user]=(name, role)."""
    by_github, by_role = {}, {}
    path = _path("team.csv")
    if not os.path.exists(path):
        return by_github, by_role
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gh = (row.get("github") or "").strip()
            name = (row.get("name") or "").strip()
            role = (row.get("role") or "").strip()
            if gh:
                by_github[gh] = (name, role)
            if role:
                by_role[role] = gh  # last holder of that role
    return by_github, by_role

def load_tasks():
    path = _path("tasks.csv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [row for row in csv.DictReader(f)]

def save_tasks(rows):
    path = _path("tasks.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in FIELDS})

def resolve(assignee, by_github, by_role):
    """Returns (github_or_empty, readable_label, role)."""
    assignee = (assignee or "").strip()
    if assignee.lower().startswith("role:"):
        role = assignee[5:]
        gh = by_role.get(role, "")
        name = by_github.get(gh, ("", ""))[0]
        label = name or f"(role {role} unassigned)"
        return gh, label, role
    gh = assignee
    name, role = by_github.get(gh, ("", ""))
    return gh, (name or gh or "—"), role

# --------------------------------------------------------------------------- #
#  Task board
# --------------------------------------------------------------------------- #

def _due_state(due_str):
    """Returns (marker, color, days_text) based on the due date."""
    try:
        d = datetime.strptime(due_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return "·", DIM, "date?"
    days = (d - datetime.now().date()).days
    if days < 0:
        return "⚠", "\033[31m" if RESET else "", f"overdue (-{abs(days)}d)"
    if days == 0:
        return "●", "\033[33m" if RESET else "", "TODAY"
    if days <= LEAD_DAYS:
        return "○", CYAN, f"in {days}d"
    return "·", DIM, f"in {days}d"

def show():
    by_github, by_role = load_team()
    rows = load_tasks()
    pend = [x for x in rows if (x.get("status", "").strip().lower() != "done")]
    done_n = len(rows) - len(pend)

    def key(x):
        try:
            return datetime.strptime(x["due"].strip(), "%Y-%m-%d").date()
        except Exception:
            return datetime.max.date()
    pend.sort(key=key)

    width = 70
    print()
    print(f"{CYAN}┌{'─'*(width-2)}┐{RESET}")
    title = " TASK BOARD "
    print(f"{CYAN}│{RESET}{BOLD}{title.center(width-2)}{RESET}{CYAN}│{RESET}")
    print(f"{CYAN}├{'─'*(width-2)}┤{RESET}")
    if not pend:
        empty = "No pending tasks. All caught up!"
        print(f"{CYAN}│{RESET}{DIM}{empty.center(width-2)}{RESET}{CYAN}│{RESET}")
    else:
        for x in pend:
            marc, color, days = _due_state(x.get("due", ""))
            gh, label, role = resolve(x.get("assignee", ""), by_github, by_role)
            role_txt = f" [{role}]" if role else ""
            id_txt = f"#{x.get('id','?')}"
            line1 = f" {color}{marc}{RESET} {id_txt:<4} {x.get('task','')[:width-9]}"
            line2 = (f"     {DIM}{x.get('due','')}  ·  {color}{days}{RESET}{DIM}"
                     f"  ·  {label}{role_txt}{RESET}")
            print(f"{CYAN}│{RESET}{line1}")
            print(f"{CYAN}│{RESET}{line2}")
    print(f"{CYAN}└{'─'*(width-2)}┘{RESET}")
    legend = f"{DIM}⚠ overdue   ● today   ○ upcoming (≤{LEAD_DAYS}d)   · later"
    if done_n:
        legend += f"   ·   {done_n} done"
    print("  " + legend + RESET)
    print(f"  {DIM}Add: tasks new   ·   Finish: tasks done <id>{RESET}\n")

# --------------------------------------------------------------------------- #
#  Add and close tasks
# --------------------------------------------------------------------------- #

def _parse_due(text):
    """Accepts YYYY-MM-DD, 'today', or '+Nd' (N days from today)."""
    text = text.strip().lower()
    if text in ("today",):
        return datetime.now().date().isoformat()
    if text.startswith("+") and text.endswith("d"):
        try:
            n = int(text[1:-1])
            return (datetime.now().date() + timedelta(days=n)).isoformat()
        except ValueError:
            pass
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None

def new():
    by_github, by_role = load_team()
    print(f"\n{BOLD}New task{RESET}\n")
    task = input("  Task: ").strip()
    if not task:
        print(f"{DIM}No task, cancelled.{RESET}")
        return

    print(f"\n  {DIM}Assign to a role or a person:{RESET}")
    roles = sorted(by_role.keys())
    for i, r in enumerate(roles, 1):
        gh = by_role.get(r, "")
        name = by_github.get(gh, ("", ""))[0] or gh or "(open)"
        print(f"    [{i}] role:{r}  ({name})")
    print(f"    [u] type a GitHub username directly")
    sel = input("  > ").strip()
    if sel.lower() == "u":
        assignee = input("  GitHub username: ").strip()
    else:
        try:
            assignee = "role:" + roles[int(sel) - 1]
        except (ValueError, IndexError):
            print(f"{DIM}Invalid option.{RESET}")
            return

    raw = input("  Due date (YYYY-MM-DD, 'today' or '+7d'): ").strip()
    due = _parse_due(raw)
    if not due:
        print(f"{DIM}Invalid date.{RESET}")
        return

    rows = load_tasks()
    ids = [int(x["id"]) for x in rows if x.get("id", "").isdigit()]
    new_id = (max(ids) + 1) if ids else 1
    rows.append({"id": str(new_id), "task": task, "assignee": assignee,
                 "due": due, "status": "pending"})
    save_tasks(rows)
    print(f"\n{GREEN}Task #{new_id} added for {due}.{RESET}")
    publish([_path("tasks.csv")], f"task #{new_id}: {task[:40]}")

def done(id_str):
    rows = load_tasks()
    found = False
    for x in rows:
        if x.get("id") == str(id_str):
            x["status"] = "done"
            found = True
            break
    if not found:
        print(f"{DIM}Task #{id_str} does not exist.{RESET}")
        return
    save_tasks(rows)
    print(f"{GREEN}Task #{id_str} marked done ✓{RESET}")
    publish([_path("tasks.csv")], f"task #{id_str} done")

# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #

def main():
    args = sys.argv[1:]
    if not args:
        show()
        return
    kw = args[0].lower()
    if kw in ("new", "add", "n"):
        new()
    elif kw in ("done", "d"):
        if len(args) >= 2:
            done(args[1])
        else:
            print("Usage: tasks done <id>")
    elif kw in ("-h", "--help", "help"):
        print(__doc__)
    else:
        show()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
