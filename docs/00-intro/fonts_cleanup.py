#!/usr/bin/env python3
"""Remove references to fonts PowerPoint cannot embed and keep slide text in Roboto."""
import re, sys, zipfile
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'a': A}
REPLACE = {'sohne': 'Roboto', 'Times': 'Roboto', 'Noto Sans Symbols': 'Arial', 'Helvetica Neue': 'Roboto'}
KEEP = {'Cambria Math'}
AFTER_LATIN = {f'{{{A}}}{t}' for t in ('ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')}


def in_math(el):
    p = el.getparent()
    while p is not None:
        if p.tag.startswith(f'{{{M}}}'):
            return True
        p = p.getparent()
    return False


def set_font(el, face):
    for k in ('panose', 'pitchFamily', 'charset'):
        el.attrib.pop(k, None)
    el.set('typeface', face)


def roboto_pass(root):
    n = 0
    for r in list(root.iter(f'{{{A}}}r', f'{{{A}}}fld', f'{{{A}}}br')):
        if in_math(r) or r.find('a:rPr', NS) is not None:
            continue
        rpr = etree.Element(f'{{{A}}}rPr'); rpr.set('lang', 'en'); r.insert(0, rpr)
    for rpr in root.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr', f'{{{A}}}defRPr'):
        if in_math(rpr):
            continue
        latin = rpr.find('a:latin', NS)
        if latin is not None and latin.get('typeface') in KEEP:
            continue
        if latin is None:
            latin = etree.Element(f'{{{A}}}latin')
            pos = next((i for i, c in enumerate(rpr) if c.tag in AFTER_LATIN), len(rpr))
            rpr.insert(pos, latin)
        if latin.get('typeface') != 'Roboto':
            n += 1
        set_font(latin, 'Roboto')
        for tag in ('ea', 'cs'):
            el = rpr.find(f'a:{tag}', NS)
            if el is not None and el.get('typeface') not in KEEP:
                set_font(el, 'Roboto')
    return n


def main():
    z = zipfile.ZipFile(SRC)
    parts = {n: z.read(n) for n in z.namelist()}
    report = {}
    for name in list(parts):
        if not name.endswith('.xml') or name == '[Content_Types].xml':
            continue
        data = parts[name]
        hit = any(f'typeface="{f}"'.encode() in data for f in REPLACE)
        is_slide = re.match(r'ppt/slides/slide\d+\.xml$', name)
        if not hit and not is_slide:
            continue
        root = etree.fromstring(data)
        changes = 0
        for el in root.iter(f'{{{A}}}latin', f'{{{A}}}ea', f'{{{A}}}cs', f'{{{A}}}sym', f'{{{A}}}buFont'):
            face = el.get('typeface')
            if face in REPLACE:
                set_font(el, REPLACE[face]); changes += 1
        if is_slide:
            changes += roboto_pass(root)
        if changes:
            parts[name] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            report[name] = changes
    for k, v in sorted(report.items()):
        print(f'  {k}: {v} font references changed')
    left = set()
    for name, data in parts.items():
        if name.endswith('.xml'):
            for f in REPLACE:
                if f'typeface="{f}"'.encode() in data:
                    left.add((name, f))
    print('remaining references to unavailable fonts:', sorted(left) or 'none')
    with zipfile.ZipFile(OUT, 'w') as zo:
        for k in ['[Content_Types].xml'] + [k for k in parts if k != '[Content_Types].xml']:
            stored = k.startswith(('ppt/media/', 'ppt/fonts/', 'ppt/embeddings/'))
            zo.writestr(k, parts[k], compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
