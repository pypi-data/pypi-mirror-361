import pathlib
from .libpdf import _extract
from .table import CharTable, TextObjTable, FontTable, PageTable

def extract(path: str) -> tuple[PageTable, CharTable, TextObjTable, FontTable]:
    path = pathlib.Path(path)

    # make sure path exists
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist.")

    return _extract(str(path.resolve()).encode('utf-8'))