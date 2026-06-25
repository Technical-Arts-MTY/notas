#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
avisar.py — lo corre la GitHub Action.

Lee labores.csv + equipo.csv, encuentra las labores VENCIDAS o que vencen dentro
de DIAS_AVISO, y publica un recordatorio en un issue mencionando (@usuario) a la
persona responsable. La mencion en GitHub le llega como notificacion + correo.

No necesita secrets: usa el GITHUB_TOKEN que la Action ya provee (via GH_TOKEN).
"""

import os
import csv
import sys
import subprocess
from datetime import datetime

DIAS_AVISO = int(os.environ.get("DIAS_AVISO", "3"))
TITULO_ISSUE = "📋 Labores — recordatorios"
ETIQUETA = "labores"


def gh(*args, entrada=None):
    """Llama a la GitHub CLI y devuelve (codigo, stdout)."""
    p = subprocess.run(["gh", *args], capture_output=True, text=True, input=entrada)
    if p.returncode != 0:
        sys.stderr.write(p.stderr)
    return p.returncode, p.stdout.strip()


def cargar_equipo():
    por_github, por_rol = {}, {}
    if not os.path.exists("equipo.csv"):
        return por_github, por_rol
    with open("equipo.csv", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            ghu = (fila.get("github") or "").strip()
            nombre = (fila.get("nombre") or "").strip()
            rol = (fila.get("rol") or "").strip()
            if ghu:
                por_github[ghu] = (nombre, rol)
            if rol:
                por_rol[rol] = ghu
    return por_github, por_rol


def resolver(asignar, por_github, por_rol):
    asignar = (asignar or "").strip()
    if asignar.lower().startswith("rol:"):
        rol = asignar[4:]
        ghu = por_rol.get(rol, "")
        nombre = por_github.get(ghu, ("", ""))[0]
        return ghu, (nombre or f"(rol {rol} sin asignar)"), rol
    ghu = asignar
    nombre, rol = por_github.get(ghu, ("", ""))
    return ghu, (nombre or ghu or "—"), rol


def construir_digest():
    if not os.path.exists("labores.csv"):
        return None
    por_github, por_rol = cargar_equipo()
    hoy = datetime.now().date()

    # agrupa por persona: clave = usuario github (o "" si no se conoce)
    por_persona = {}
    relevantes = 0
    with open("labores.csv", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if (fila.get("estado") or "").strip().lower() == "hecho":
                continue
            try:
                f_lim = datetime.strptime(fila["fecha"].strip(), "%Y-%m-%d").date()
            except (ValueError, KeyError):
                continue
            dias = (f_lim - hoy).days
            if dias > DIAS_AVISO:      # todavia lejos: no se avisa
                continue
            relevantes += 1
            ghu, etiqueta, rol = resolver(fila.get("asignar", ""), por_github, por_rol)
            if dias < 0:
                estado = f"⚠ **Vencida** (hace {abs(dias)}d, vencía {fila['fecha']})"
            elif dias == 0:
                estado = "● **Hoy**"
            else:
                estado = f"○ vence en {dias}d ({fila['fecha']})"
            por_persona.setdefault((ghu, etiqueta, rol), []).append(
                f"- {estado}: {fila.get('tarea','')}  ·  `#{fila.get('id','?')}`"
            )

    if relevantes == 0:
        return None

    fecha = hoy.isoformat()
    partes = [f"## ⏰ Recordatorio de labores — {fecha}\n"]
    for (ghu, etiqueta, rol), items in por_persona.items():
        encabezado = f"**@{ghu}**" if ghu else f"**{etiqueta}**"
        nombre_rol = f" — {etiqueta}" + (f" ({rol})" if rol else "") if ghu else ""
        partes.append(f"\n{encabezado}{nombre_rol}")
        partes.extend(items)
    partes.append(f"\n\n_Marca terminada con `labores hecho <id>`. "
                  f"Aviso configurado a {DIAS_AVISO} días._")
    return "\n".join(partes)


def asegurar_etiqueta():
    gh("label", "create", ETIQUETA, "--color", "FFA500",
       "--description", "Recordatorios de labores")  # falla en silencio si ya existe


def numero_issue_abierto():
    code, out = gh("issue", "list", "--state", "open", "--label", ETIQUETA,
                   "--json", "number", "--jq", ".[0].number // empty")
    return out.strip() or None


def publicar_recordatorio(cuerpo):
    asegurar_etiqueta()
    num = numero_issue_abierto()
    if num:
        gh("issue", "comment", num, "--body-file", "-", entrada=cuerpo)
        print(f"Recordatorio comentado en el issue #{num}.")
    else:
        gh("issue", "create", "--title", TITULO_ISSUE, "--label", ETIQUETA,
           "--body-file", "-", entrada=cuerpo)
        print("Issue de recordatorios creado.")


def main():
    cuerpo = construir_digest()
    if not cuerpo:
        print("No hay labores vencidas ni próximas. Nada que notificar.")
        return
    publicar_recordatorio(cuerpo)


if __name__ == "__main__":
    main()
