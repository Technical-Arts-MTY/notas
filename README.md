# Technical Arts MTY · `notes`

Chapter logbook and documentation, editable from the terminal on any member's
computer. One tool: `notes`. The idea is to be fast — **you write and it
publishes on its own**.

---

## Active projects

| Project | Folder | Progress |
|---|---|---|
| **DT-HRES** | `projects/DT-HRES/` | `PROGRESS.md` |
| **Michelson Interferometer** | `projects/Michelson_Interferometer/` | `PROGRESS.md` |

Quick status in the terminal:

```
notes projects
```

---

## Quick start

```bash
gh repo clone Technical-Arts-MTY/notas     # clone (first time only)
cd notas
python notes.py                            # open the interface
```

Sign your notes with your name (once per computer):

```
Windows :  set TA_AUTHOR=German
Unix    :  export TA_AUTHOR=German
```

To type just `notes` (without `python`): inside the folder `notes` already works
(Windows, via `notes.bat`) or `./notes` (Mac/Linux). To use it from anywhere, add
this folder to your `PATH`.

---

## Everyday flow

**A quick note, published instantly:**

```bash
notes "fixed the Unity display bug, TMC2209 sourcing still pending"
```

**Or via menu:** `notes` → `[1] Write note` → type → Enter. It does
`pull` + `commit` + `push` for you.

---

## End of session → wiki

When you finish working (e.g. on the interferometer), document the session and
push it to the wiki, already in physics standard:

```bash
notes session
```

It asks for project, participants, what was done, measurements and pending items;
builds a well-structured page and pushes it to the repo **wiki**.

> The first time, open the wiki once on GitHub (**Wiki → Create the first page**,
> save). After that `notes session` writes on its own.

---

## Citations (physics standard)

```bash
notes cite
```

- **Measurement:** logs quantity, value ± uncertainty, **SI unit**, instrument,
  **calibration state**, conditions and method. Stored in
  `projects/<project>/measurements.md`.
- **Reference:** generates a **BibTeX** entry for your LaTeX reports and adds it
  to `references.bib`.

---

## Tasks and automatic reminders

The task board lives inside the `notes` menu as **`[6] Tasks`**, and also as
quick subcommands:

```bash
notes tasks            # show the task board
notes tasks new        # add a task (to a role or a person)
notes tasks done 3     # mark task #3 as finished
```

(There is also the standalone `tasks` command, equivalent.)

Tasks live in `tasks.csv` and the team in `team.csv`. In `assignee` you put a
GitHub username (`Aaron-Cuevas`) or a **role** (`role:Dir`), which resolves to
whoever holds that role.

### Reminders: GitHub mention + email

The Action `.github/workflows/tasks.yml` runs every weekday (~8 a.m. Monterrey),
checks due dates and, for what is **overdue or upcoming** (3 days by default),
notifies the assignee in two ways:

1. **Mention in an issue** (`@user`) → GitHub notification. Only needs the
   person's `github` to be set correctly in `team.csv`.
2. **Email** to the address in the `email` column of `team.csv`.

**To enable email** add these secrets in the repo
(Settings → Secrets and variables → Actions → New repository secret):

| Secret | Value (Gmail example) |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | `youremail@gmail.com` |
| `SMTP_PASS` | an **app password** (not your normal one) |
| `MAIL_FROM` | `youremail@gmail.com` |

For Gmail, create the app password at
`myaccount.google.com → Security → 2-Step Verification → App passwords`
(requires 2FA on). Paste that 16-letter key into `SMTP_PASS`. Without these
secrets, email is skipped and only the GitHub mention remains (nothing breaks).

> Fill in each member's real `github` and `email` in `team.csv`: the mention
> needs the username; the email needs the address.

Tuning: the lead time (`LEAD_DAYS`) and the schedule (`cron`) are changed inside
`.github/workflows/tasks.yml`. The cron uses UTC; `0 14 * * 1-5` ≈ 8:00 a.m.
Monterrey, Monday to Friday.

---

## Structure

```
notas/
├── notes.py                 # the tool
├── notes.bat / notes        # launchers (Windows / Unix)
├── tasks.py                 # task board
├── tasks.bat / tasks        # launchers
├── team.csv · tasks.csv     # team (roles, emails) and tasks
├── README.md
├── projects/
│   ├── DT-HRES/             PROGRESS.md · measurements.md
│   └── Michelson_Interferometer/   PROGRESS.md · measurements.md
├── log/                    # daily notes (YYYY-MM.md), filled on their own
├── guides/github.md        # git/GitHub cheat sheet
├── assets/
│   ├── logos/              # put the chapter .png files here
│   └── templates/          # session-template.md · measurement-template.md
└── .github/                # automation (reminders)
    ├── workflows/tasks.yml
    └── scripts/notify.py
```

---

## Roster

Alfred RS · Aaron Dir · German GH · Edgar Mth · — · — · —
