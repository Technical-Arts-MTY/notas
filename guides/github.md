
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
