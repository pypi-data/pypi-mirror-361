# cython: infer_types=True
# cython: boundscheck=False
# cython: wraparound=False

import atexit
import array
from cpython cimport array

from . cimport cpdfium
from .table import CharTable, TextObjTable, FontTable, PageTable

from libc.stdlib cimport malloc, free
from libc.stdint cimport uint64_t

_initialized = False

cpdef void _lib_init():
    global _initialized
    assert not _initialized

    cdef cpdfium.FPDF_LIBRARY_CONFIG _c_config

    _c_config.version = 2
    _c_config.m_pUserFontPaths = NULL
    _c_config.m_pIsolate = NULL
    _c_config.m_v8EmbedderSlot = 0
    _c_config.m_pPlatform = NULL
    _c_config.m_RendererType = cpdfium.FPDF_RENDERER_TYPE.FPDF_RENDERERTYPE_AGG

    cpdfium.FPDF_InitLibraryWithConfig(&_c_config)

    _initialized = True

cpdef void _lib_destroy():
    global _initialized
    assert _initialized

    cpdfium.FPDF_DestroyLibrary()
    _initialized = False

cdef _extract_chars(cpdfium.FPDF_TEXTPAGE* buf_textpages, int count):
    cdef cpdfium.FPDF_TEXTPAGE textpage
    cdef int i, j, k, n, offset, total_chars


    cdef array.array arr_pagechars = array.array('i', [0] * (count + 1))
    cdef int[:] buf_pagechars = arr_pagechars
    cdef array.array arr_pageoffset = array.array('l', [0] * (count + 1))
    cdef long[:] buf_pageoffset = arr_pageoffset

    for i in range(count):
        textpage = buf_textpages[i]
        buf_pagechars[i+1] = cpdfium.FPDFText_CountChars(textpage)
        buf_pageoffset[i+1] = buf_pageoffset[i] + buf_pagechars[i+1]

    total_chars = buf_pageoffset[count]

    tbl = CharTable(total_chars)

    # Create memory views
    cdef int[:] buf_page = tbl.arrays['page']
    cdef unsigned int[:] buf_char = tbl.arrays['char']
    cdef int[:] buf_generated = tbl.arrays['is_generated']
    cdef uint64_t[:] buf_objptr = tbl.arrays['txt_obj_id']
    cdef int[:] buf_bbox_ok = tbl.arrays['bbox_ok']
    cdef int[:] buf_loose_bbox_ok = tbl.arrays['loose_bbox_ok']
    cdef double[:] buf_left = tbl.arrays['left']
    cdef double[:] buf_right = tbl.arrays['right']
    cdef double[:] buf_bottom = tbl.arrays['bottom']
    cdef double[:] buf_top = tbl.arrays['top']
    cdef float[:] buf_loose_left = tbl.arrays['loose_left']
    cdef float[:] buf_loose_right = tbl.arrays['loose_right']
    cdef float[:] buf_loose_bottom = tbl.arrays['loose_bottom']
    cdef float[:] buf_loose_top = tbl.arrays['loose_top']
    cdef int[:] buf_hyphen = tbl.arrays['hyphen']
    cdef int[:] buf_unicodemaperror = tbl.arrays['has_unicode_map_error']

    cdef cpdfium.FPDF_TEXTPAGE * iter_pages = <cpdfium.FPDF_TEXTPAGE *> malloc(sizeof(cpdfium.FPDF_TEXTPAGE) * total_chars)
    cdef int* iter_idx = <int*> malloc(sizeof(int) * total_chars)

    for i in range(count):
        textpage = buf_textpages[i]
        n = buf_pagechars[i + 1]
        offset = buf_pageoffset[i]
        for j in range(n):
            k = offset + j
            buf_page[k] = i
            iter_pages[k] = textpage
            iter_idx[k] = j

    # Fill values
    for offset in range(total_chars):
        _fill_chars_data(iter_pages[offset], offset, iter_idx[offset],
                       &buf_char[0], &buf_generated[0], &buf_objptr[0],
                       &buf_left[0], &buf_right[0], &buf_bottom[0], &buf_top[0],
                       &buf_loose_left[0], &buf_loose_right[0], &buf_loose_bottom[0], &buf_loose_top[0],
                       &buf_bbox_ok[0], &buf_loose_bbox_ok[0],
                       &buf_hyphen[0], &buf_unicodemaperror[0])

    free(iter_pages)
    free(iter_idx)

    return tbl

