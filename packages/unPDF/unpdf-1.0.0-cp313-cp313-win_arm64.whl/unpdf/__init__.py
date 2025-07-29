"""""" # start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'unpdf.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

import pathlib
from .libpdf import _extract
from .table import CharTable, TextObjTable, FontTable, PageTable

def extract(path: str) -> tuple[PageTable, CharTable, TextObjTable, FontTable]:
    path = pathlib.Path(path)

    # make sure path exists
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist.")

    return _extract(str(path.resolve()).encode('utf-8'))
