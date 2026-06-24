
GUIA RAPIDA DE GIT / GitHub  ·  Technical Arts MTY

  PRIMERA VEZ (clonar el repo)
    gh repo clone Technical-Arts-MTY/notas      clonar con GitHub CLI
    cd notas                                    entrar a la carpeta
    gh auth login                               iniciar sesion (si lo pide)

  EL CICLO DE TODOS LOS DIAS
    git pull                                    traer lo ultimo antes de trabajar
    ...trabajas...
    git status                                  ver que cambio
    git add .                                   marcar todos los cambios
    git commit -m "que hice"                    guardar un punto con mensaje
    git push                                    subirlo a GitHub

  EDITAR EL README (o cualquier archivo)
    1. abre README.md y editalo
    2. git add README.md
    3. git commit -m "actualizo README"
    4. git push

  REVISAR
    git log --oneline                           historial corto
    git diff                                     ver cambios sin commitear

  RAMAS (para cambios grandes sin romper lo demas)
    git switch -c mi-rama                        crear y cambiar a una rama
    git switch main                             volver a la rama principal
    git merge mi-rama                            fusionar a donde estes parado

  SI EL PUSH ES RECHAZADO (alguien subio antes)
    git pull                                     traer y fusionar lo de el/ella
    (resuelve conflictos si los hay, luego)
    git add .  &&  git commit  &&  git push

  CREAR UN REPO NUEVO
    gh repo create Technical-Arts-MTY/NOMBRE --private --clone

  Atajo de este capitulo: en vez de los 4 pasos de arriba, usa
    notas "lo que hice"      <- guarda en la bitacora y hace push solo
