"""Empaqueta cada carpeta de datapacks/ en dist/<Nombre>.zip (con pack.mcmeta en la raíz, listo para copiar a saves/<mundo>/datapacks/)."""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "datapacks")
OUT = os.path.join(ROOT, "dist")
os.makedirs(OUT, exist_ok=True)

for name in sorted(os.listdir(SRC)):
    folder = os.path.join(SRC, name)
    if not os.path.isfile(os.path.join(folder, "pack.mcmeta")):
        continue
    zp = os.path.join(OUT, "".join(w.capitalize() for w in name.split("_")) + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(folder):
            for f in files:
                full = os.path.join(dirpath, f)
                z.write(full, os.path.relpath(full, folder).replace(os.sep, "/"))
    print("created", os.path.relpath(zp, ROOT))