cdef inline void _fill_chars_data(cpdfium.FPDF_TEXTPAGE textpage, int offset, int i,
                         unsigned int* buf_char, int *buf_generated, uint64_t *buf_objptr,
                         double* buf_left, double* buf_right, double* buf_bottom, double* buf_top,
                         float* buf_loose_left, float* buf_loose_right, float* buf_loose_bottom, float* buf_loose_top,
                         int* buf_bbox_ok, int* buf_loose_bbox_ok,
                         int* buf_hyphen, int* buf_unicodemaperror) noexcept nogil:
    cdef cpdfium.FS_RECTF rect

    buf_generated[offset] = cpdfium.FPDFText_IsGenerated(textpage, i)
    buf_char[offset] = cpdfium.FPDFText_GetUnicode(textpage, i)
    buf_objptr[offset] = <uint64_t> cpdfium.FPDFText_GetTextObject(textpage, i)

    buf_bbox_ok[offset] = cpdfium.FPDFText_GetCharBox(textpage, i, &buf_left[offset], &buf_right[offset], &buf_bottom[offset], &buf_top[offset])
    buf_loose_bbox_ok[offset] = cpdfium.FPDFText_GetLooseCharBox(textpage, i, &rect)

    buf_loose_left[offset] = rect.left
    buf_loose_right[offset] = rect.right
    buf_loose_bottom[offset] = rect.bottom
    buf_loose_top[offset] = rect.top

    buf_hyphen[offset] = cpdfium.FPDFText_IsHyphen(textpage, i)
    buf_unicodemaperror[offset] = cpdfium.FPDFText_HasUnicodeMapError(textpage, i)

cdef _extract_textobjs(arr_objptr):
    py_uq_objptr = filter(None, sorted(set(arr_objptr)))  # Filter because we want to evict null pointer
    cdef array.array arr_uq_objptr = array.array('Q', py_uq_objptr)

    if arr_uq_objptr[0] == 0:
        arr_uq_objptr = arr_uq_objptr[1:]  # Filter out null pointer

    cdef int n_objs = len(arr_uq_objptr)

    # Prepare numpy arrays
    tbl = TextObjTable(arr_uq_objptr)

    # Create memory views
    cdef uint64_t[:] uq_objptrs = arr_uq_objptr
    cdef float[:] buf_fontsize = tbl.arrays['fontsize']
    cdef int[:] buf_transparency = tbl.arrays['has_transparency']
    cdef uint64_t[:] buf_fontptr = tbl.arrays['font_obj_id']
    cdef unsigned int[:] buf_color_r = tbl.arrays['color_R']
    cdef unsigned int[:] buf_color_g = tbl.arrays['color_G']
    cdef unsigned int[:] buf_color_b = tbl.arrays['color_B']
    cdef unsigned int[:] buf_color_a = tbl.arrays['color_A']
    cdef float[:] buf_tmatrix_a = tbl.arrays['tmatrix_a']
    cdef float[:] buf_tmatrix_b = tbl.arrays['tmatrix_b']
    cdef float[:] buf_tmatrix_c = tbl.arrays['tmatrix_c']
    cdef float[:] buf_tmatrix_d = tbl.arrays['tmatrix_d']
    cdef float[:] buf_tmatrix_e = tbl.arrays['tmatrix_e']
    cdef float[:] buf_tmatrix_f = tbl.arrays['tmatrix_f']


    _fill_textobjs_data(<cpdfium.FPDF_PAGEOBJECT *> &uq_objptrs[0], n_objs,
                        &buf_fontsize[0], &buf_transparency[0], &buf_fontptr[0],
                        &buf_color_r[0], &buf_color_g[0], &buf_color_b[0], &buf_color_a[0],
                        &buf_tmatrix_a[0], &buf_tmatrix_b[0], &buf_tmatrix_c[0],
                        &buf_tmatrix_d[0], &buf_tmatrix_e[0], &buf_tmatrix_f[0])

    return tbl


cdef void _fill_textobjs_data(cpdfium.FPDF_PAGEOBJECT* ptrs, int n,
                              float* buf_fontsize, int* buf_transparency, uint64_t* buf_fontptr,
                              unsigned int* buf_color_r, unsigned int* buf_color_g,
                              unsigned int* buf_color_b, unsigned int* buf_color_a,
                              float* buf_tmatrix_a, float* buf_tmatrix_b, float* buf_tmatrix_c,
                              float* buf_tmatrix_d, float* buf_tmatrix_e, float* buf_tmatrix_f):
    cdef int i
    cdef cpdfium.FS_MATRIX tmatrix

    for i in range(0, n):
        obj = ptrs[i]

        cpdfium.FPDFTextObj_GetFontSize(obj, &buf_fontsize[i])
        buf_transparency[i] = cpdfium.FPDFPageObj_HasTransparency(obj)
        buf_fontptr[i] = <uint64_t> cpdfium.FPDFTextObj_GetFont(obj)

        cpdfium.FPDFPageObj_GetFillColor(obj, &buf_color_r[i], &buf_color_g[i], &buf_color_b[i], &buf_color_a[i])

        cpdfium.FPDFPageObj_GetMatrix(obj, &tmatrix)
        buf_tmatrix_a[i] = tmatrix.a
        buf_tmatrix_b[i] = tmatrix.b
        buf_tmatrix_c[i] = tmatrix.c
        buf_tmatrix_d[i] = tmatrix.d
        buf_tmatrix_e[i] = tmatrix.e
        buf_tmatrix_f[i] = tmatrix.f

