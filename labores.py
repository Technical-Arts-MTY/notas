#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
labores — ventana de tareas del capitulo (parte de `notas`).

Uso:
    labores                  ver la ventana de labores (pendientes por fecha)
    labores nueva            dar de alta una labor (interactivo)
    labores hecho <id>       marcar una labor como terminada
    labores --help

La columna 'asignar' de labores.csv puede ser:
    - un usuario de GitHub (p.ej. Aaron-Cuevas)
    - o un rol con el prefijo rol:  (p.ej. rol:Dir) -> se resuelve a quien
      tenga ese rol en equipo.csv.

La GitHub Action (.github/workflows/labores.yml) lee estos mismos archivos y
manda recordatorios mencionando a la persona segun la fecha y el rol.
"""

import os
import sys
import csv
from datetime import datetime, timedelta

# Reutilizamos color, git y publicacion de notas.py (mismo folder)
try:
    import notas as N
    CYAN, GREEN, DIM, BOLD, RESET = N.CYAN, N.GREEN, N.DIM, N.BOLD, N.RESET
    raiz_repo, publicar = N.raiz_repo, N.publicar
except Exception:  # respaldo minimo si se corre suelto
    CYAN = GREEN = DIM = BOLD = RESET = ""
    def raiz_repo():
        return os.getcwd()
    def publicar(rutas, mensaje):
        print("(sin publicar: no se encontro notas.py)")
        return False

AVISO_DIAS = 3          # cuantos dias antes se considera "proxima"
CAMPOS = ["id", "tarea", "asignar", "fecha", "estado"]

# --------------------------------------------------------------------------- #
#  Carga de datos
# --------------------------------------------------------------------------- #

def _ruta(nombre):
    return os.path.join(raiz_repo() or ".", nombre)

def cargar_equipo():
    """Devuelve (por_github, por_rol). por_github[user]=(nombre, rol)."""
    por_github, por_rol = {}, {}
    ruta = _ruta("equipo.csv")
    if not os.path.exists(ruta):
        return por_github, por_rol
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            gh = (fila.get("github") or "").strip()
            nombre = (fila.get("nombre") or "").strip()
            rol = (fila.get("rol") or "").strip()
            if gh:
                por_github[gh] = (nombre, rol)
            if rol:
                por_rol[rol] = gh  # ultimo que tenga ese rol
    return por_github, por_rol

def cargar_labores():
    ruta = _ruta("labores.csv")
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding="utf-8") as f:
        return [fila for fila in csv.DictReader(f)]

def guardar_labores(filas):
    ruta = _ruta("labores.csv")
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in CAMPOS})

def resolver(asignar, por_github, por_rol):
    """Devuelve (github_o_vacio, etiqueta_legible, rol)."""
    asignar = (asignar or "").strip()
    if asignar.lower().startswith("rol:"):
        rol = asignar[4:]
        gh = por_rol.get(rol, "")
        nombre = por_github.get(gh, ("", ""))[0]
        etiqueta = nombre or f"(rol {rol} sin asignar)"
        return gh, etiqueta, rol
    gh = asignar
    nombre, rol = por_github.get(gh, ("", ""))
    return gh, (nombre or gh or "—"), rol

# --------------------------------------------------------------------------- #
#  Ventana de labores
# --------------------------------------------------------------------------- #

def _estado_fecha(fecha_str):
    """Devuelve (marcador, color, texto_dias) segun la fecha limite."""
    try:
        f = datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return "·", DIM, "fecha?"
    dias = (f - datetime.now().date()).days
    if dias < 0:
        return "⚠", "\033[31m" if RESET else "", f"vencida (-{abs(dias)}d)"
    if dias == 0:
        return "●", "\033[33m" if RESET else "", "HOY"
    if dias <= AVISO_DIAS:
        return "○", CYAN, f"en {dias}d"
    return "·", DIM, f"en {dias}d"

def ver():
    por_github, por_rol = cargar_equipo()
    filas = cargar_labores()
    pend = [x for x in filas if (x.get("estado", "").strip().lower() != "hecho")]
    hechas = len(filas) - len(pend)

    def clave(x):
        try:
            return datetime.strptime(x["fecha"].strip(), "%Y-%m-%d").date()
        except Exception:
            return datetime.max.date()
    pend.sort(key=clave)

    ancho = 70
    print()
    print(f"{CYAN}┌{'─'*(ancho-2)}┐{RESET}")
    titulo = " VENTANA DE LABORES "
    print(f"{CYAN}│{RESET}{BOLD}{titulo.center(ancho-2)}{RESET}{CYAN}│{RESET}")
    print(f"{CYAN}├{'─'*(ancho-2)}┤{RESET}")
    if not pend:
        vacio = "Sin labores pendientes. ¡Todo al día!"
        print(f"{CYAN}│{RESET}{DIM}{vacio.center(ancho-2)}{RESET}{CYAN}│{RESET}")
    else:
        for x in pend:
            marc, color, dias = _estado_fecha(x.get("fecha", ""))
            gh, etiqueta, rol = resolver(x.get("asignar", ""), por_github, por_rol)
            rol_txt = f" [{rol}]" if rol else ""
            id_txt = f"#{x.get('id','?')}"
            linea1 = f" {color}{marc}{RESET} {id_txt:<4} {x.get('tarea','')[:ancho-9]}"
            linea2 = (f"     {DIM}{x.get('fecha','')}  ·  {color}{dias}{RESET}{DIM}"
                      f"  ·  {etiqueta}{rol_txt}{RESET}")
            print(f"{CYAN}│{RESET}{linea1}")
            print(f"{CYAN}│{RESET}{linea2}")
    print(f"{CYAN}└{'─'*(ancho-2)}┘{RESET}")
    leyenda = f"{DIM}⚠ vencida   ● hoy   ○ próxima (≤{AVISO_DIAS}d)   · futura"
    if hechas:
        leyenda += f"   ·   {hechas} hecha(s)"
    print("  " + leyenda + RESET)
    print(f"  {DIM}Alta: labores nueva   ·   Terminar: labores hecho <id>{RESET}\n")

# --------------------------------------------------------------------------- #
#  Alta y cierre de labores
# --------------------------------------------------------------------------- #

def _parsear_fecha(texto):
    """Acepta AAAA-MM-DD, 'hoy', o '+Nd' (N dias a partir de hoy)."""
    texto = texto.strip().lower()
    if texto in ("hoy", "today"):
        return datetime.now().date().isoformat()
    if texto.startswith("+") and texto.endswith("d"):
        try:
            n = int(texto[1:-1])
            return (datetime.now().date() + timedelta(days=n)).isoformat()
        except ValueError:
            pass
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None

def nueva():
    por_github, por_rol = cargar_equipo()
    print(f"\n{BOLD}Nueva labor{RESET}\n")
    tarea = input("  Tarea: ").strip()
    if not tarea:
        print(f"{DIM}Sin tarea, se cancela.{RESET}")
        return

    print(f"\n  {DIM}Asignar a un rol o a una persona:{RESET}")
    roles = sorted(por_rol.keys())
    for i, r in enumerate(roles, 1):
        gh = por_rol.get(r, "")
        nombre = por_github.get(gh, ("", ""))[0] or gh or "(libre)"
        print(f"    [{i}] rol:{r}  ({nombre})")
    print(f"    [u] escribir un usuario de GitHub directo")
    sel = input("  > ").strip()
    if sel.lower() == "u":
        asignar = input("  Usuario de GitHub: ").strip()
    else:
        try:
            asignar = "rol:" + roles[int(sel) - 1]
        except (ValueError, IndexError):
            print(f"{DIM}Opción inválida.{RESET}")
            return

    cruda = input("  Fecha límite (AAAA-MM-DD, 'hoy' o '+7d'): ").strip()
    fecha = _parsear_fecha(cruda)
    if not fecha:
        print(f"{DIM}Fecha no válida.{RESET}")
        return

    filas = cargar_labores()
    ids = [int(x["id"]) for x in filas if x.get("id", "").isdigit()]
    nuevo_id = (max(ids) + 1) if ids else 1
    filas.append({"id": str(nuevo_id), "tarea": tarea, "asignar": asignar,
                  "fecha": fecha, "estado": "pendiente"})
    guardar_labores(filas)
    print(f"\n{GREEN}Labor #{nuevo_id} agregada para {fecha}.{RESET}")
    publicar([_ruta("labores.csv")], f"labor #{nuevo_id}: {tarea[:40]}")

def hecho(id_str):
    filas = cargar_labores()
    encontrada = False
    for x in filas:
        if x.get("id") == str(id_str):
            x["estado"] = "hecho"
            encontrada = True
            break
    if not encontrada:
        print(f"{DIM}No existe la labor #{id_str}.{RESET}")
        return
    guardar_labores(filas)
    print(f"{GREEN}Labor #{id_str} marcada como hecha ✓{RESET}")
    publicar([_ruta("labores.csv")], f"labor #{id_str} hecha")

# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #

def main():
    args = sys.argv[1:]
    if not args:
        ver()
        return
    kw = args[0].lower()
    if kw in ("nueva", "alta", "n", "add"):
        nueva()
    elif kw in ("hecho", "done", "h"):
        if len(args) >= 2:
            hecho(args[1])
        else:
            print("Uso: labores hecho <id>")
    elif kw in ("-h", "--help", "help", "ayuda"):
        print(__doc__)
    else:
        ver()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
