#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whadeps.py - Arranque seguro de las herramientas

COMETIDO DE ESTE ARCHIVO
    Que a nadie le salte un traceback de Python al arrancar una herramienta.
    Se ocupa de dos cosas:

    1. DEPENDENCIAS. Cuando falta un modulo, se explica en una linea cual es y
       como instalarlo, en vez de soltar un traceback.

    2. CONSOLA. Los mensajes de WhatsApp traen emojis y caracteres que la
       consola de Windows (cp1252) no sabe representar. Al imprimirlos, Python
       aborta con UnicodeEncodeError y se pierde todo el analisis. safe_console()
       lo evita.

    No tiene linea de ordenes: lo usan las herramientas de libs/.

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import sys
import importlib
import importlib.util

# modulo que se importa -> paquete que hay que instalar con pip
PIP_NAME = {
    "Crypto": "pycryptodome",
    "Cryptodome": "pycryptodomex",
    "pyicloud": "pyicloud",
    "gpsoauth": "gpsoauth",
    "selenium": "selenium",
    "webdriver_manager": "webdriver-manager",
    "selenium_stealth": "selenium-stealth",
    "customtkinter": "customtkinter",
    "colorama": "colorama",
    "requests": "requests",
    "pandas": "pandas",
    "numpy": "numpy",
    "configobj": "ConfigObj",
    "click": "click",
    "packaging": "packaging",
}

_ABS = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.sep.join(_ABS.split(os.sep)[:-1])
_REQ = os.path.join(_RAIZ, "doc", "requirements.txt")


def _orden_pip(paquetes):
    pip = "pip3" if sys.platform != "win32" else "pip"
    return "{} install --upgrade {}".format(pip, " ".join(paquetes))


def require(*modulos, tool=None):
    """Comprueba que los modulos esten disponibles; si no, sale con un aviso.

    Uso al principio de una herramienta:
        whadeps.require("pyicloud", tool="whacloud")
    """
    faltan = []
    for m in modulos:
        try:
            importlib.import_module(m)
        except ImportError as e:
            # Si el modulo esta pero falla al cargarse, lo que falta es lo que
            # el importa. Se anota eso y no el modulo en si.
            interno = getattr(e, "name", None)
            if interno and interno != m:
                if interno not in faltan:
                    faltan.append(interno)
            elif m not in faltan:
                faltan.append(m)
        except Exception:
            pass
    if not faltan:
        return True

    paquetes = [PIP_NAME.get(m, m) for m in faltan]
    quien = " de {}".format(tool) if tool else ""
    print("\n[e] Faltan dependencias{}: {}".format(quien, ", ".join(faltan)))
    print("\n    Instala solo lo que falta:")
    print("        {}".format(_orden_pip(paquetes)))
    print("\n    O instala todas las dependencias del proyecto:")
    pip = "pip3" if sys.platform != "win32" else "pip"
    print('        {} install --upgrade -r "{}"'.format(pip, _REQ))
    print("\n    En la interfaz grafica tienes el boton «Instalar dependencias».\n")
    sys.exit(1)


def check(*modulos):
    """Como require(), pero devuelve la lista de los que faltan sin salir."""
    faltan = []
    for m in modulos:
        try:
            importlib.import_module(m)
        except ImportError:
            faltan.append(m)
        except Exception:
            pass
    return faltan


def safe_console():
    """Evita que imprimir un mensaje con emojis aborte la herramienta.

    Los mensajes de WhatsApp llevan emojis y simbolos que la consola de Windows
    (cp1252 o cp850) no puede representar. Sin esto, un solo emoji corta la
    ejecucion con UnicodeEncodeError, justo despues de haber leido toda la base.

    Se distinguen dos situaciones:

      * Salida canalizada (por ejemplo desde la interfaz grafica): se fuerza
        UTF-8, porque quien la lee sabe interpretarlo.
      * Consola real: se conserva su codificacion, para que los acentos se sigan
        viendo bien, pero se sustituye lo que no quepa por un caracter neutro
        en lugar de fallar.
    """
    for flujo in (sys.stdout, sys.stderr):
        if flujo is None:
            continue
        try:
            es_terminal = flujo.isatty()
        except Exception:
            es_terminal = False
        try:
            if es_terminal:
                flujo.reconfigure(errors="replace")
            else:
                flujo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass          # flujos que no admiten reconfigure: se deja como esta
