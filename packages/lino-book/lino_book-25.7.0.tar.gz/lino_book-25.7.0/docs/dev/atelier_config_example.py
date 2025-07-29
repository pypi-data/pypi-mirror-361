# NB lines 1-9 are not shown on docs/dev/env.rst and are not meant to
# go to your atelier config file. They are here for testing the script.
import unipath


def add_project(p):
    print(unipath.Path(p))


from pathlib import Path
for root in ["~/lino/lino_local", "~/lino/env/repositories"]:
    for p in Path(root).expanduser().iterdir():
        if p.is_dir():
            add_project(str(p))
