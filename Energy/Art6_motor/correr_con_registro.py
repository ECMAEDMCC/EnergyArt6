# -*- coding: utf-8 -*-
"""Corre un paso de la cadena mostrando su salida en la terminal y copiándola al registro de la corrida.

Uso (lo llama ejecutar_modelo.bat):
    python Energy/Art6_motor/correr_con_registro.py --registro <archivo.log> --titulo "B1" -- python B1_Base_Scenarios_Adj_Parallel.py

Escribe en el registro la hora de inicio y de fin, la duración y el código de salida del paso. Sale con el código del
paso, para que el .bat decida si sigue.
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registro", required=True)
    ap.add_argument("--titulo", required=True)
    ap.add_argument("comando", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.comando[1:] if a.comando and a.comando[0] == "--" else a.comando
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    t0 = time.time()
    with open(a.registro, "a", encoding="utf-8", newline="") as log:
        cab = "\n===== %s · %s · %s\n" % (a.titulo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), " ".join(cmd))
        log.write(cab)
        print(cab, end="", flush=True)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True,
                             encoding="utf-8", errors="replace", bufsize=1)
        for linea in p.stdout:
            sys.stdout.write(linea)
            sys.stdout.flush()
            log.write(linea)
        p.wait()
        pie = "===== %s terminó con código %d en %.0f s (%s)\n" % (a.titulo, p.returncode, time.time() - t0,
                                                                 datetime.now().strftime("%H:%M:%S"))
        log.write(pie)
        print(pie, end="", flush=True)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
