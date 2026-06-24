#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notas — Technical Arts MTY · student chapter notes

Herramienta de terminal del capítulo. Multiplataforma (Windows/macOS/Linux),
solo necesita Python 3 y git. Pensada para ser rapida: escribe y se publica.

Uso rapido:
    notas                       interfaz interactiva (banner + menu)
    notas "lo que hice hoy"     guarda una nota y la publica al instante
    notas proyectos             estado de los proyectos activos
    notas github                guia de comandos comunes de git/GitHub
    notas citar                 registrar una medicion (estandar de fisica) o una referencia
    notas sesion                cerrar sesion de trabajo y subirla al wiki
    notas --help                ayuda

Tip: define tu nombre para que tus notas queden firmadas:
    Windows :  set TA_AUTOR=German
    Unix    :  export TA_AUTOR=German
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Configuracion del capitulo
# --------------------------------------------------------------------------- #

ROSTER = ["Alfred RS", "Aaron Dir", "German GH", "Edgar Mth", "—", "—", "—"]

PROYECTOS = {
    "DT-HRES": "proyectos/DT-HRES",
    "Michelson Interferometer": "proyectos/Michelson_Interferometer",
}

ANCHO = 64  # ancho de la interfaz

# --------------------------------------------------------------------------- #
#  Color / terminal
# --------------------------------------------------------------------------- #

def _habilitar_ansi():
    """Activa codigos ANSI en consolas de Windows."""
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass

_habilitar_ansi()

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
def _c(code):  # devuelve el codigo solo si hay color
    return code if _COLOR else ""

CYAN  = _c("\033[36m")
GREEN = _c("\033[32m")
DIM   = _c("\033[2m")
BOLD  = _c("\033[1m")
RESET = _c("\033[0m")

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def _escribir(s):
    sys.stdout.write(s)
    sys.stdout.flush()

# --------------------------------------------------------------------------- #
#  Helpers de git
# --------------------------------------------------------------------------- #

