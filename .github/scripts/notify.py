#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notify.py — run by the GitHub Action.

Reads tasks.csv + team.csv, finds tasks that are OVERDUE or due within LEAD_DAYS,
and notifies the assignee in two ways:
  1) comments on an issue mentioning (@user)  -> GitHub notification
  2) sends them an EMAIL with their tasks      -> if SMTP is configured

Email uses standard SMTP (smtplib). It needs these repo secrets:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_FROM
If they are missing, email is skipped and only the GitHub notice remains (no
crash). The 'email' column of team.csv defines who gets written to.
"""

import os
import csv
import sys
import ssl
import smtplib
import subprocess
from email.message import EmailMessage
from datetime import datetime

LEAD_DAYS = int(os.environ.get("LEAD_DAYS", "3"))
ISSUE_TITLE = "📋 Tasks — reminders"
LABEL = "tasks"
TODAY = datetime.now().date()
DATE = TODAY.isoformat()


# --------------------------------------------------------------------------- #
#  Data
# --------------------------------------------------------------------------- #

def load_team():
    """by_github[user] = (name, role, email) ; by_role[role] = user."""
    by_github, by_role = {}, {}
    if not os.path.exists("team.csv"):
        return by_github, by_role
    with open("team.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ghu = (row.get("github") or "").strip()
            name = (row.get("name") or "").strip()
            role = (row.get("role") or "").strip()
            email = (row.get("email") or "").strip()
            if ghu:
                by_github[ghu] = (name, role, email)
            if role:
                by_role[role] = ghu
    return by_github, by_role


def resolve(assignee, by_github, by_role):
    assignee = (assignee or "").strip()
    if assignee.lower().startswith("role:"):
        role = assignee[5:]
        ghu = by_role.get(role, "")
        name, _, email = by_github.get(ghu, ("", "", ""))
        return ghu, (name or f"(role {role} unassigned)"), role, email
    ghu = assignee
    name, role, email = by_github.get(ghu, ("", "", ""))
    return ghu, (name or ghu or "—"), role, email


def collect():
    """List of people with relevant tasks:
       [{github, name, role, email, items_md, items_txt}, ...]"""
    if not os.path.exists("tasks.csv"):
        return []
    by_github, by_role = load_team()
    people = {}  # key -> dict
    with open("tasks.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip().lower() == "done":
                continue
            try:
                due = datetime.strptime(row["due"].strip(), "%Y-%m-%d").date()
            except (ValueError, KeyError):
                continue
            days = (due - TODAY).days
            if days > LEAD_DAYS:
                continue
            ghu, name, role, email = resolve(row.get("assignee", ""), by_github, by_role)
            if days < 0:
                md = f"⚠ **Overdue** ({abs(days)}d ago, was due {row['due']})"
                txt = f"[OVERDUE {abs(days)}d ago] "
            elif days == 0:
                md = "● **Today**"
                txt = "[TODAY] "
            else:
                md = f"○ due in {days}d ({row['due']})"
                txt = f"[in {days}d] "
            task = row.get("task", "")
            idd = row.get("id", "?")
            key = ghu or name
            p = people.setdefault(key, {
                "github": ghu, "name": name, "role": role,
                "email": email, "items_md": [], "items_txt": [],
            })
            p["items_md"].append(f"- {md}: {task}  ·  `#{idd}`")
            p["items_txt"].append(f"  {txt}{task}  (#{idd}, due {row['due']})")
    return list(people.values())


# --------------------------------------------------------------------------- #
#  GitHub notice (issue + mention)
# --------------------------------------------------------------------------- #

def gh(*args, stdin=None):
    try:
        p = subprocess.run(["gh", *args], capture_output=True, text=True, input=stdin)
    except FileNotFoundError:
        sys.stderr.write("gh (GitHub CLI) not available; skipping GitHub notice.\n")
        return 127, ""
    if p.returncode != 0:
        sys.stderr.write(p.stderr)
    return p.returncode, p.stdout.strip()


def issue_body(people):
    parts = [f"## ⏰ Task reminder — {DATE}\n"]
    for p in people:
        if p["github"]:
            head = f"\n**@{p['github']}** — {p['name']}" + (f" ({p['role']})" if p['role'] else "")
        else:
            head = f"\n**{p['name']}**"
        parts.append(head)
        parts.extend(p["items_md"])
    parts.append(f"\n\n_Mark done with `tasks done <id>`. Reminder set to {LEAD_DAYS} days._")
    return "\n".join(parts)


def notify_github(people):
    gh("label", "create", LABEL, "--color", "FFA500",
       "--description", "Task reminders")  # silent if it already exists
    code, num = gh("issue", "list", "--state", "open", "--label", LABEL,
                   "--json", "number", "--jq", ".[0].number // empty")
    body = issue_body(people)
    if num:
        gh("issue", "comment", num, "--body-file", "-", stdin=body)
        print(f"Reminder commented on issue #{num}.")
    else:
        gh("issue", "create", "--title", ISSUE_TITLE, "--label", LABEL,
           "--body-file", "-", stdin=body)
        print("Reminder issue created.")


# --------------------------------------------------------------------------- #
#  Email notice (SMTP)
# --------------------------------------------------------------------------- #

def email_body(p):
    greeting = f"Hi {p['name']}," if p['name'] and p['name'] != "—" else "Hi,"
    body = (
        f"{greeting}\n\n"
        f"You have pending Technical Arts MTY tasks:\n\n"
        + "\n".join(p["items_txt"])
        + "\n\n"
        "When you finish one, mark it with:  tasks done <id>\n\n"
        "— Technical Arts MTY automated reminder\n"
    )
    return body


def notify_email(people):
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    pwd = os.environ.get("SMTP_PASS")
    port = int(os.environ.get("SMTP_PORT", "587"))
    sender = os.environ.get("MAIL_FROM") or user

    if not (host and user and pwd):
        print("SMTP not configured (missing secrets); skipping email.")
        return
    recipients = [p for p in people if p.get("email")]
    if not recipients:
        print("Nobody has 'email' in team.csv; skipping email.")
        return

    context = ssl.create_default_context()
    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, context=context)
        else:
            server = smtplib.SMTP(host, port)
            server.starttls(context=context)
        with server:
            server.login(user, pwd)
            for p in recipients:
                msg = EmailMessage()
                msg["Subject"] = f"Task reminder — {DATE}"
                msg["From"] = sender
                msg["To"] = p["email"]
                msg.set_content(email_body(p))
                server.send_message(msg)
                print(f"Email sent to {p['email']}")
    except Exception as e:
        print(f"Could not send email: {e}")


# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #

def main():
    people = collect()
    if not people:
        print("No overdue or upcoming tasks. Nothing to notify.")
        return
    notify_github(people)
    notify_email(people)


if __name__ == "__main__":
    main()
