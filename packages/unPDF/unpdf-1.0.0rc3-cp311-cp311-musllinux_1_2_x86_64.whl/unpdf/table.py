import array

class PageTable:
    def __init__(self, n):
        self.arrays = {
            'page': array.array('i', [0] * n),
            'width': array.array('f', [0.0] * n),
            'height': array.array('f', [0.0] * n),
            'left': array.array('f', [0.0] * n),
            'right': array.array('f', [0.0] * n),
            'bottom': array.array('f', [0.0] * n),
            'top': array.array('f', [0.0] * n),
        }

    @property
    def table(self):
        import pyarrow as pa
        return pa.Table.from_pydict({k: pa.array(v) for k, v in self.arrays.items()})

class FontTable:
    def __init__(self, uq_fontptr: array.array):
        n = len(uq_fontptr)

        self.arrays = {
            'font_obj_id': uq_fontptr,
            'flags': array.array('i', [0] * n),
            'weight': array.array('i', [0] * n),
            'italic_angle': array.array('i', [0] * n),
            'base_fontname': [None] * n,
            'family_fontname': [None] * n,
        }

    @property
    def table(self):
        import pyarrow as pa
        return pa.Table.from_pydict({k: pa.array(v) for k, v in self.arrays.items()})

class TextObjTable:
    def __init__(self, uq_objptr: array.array):
        n = len(uq_objptr)

        self.arrays = {
            'txt_obj_id': uq_objptr,
            'fontsize': array.array('f', [0.0] * n),
            'has_transparency': array.array('i', [0] * n),
            'font_obj_id': array.array('Q', [0] * n),
            'color_R': array.array('I', [0] * n),
            'color_G': array.array('I', [0] * n),
            'color_B': array.array('I', [0] * n),
            'color_A': array.array('I', [0] * n),
            'tmatrix_a': array.array('f', [0.0] * n),
            'tmatrix_b': array.array('f', [0.0] * n),
            'tmatrix_c': array.array('f', [0.0] * n),
            'tmatrix_d': array.array('f', [0.0] * n),
            'tmatrix_e': array.array('f', [0.0] * n),
            'tmatrix_f': array.array('f', [0.0] * n),
        }

    @property
    def table(self):
        import pyarrow as pa
        return pa.Table.from_pydict({k: pa.array(v) for k, v in self.arrays.items()})

class CharTable:
    def __init__(self, n):
        self.arrays = {
            'page': array.array('i', [0] * n),
            'char': array.array('I', [0] * n),
            'is_generated': array.array('i', [0] * n),
            'txt_obj_id': array.array('Q', [0] * n),
            'left': array.array('d', [0.0] * n),
            'right': array.array('d', [0.0] * n),
            'bottom': array.array('d', [0.0] * n),
            'top': array.array('d', [0.0] * n),
            'loose_left': array.array('f', [0.0] * n),
            'loose_right': array.array('f', [0.0] * n),
            'loose_bottom': array.array('f', [0.0] * n),
            'loose_top': array.array('f', [0.0] * n),
            'bbox_ok': array.array('i', [0] * n),
            'loose_bbox_ok': array.array('i', [0] * n),
            'hyphen': array.array('i', [0] * n),
            'has_unicode_map_error': array.array('i', [0] * n),
        }

    @property
    def table(self):
        import pyarrow as pa

        arrays = self.arrays.copy()
        arrays['char'] = arrays['char'].tobytes().decode('utf32')

        return pa.Table.from_pydict({k: pa.array(v) for k, v in arrays.items()})