def run(cmd, cwd=None):
    """Ejecuta un comando y devuelve (codigo, stdout, stderr)."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"comando no encontrado: {cmd[0]}"

def raiz_repo():
    """Ruta raiz del repo 'notas' si estamos dentro, si no None."""
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"])
    return out.strip() if code == 0 else None

def autor():
    return (os.environ.get("TA_AUTOR")
            or os.environ.get("USERNAME")
            or os.environ.get("USER")
            or "anonimo")

def publicar(rutas, mensaje):
    """add + commit + push. Si el push falla, la nota igual queda guardada."""
    root = raiz_repo()
    if not root:
        print(f"{DIM}No estas dentro del repo 'notas'.{RESET}")
        print("  git clone https://github.com/Technical-Arts-MTY/notas.git")
        print("  cd notas")
        return False
    run(["git", "pull", "--quiet", "--no-rebase"], cwd=root)  # mejor esfuerzo
    run(["git", "add"] + rutas, cwd=root)
    code, out, err = run(["git", "commit", "-m", mensaje], cwd=root)
    if code != 0 and "nothing to commit" in (out + err):
        print(f"{DIM}Nada nuevo que publicar.{RESET}")
        return True
    code, out, err = run(["git", "push"], cwd=root)
    if code != 0:
        print(f"{DIM}Guardado y commiteado localmente, pero el push fallo:{RESET}")
        print("  " + (err or out).strip().splitlines()[-1] if (err or out).strip() else "")
        print(f"  Revisa tu sesion:  {BOLD}gh auth login{RESET}  (o haz git push a mano)")
        return False
    print(f"{GREEN}Publicado \u2713{RESET}")
    return True

# --------------------------------------------------------------------------- #
#  Arte ASCII: bailarines y diagonal animada
# --------------------------------------------------------------------------- #

# Cinco humanitos. Dos cuadros que se alternan -> parecen bailar.
_BAILE_A = [
    " \\o/    o     \\o/    o     \\o/ ",
    "  |    /|\\     |    /|\\     |  ",
    " / \\   / \\    / \\   / \\    / \\ ",
]
_BAILE_B = [
    "  o    \\o/     o    \\o/     o  ",
    " /|\\    |     /|\\    |     /|\\ ",
    " / \\   / \\    / \\   / \\    / \\ ",
]
_W = max(len(l) for l in _BAILE_A + _BAILE_B)

def _cuadro_baile(i):
    return [l.ljust(_W) for l in (_BAILE_A if i % 2 == 0 else _BAILE_B)]

def _centrar(linea, ancho=ANCHO):
    return linea.center(ancho)

# --------------------------------------------------------------------------- #
#  Interfaz
# --------------------------------------------------------------------------- #

def _barra_roster():
    nombres = " · ".join(ROSTER)
    return f"{DIM}{_centrar(nombres)}{RESET}"

def _bailarines_estatico(frame=0):
    return "\n".join(f"{CYAN}{_centrar(l)}{RESET}" for l in _cuadro_baile(frame))

def intro():
    """Animacion de arranque: primero 'notas', luego Technical Arts con la
    diagonal animada / | \\ , y los bailarines moviendose."""
    limpiar()
    print()
    print(_barra_roster())
    print()
    # 1) primero dice notas
    titulo = "n o t a s"
    _escribir("\n" + " " * ((ANCHO - len(titulo)) // 2))
    for ch in titulo:
        _escribir(BOLD + ch + RESET)
        time.sleep(0.045)
    print("\n")
    # 2) Technical Arts con la diagonal girando al lado
    spins = ["/", "|", "\\"]
    izq = "Technical Arts "
    der = " student chapter notes"
    base = (ANCHO - (len(izq) + 1 + len(der))) // 2
    for i in range(12):
        linea = " " * base + izq + CYAN + spins[i % 3] + RESET + DIM + der + RESET
        _escribir("\r" + linea)
        time.sleep(0.085)
    print("\n")
    # 3) los humanitos bailan unos cuadros
    for l in _cuadro_baile(0):
        print(f"{CYAN}{_centrar(l)}{RESET}")
    for i in range(1, 7):
        _escribir("\033[3A")  # subir 3 lineas
        for l in _cuadro_baile(i):
            _escribir("\r\033[K" + f"{CYAN}{_centrar(l)}{RESET}" + "\n")
        time.sleep(0.16)
    time.sleep(0.2)

def menu_estatico():
    limpiar()
    raya = "─" * ANCHO
    print()
    print(_barra_roster())
    print(f"{DIM}{raya}{RESET}")
    print()
    print(f"{BOLD}{_centrar('n o t a s')}{RESET}")
    print(f"{_centrar('Technical Arts ' + CYAN + '/' + RESET + DIM + ' student chapter notes' + RESET)}")
    print()
    opciones = [
        ("1", "Escribir nota", "4", "Citar (estandar fisica)"),
        ("2", "Proyectos activos", "5", "Cerrar sesion \u2192 wiki"),
        ("3", "Guia de GitHub", "q", "Salir"),
    ]
    for a, ta, b, tb in opciones:
        izq = f"  {CYAN}[{a}]{RESET} {ta}"
        der = f"{CYAN}[{b}]{RESET} {tb}"
        print(f"{izq:<38}{der}")
    print()
    print(_bailarines_estatico(0))
    print()

def pausa():
    try:
        input(f"\n{DIM}  Enter para volver al menu...{RESET}")
    except EOFError:
        pass

# --------------------------------------------------------------------------- #
#  Accion: escribir nota
# --------------------------------------------------------------------------- #

def escribir_nota(texto=None):
    if texto is None:
        print(f"\n{BOLD}Escribe tu nota.{RESET} {DIM}(linea vacia para terminar){RESET}\n")
        lineas = []
        while True:
            try:
                l = input("  ")
            except EOFError:
                break
            if l == "" and lineas:
                break
            if l == "" and not lineas:
                continue
            lineas.append(l)
        texto = "\n".join(lineas).strip()
    if not texto:
        print(f"{DIM}Sin contenido, no se publica nada.{RESET}")
        return
    root = raiz_repo() or "."
    carpeta = os.path.join(root, "bitacora")
    os.makedirs(carpeta, exist_ok=True)
    ahora = datetime.now()
    archivo = os.path.join(carpeta, ahora.strftime("%Y-%m") + ".md")
    nuevo = not os.path.exists(archivo)
    with open(archivo, "a", encoding="utf-8") as f:
        if nuevo:
            f.write(f"# Bitacora {ahora.strftime('%Y-%m')}\n")
        f.write(f"\n### {ahora.strftime('%Y-%m-%d %H:%M')} · {autor()}\n{texto}\n")
    resumen = " ".join(texto.split())[:50]
    publicar([archivo], f"nota: {resumen}")

# --------------------------------------------------------------------------- #
#  Accion: ver proyectos
# --------------------------------------------------------------------------- #

def ver_proyectos():
    root = raiz_repo() or "."
    print()
    for nombre, ruta in PROYECTOS.items():
        print(f"{BOLD}{CYAN}▌ {nombre}{RESET}")
        p = os.path.join(root, ruta, "PROGRESO.md")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                lineas = [l.rstrip() for l in f.readlines()]
            mostradas = 0
            for l in lineas:
                if l.startswith("# "):
                    continue
                print("  " + l)
                mostradas += 1
                if mostradas >= 22:
                    print(f"  {DIM}... (abre {ruta}/PROGRESO.md para el detalle){RESET}")
                    break
        else:
            print(f"  {DIM}(aun sin PROGRESO.md){RESET}")
        print()

# --------------------------------------------------------------------------- #
#  Accion: guia de GitHub
# --------------------------------------------------------------------------- #

GUIA = """
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
"""

def guia_github():
    root = raiz_repo() or "."
    p = os.path.join(root, "guias", "github.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            print("\n" + f.read())
    else:
        print(GUIA)

# --------------------------------------------------------------------------- #
#  Accion: citar (estandar de fisica) / referencia
# --------------------------------------------------------------------------- #

def _preg(etiqueta, default=""):
    extra = f" {DIM}[{default}]{RESET}" if default else ""
    try:
        r = input(f"  {etiqueta}{extra}: ").strip()
    except EOFError:
        r = ""
    return r or default

def citar():
    print(f"\n{BOLD}Registrar{RESET}  [{CYAN}m{RESET}] medicion (estandar de fisica)   "
          f"[{CYAN}r{RESET}] referencia bibliografica")
    try:
        tipo = input("  > ").strip().lower()
    except EOFError:
        tipo = "m"

    if tipo.startswith("r"):
        _citar_referencia()
    else:
        _citar_medicion()

def _citar_medicion():
    print(f"\n{DIM}Documenta la medicion con unidades SI, incertidumbre y calibracion.{RESET}\n")
    magnitud = _preg("Magnitud (p.ej. longitud de onda)")
    simbolo  = _preg("Simbolo", "x")
    valor    = _preg("Valor")
    incert   = _preg("Incertidumbre (±)", "—")
    unidad   = _preg("Unidad SI (m, s, V, nm, ...)")
    instr    = _preg("Instrumento")
    calib    = _preg("Calibracion (si/no)", "no")
    calref   = _preg("  Referencia/fecha de calibracion", "—") if calib.lower().startswith("s") else "—"
    cond     = _preg("Condiciones (T, humedad, montaje...)", "—")
    metodo   = _preg("Metodo", "—")

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    bloque = (
        f"\n### Medicion: {magnitud} ({simbolo})\n"
        f"- **Valor:** {valor} ± {incert} {unidad}\n"
        f"- **Instrumento:** {instr}\n"
        f"- **Calibracion:** {calib} — {calref}\n"
        f"- **Condiciones:** {cond}\n"
        f"- **Metodo:** {metodo}\n"
        f"- **Registrado:** {ahora} · {autor()}\n"
    )
    print(f"\n{GREEN}Bloque generado:{RESET}")
    print(bloque)
    _guardar_en_proyecto(bloque, "mediciones.md", f"medicion: {magnitud} ({simbolo})")

def _citar_referencia():
    print(f"\n{DIM}Genera una entrada BibTeX para tus reportes en LaTeX.{RESET}\n")
    tipo   = _preg("Tipo (article/book/misc)", "article")
    clave  = _preg("Clave de cita (p.ej. born1999principles)")
    autorf = _preg("Autor(es)")
    titulo = _preg("Titulo")
    anio   = _preg("Año")
    fuente = _preg("Revista / editorial", "—")

    bib = (
        f"@{tipo}{{{clave or 'ref'},\n"
        f"  author  = {{{autorf}}},\n"
        f"  title   = {{{titulo}}},\n"
        f"  journal = {{{fuente}}},\n"
        f"  year    = {{{anio}}}\n"
        f"}}\n"
    )
    print(f"\n{GREEN}Entrada BibTeX:{RESET}")
    print(bib)
    root = raiz_repo() or "."
    archivo = os.path.join(root, "referencias.bib")
    with open(archivo, "a", encoding="utf-8") as f:
        f.write("\n" + bib)
    print(f"{DIM}Agregada a referencias.bib{RESET}")
    publicar([archivo], f"ref: {clave or titulo[:40]}")

def _guardar_en_proyecto(bloque, archivo_dest, mensaje):
    print(f"{DIM}¿En que proyecto?{RESET}")
    proyectos = list(PROYECTOS.items())
    for i, (nombre, _) in enumerate(proyectos, 1):
        print(f"  [{i}] {nombre}")
    print("  [0] solo mostrarlo (no guardar)")
    try:
        sel = input("  > ").strip()
    except EOFError:
        sel = "0"
    if sel in ("", "0"):
        print(f"{DIM}No se guardo. Copialo de arriba si lo necesitas.{RESET}")
        return
    try:
        ruta = proyectos[int(sel) - 1][1]
    except (ValueError, IndexError):
        print(f"{DIM}Opcion invalida.{RESET}")
        return
    root = raiz_repo() or "."
    destino = os.path.join(root, ruta, archivo_dest)
    nuevo = not os.path.exists(destino)
    with open(destino, "a", encoding="utf-8") as f:
        if nuevo:
            f.write(f"# Mediciones — {proyectos[int(sel)-1][0]}\n")
        f.write(bloque)
    publicar([destino], mensaje)

# --------------------------------------------------------------------------- #
#  Accion: cerrar sesion -> wiki
# --------------------------------------------------------------------------- #

def _url_origin():
    code, out, _ = run(["git", "remote", "get-url", "origin"])
    return out.strip() if code == 0 else None

def _url_wiki(origin):
    return (origin[:-4] + ".wiki.git") if origin.endswith(".git") else origin + ".wiki.git"

def _dir_wiki(origin):
    nombre = origin.rstrip("/").split("/")[-1].replace(".git", "")
    return Path.home() / ".technical-arts" / (nombre + ".wiki")

def _asegurar_wiki(origin):
    """Clona o actualiza el repo del wiki. Devuelve (Path, ok)."""
    wdir = _dir_wiki(origin)
    wurl = _url_wiki(origin)
    if (wdir / ".git").exists():
        run(["git", "pull", "--quiet", "--no-rebase"], cwd=str(wdir))
        return wdir, True
    wdir.parent.mkdir(parents=True, exist_ok=True)
    code, out, err = run(["git", "clone", wurl, str(wdir)])
    if code != 0:
        return None, False
    return wdir, True

def _pagina_wiki(nombre_proyecto):
    return nombre_proyecto.replace(" ", "-") + ".md"

def cerrar_sesion():
    root = raiz_repo()
    if not root:
        print(f"{DIM}Entra primero al repo: cd notas{RESET}")
        return
    origin = _url_origin()
    if not origin:
        print(f"{DIM}Este repo no tiene 'origin' configurado.{RESET}")
        return

    print(f"\n{BOLD}Cerrar sesion de trabajo{RESET}  →  se documenta y sube al wiki\n")
    proyectos = list(PROYECTOS.items())
    for i, (nombre, _) in enumerate(proyectos, 1):
        print(f"  [{i}] {nombre}")
    try:
        sel = input("  Proyecto > ").strip()
        proyecto = proyectos[int(sel) - 1][0]
    except (EOFError, ValueError, IndexError):
        print(f"{DIM}Opcion invalida.{RESET}")
        return

    participantes = _preg("Participantes (separados por coma)", autor())
    print(f"\n{DIM}Resumen de lo realizado (linea vacia para terminar):{RESET}")
    realizado = []
    while True:
        try:
            l = input("  - ")
        except EOFError:
            break
        if l == "":
            break
        realizado.append(f"- {l}")
    mediciones = _preg("Mediciones / datos clave (o referencia)", "—")
    pendientes = _preg("Pendientes / siguiente paso", "—")

    fecha = datetime.now().strftime("%Y-%m-%d")
    seccion = (
        f"\n---\n\n## Sesion {fecha}\n\n"
        f"**Participantes:** {participantes}\n\n"
        f"**Realizado:**\n" + ("\n".join(realizado) if realizado else "- —") + "\n\n"
        f"**Mediciones / datos:** {mediciones}\n\n"
        f"**Pendientes:** {pendientes}\n\n"
        f"*Estandar: unidades SI · valor ± incertidumbre · estado de calibracion indicado.*\n"
    )

    print(f"\n{DIM}Conectando con el wiki...{RESET}")
    wdir, ok = _asegurar_wiki(origin)
    if not ok:
        print(f"{DIM}El wiki todavia no existe.{RESET}")
        print(f"  Abrelo UNA vez en GitHub:  {origin.replace('.git','')}/wiki")
        print(f"  (boton 'Create the first page', guarda) y vuelve a correr {BOLD}notas sesion{RESET}.")
        return

    pagina = wdir / _pagina_wiki(proyecto)
    nuevo = not pagina.exists()
    with open(pagina, "a", encoding="utf-8") as f:
        if nuevo:
            f.write(f"# {proyecto} — Bitacora de sesiones\n")
        f.write(seccion)

    run(["git", "add", "."], cwd=str(wdir))
    run(["git", "commit", "-m", f"sesion {proyecto} {fecha}"], cwd=str(wdir))
    code, out, err = run(["git", "push"], cwd=str(wdir))
    if code == 0:
        print(f"{GREEN}Sesion publicada en el wiki \u2713{RESET}")
        print(f"  {origin.replace('.git','')}/wiki/{_pagina_wiki(proyecto)[:-3]}")
    else:
        print(f"{DIM}Se escribio localmente pero el push al wiki fallo:{RESET}")
        print("  " + (err or out).strip().splitlines()[-1] if (err or out).strip() else "")

# --------------------------------------------------------------------------- #
#  Menu interactivo y main
# --------------------------------------------------------------------------- #

def menu():
    intro()
    while True:
        menu_estatico()
        try:
            op = input(f"  {CYAN}>{RESET} ").strip().lower()
        except EOFError:
            print()
            break
        if op in ("1", "n", "nota"):
            escribir_nota(); pausa()
        elif op in ("2", "p", "proyectos"):
            ver_proyectos(); pausa()
        elif op in ("3", "g", "github"):
            guia_github(); pausa()
        elif op in ("4", "c", "citar"):
            citar(); pausa()
        elif op in ("5", "s", "sesion", "sesión"):
            cerrar_sesion(); pausa()
        elif op in ("q", "salir", "exit", "quit"):
            print(f"  {DIM}Hasta luego.{RESET}")
            break
        else:
            print(f"  {DIM}Opcion no valida.{RESET}")
            time.sleep(0.6)

def ayuda():
    print(__doc__)

def main():
    args = sys.argv[1:]
    if not args:
        menu()
        return
    kw = args[0].lower()
    if kw in ("proyectos", "p"):
        ver_proyectos()
    elif kw in ("github", "g", "guia", "guía"):
        guia_github()
    elif kw in ("citar", "c", "cita"):
        citar()
    elif kw in ("sesion", "sesión", "s"):
        cerrar_sesion()
    elif kw in ("-h", "--help", "help", "ayuda"):
        ayuda()
    else:
        escribir_nota(" ".join(args))  # nota rapida

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
    except BrokenPipeError:
        # ocurre al canalizar la salida (p.ej. | head); no es un error real
        try:
            sys.stdout.close()
        except Exception:
            pass