cdef _extract_fonts(arr_fontptr):
    py_uq_fontptr = filter(None, sorted(set(arr_fontptr)))  # Filter because we want to evict null pointer
    cdef array.array arr_uq_fontptr = array.array('Q', py_uq_fontptr)

    cdef int n_fonts = len(arr_uq_fontptr)

    cdef uint64_t[:] uq_fontptr = arr_uq_fontptr

    # Prepare numpy arrays
    tbl = FontTable(arr_uq_fontptr)

    # Create memory views
    cdef int[:] buf_flags = tbl.arrays['flags']
    cdef int[:] buf_weight = tbl.arrays['weight']
    cdef int[:] buf_italic_angle = tbl.arrays['italic_angle']
    cdef list[str] buf_basefontname = tbl.arrays['base_fontname']
    cdef list[str] buf_familyfontname = tbl.arrays['family_fontname']

    _fill_fonts_data(<cpdfium.FPDF_FONT *> &uq_fontptr[0], n_fonts,
                     &buf_flags[0], &buf_weight[0], &buf_italic_angle[0],
                     buf_basefontname, buf_familyfontname)

    return tbl


cdef void _fill_fonts_data(cpdfium.FPDF_FONT* ptrs, int n,
                           int* buf_flags, int* buf_weight, int* buf_italic_angle,
                           list[str] buf_basefontname, list[str] buf_familyfontname):
    cdef int i
    cdef char* buffer = <char*> malloc(sizeof(char) * 512)
    cdef bytes py_string

    for i in range(0, n):
        font = ptrs[i]

        buf_flags[i] = cpdfium.FPDFFont_GetFlags(font)
        buf_weight[i] = cpdfium.FPDFFont_GetWeight(font)
        cpdfium.FPDFFont_GetItalicAngle(font, &buf_italic_angle[i])

        length = cpdfium.FPDFFont_GetBaseFontName(font, buffer, 512)
        if length > 0:
            length -= 1  # remove ending null char
        py_string = buffer[:length]
        buf_basefontname[i] = py_string.decode('utf-8')

        length = cpdfium.FPDFFont_GetFamilyName(font, buffer, 512)
        if length > 0:
            length -= 1
        py_string = buffer[:length]
        buf_familyfontname[i] = py_string.decode('utf-8')
    
    free(buffer)


cdef _extract_pages(cpdfium.FPDF_TEXTPAGE* buf_textpages, int count):
    cdef cpdfium.FS_RECTF bbox

    chars_tbl = _extract_chars(buf_textpages, count)
    objs_tbl = _extract_textobjs(chars_tbl.arrays['txt_obj_id'])
    fonts_tbl = _extract_fonts(objs_tbl.arrays['font_obj_id'])

    return chars_tbl, objs_tbl, fonts_tbl


cpdef _extract(char* path):
    global _initialized
    assert _initialized, "Library was not initialized"

    doc = cpdfium.FPDF_LoadDocument(path , NULL)
    err = cpdfium.FPDF_GetLastError()

    if err != 0:
        raise ValueError(f'LoadDocument Error code: {err}')

    count = cpdfium.FPDF_GetPageCount(doc)
    tbl = PageTable(count)

    cdef float[:] buf_width = tbl.arrays['width']
    cdef float[:] buf_height = tbl.arrays['height']
    cdef float[:] buf_left = tbl.arrays['left']
    cdef float[:] buf_top = tbl.arrays['top']
    cdef float[:] buf_bottom = tbl.arrays['bottom']
    cdef float[:] buf_right = tbl.arrays['right']

    cdef cpdfium.FPDF_PAGE* buf_pages = <cpdfium.FPDF_PAGE*> malloc(sizeof(cpdfium.FPDF_PAGE) * count)
    cdef cpdfium.FPDF_TEXTPAGE* buf_textpages = <cpdfium.FPDF_TEXTPAGE*> malloc(sizeof(cpdfium.FPDF_TEXTPAGE) * count)

    cdef int i
    cdef cpdfium.FS_RECTF rect
    for i in range(count):
        buf_pages[i] = cpdfium.FPDF_LoadPage(doc, i)
        buf_textpages[i] = cpdfium.FPDFText_LoadPage(buf_pages[i])
        cpdfium.FPDF_GetPageBoundingBox(buf_pages[i], &rect)
        buf_width[i] = cpdfium.FPDF_GetPageWidthF(buf_pages[i])
        buf_height[i] = cpdfium.FPDF_GetPageHeightF(buf_pages[i])
        buf_left[i] = rect.left
        buf_top[i] = rect.top
        buf_bottom[i] = rect.bottom
        buf_right[i] = rect.right

    out = _extract_pages(buf_textpages, count)

    # Destroy pdfium objects
    for i in range(count):
        cpdfium.FPDFText_ClosePage(buf_textpages[i])
        cpdfium.FPDF_ClosePage(buf_pages[i])
    free(buf_pages)
    free(buf_textpages)
    cpdfium.FPDF_CloseDocument(doc)

    return (tbl, *out)

_lib_init()
atexit.register(_lib_destroy)