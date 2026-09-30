#!/usr/bin/env python3
"""Assemble the Lecture 1 deck from three source decks.

Base template: 00-intro.pptx (masters, layouts, theme, notes master, fonts).
Imported slides keep their shapes and media. Slides from Lecture 1.pptx are
scaled from a 12192000x6858000 canvas to 9144000x5143500 (factor 0.75) and
remapped onto the base "title only" layout.
"""
import html, posixpath, re, sys, zipfile
from lxml import etree

SRC_DIR = '/Users/krishna/courses/CE397-Scientific-MachineLearning/sciml/00-intro/'
OUT = sys.argv[1] if len(sys.argv) > 1 else SRC_DIR + 'lecture-01-introduction.pptx'
SRC = {'B': SRC_DIR + '00-intro.pptx',
       'L': SRC_DIR + 'Lecture 1.pptx',
       'W': SRC_DIR + '2026-WorldModels-TAMU.pptx'}

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'a': A, 'p': P, 'r': R}
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
CT_SLIDE = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
CT_NOTES = 'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'
RT_SLIDE = R + '/slide'
RT_LAYOUT = R + '/slideLayout'
LAYOUT_TITLE_ONLY = 'ppt/slideLayouts/slideLayout17.xml'   # base "Title and body" layout used by 57/70 base slides
LAYOUT_SECTION = 'ppt/slideLayouts/slideLayout22.xml'      # base two-tone section layout (slide 16)
NOTES_MASTER = 'ppt/notesMasters/notesMaster1.xml'
ORANGE = 'BF5700'
GRAY = '424242'
LIGHT_GRAY = '737373'


def tostr(el):
    return etree.tostring(el, xml_declaration=True, encoding='UTF-8', standalone=True)


def rels_path(part):
    d, b = posixpath.split(part)
    return f'{d}/_rels/{b}.rels'


def resolve(part, target):
    if target.startswith('/'):
        return target.lstrip('/')
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))


def rel_target(new_part, from_part):
    return posixpath.relpath(new_part, posixpath.dirname(from_part))


class Pkg:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self.names = set(self.z.namelist())
        ct = etree.fromstring(self.z.read('[Content_Types].xml'))
        self.defaults = {e.get('Extension').lower(): e.get('ContentType') for e in ct if e.tag.endswith('Default')}
        self.overrides = {e.get('PartName'): e.get('ContentType') for e in ct if e.tag.endswith('Override')}
        pres = etree.fromstring(self.z.read('ppt/presentation.xml'))
        prels = etree.fromstring(self.z.read('ppt/_rels/presentation.xml.rels'))
        rid2t = {r.get('Id'): r.get('Target') for r in prels}
        self.slides = [resolve('ppt/presentation.xml', rid2t[s.get(f'{{{R}}}id')])
                       for s in pres.find('p:sldIdLst', NS)]

    def read(self, name):
        return self.z.read(name)

    def ctype(self, part):
        return self.overrides.get('/' + part) or self.defaults.get(part.rsplit('.', 1)[-1].lower())

    def rels(self, part):
        rp = rels_path(part)
        if rp not in self.names:
            return None
        return etree.fromstring(self.z.read(rp))

    def slide(self, n):
        return self.slides[n - 1]


class Target:
    def __init__(self, base):
        self.base = base
        self.parts = {}
        self.defaults = dict(base.defaults)
        self.overrides = {}
        self.cache = {}
        for n in base.names:
            if n == '[Content_Types].xml' or n.startswith(('ppt/slides/', 'ppt/notesSlides/', 'ppt/media/')):
                continue
            self.parts[n] = base.read(n)
        # keep base media referenced by kept parts (masters, layouts, notes master)
        for n in list(self.parts):
            if not n.endswith('.rels'):
                continue
            owner = n.replace('/_rels/', '/')[:-5]
            for r in etree.fromstring(self.parts[n]):
                if r.get('TargetMode') == 'External':
                    continue
                t = resolve(owner, r.get('Target'))
                if t.startswith('ppt/media/') and t in base.names:
                    self.parts[t] = base.read(t)
        for n in self.parts:
            ct = base.overrides.get('/' + n)
            if ct:
                self.overrides['/' + n] = ct

    def register_ct(self, pkg, src_part, new_name):
        ct = pkg.ctype(src_part)
        if ct is None:
            raise RuntimeError(f'no content type for {src_part}')
        ext = new_name.rsplit('.', 1)[-1].lower()
        if self.defaults.get(ext) == ct:
            return
        if ext not in self.defaults and pkg.defaults.get(ext) == ct:
            self.defaults[ext] = ct
            return
        self.overrides['/' + new_name] = ct

    def import_part(self, pkg, key, src_part):
        """Copy a generic part and everything it references. Returns the new part name."""
        ck = (key, src_part)
        if ck in self.cache:
            return self.cache[ck]
        d, b = posixpath.split(src_part)
        new_name = f'{d}/{key}_{b}'
        self.cache[ck] = new_name
        self.parts[new_name] = pkg.read(src_part)
        self.register_ct(pkg, src_part, new_name)
        rels = pkg.rels(src_part)
        if rels is not None:
            for r in list(rels):
                if r.get('TargetMode') == 'External':
                    continue
                t = resolve(src_part, r.get('Target'))
                nt = self.import_part(pkg, key, t)
                r.set('Target', rel_target(nt, new_name))
            self.parts[rels_path(new_name)] = tostr(rels)
        return new_name

    def import_notes(self, pkg, key, src, new_name, slide_new):
        self.parts[new_name] = pkg.read(src)
        self.overrides['/' + new_name] = CT_NOTES
        rels = pkg.rels(src)
        for r in list(rels):
            if r.get('TargetMode') == 'External':
                continue
            rtype = r.get('Type').rsplit('/', 1)[-1]
            t = resolve(src, r.get('Target'))
            if rtype == 'notesMaster':
                nt = NOTES_MASTER
            elif rtype == 'slide':
                nt = slide_new
            else:
                nt = self.import_part(pkg, key, t)
            r.set('Target', rel_target(nt, new_name))
        self.parts[rels_path(new_name)] = tostr(rels)

    def import_slide(self, pkg, key, n, idx, layout=None, transform=None):
        src = pkg.slide(n)
        new_name = f'ppt/slides/slide{idx}.xml'
        root = etree.fromstring(pkg.read(src))
        rels = pkg.rels(src)
        notes = None
        for r in list(rels):
            if r.get('TargetMode') == 'External':
                continue
            rtype = r.get('Type').rsplit('/', 1)[-1]
            t = resolve(src, r.get('Target'))
            if rtype == 'slideLayout':
                nt = layout or t
                if nt not in self.parts:
                    raise RuntimeError(f'layout {nt} missing in target')
            elif rtype == 'notesSlide':
                notes = (t, r)
                continue
            else:
                nt = self.import_part(pkg, key, t)
            r.set('Target', rel_target(nt, new_name))
        if notes:
            t, r = notes
            nn = f'ppt/notesSlides/notesSlide{idx}.xml'
            self.import_notes(pkg, key, t, nn, new_name)
            r.set('Target', rel_target(nn, new_name))
        if transform:
            transform(root)
        self.parts[new_name] = tostr(root)
        self.parts[rels_path(new_name)] = tostr(rels)
        self.overrides['/' + new_name] = CT_SLIDE
        return new_name

    def add_slide_xml(self, idx, xml_bytes, layout):
        new_name = f'ppt/slides/slide{idx}.xml'
        self.parts[new_name] = xml_bytes
        self.overrides['/' + new_name] = CT_SLIDE
        rels = etree.Element(f'{{{PKG}}}Relationships', nsmap={None: PKG})
        r = etree.SubElement(rels, f'{{{PKG}}}Relationship')
        r.set('Id', 'rId1'); r.set('Type', RT_LAYOUT); r.set('Target', rel_target(layout, new_name))
        self.parts[rels_path(new_name)] = tostr(rels)
        return new_name

    def finalize(self, slide_parts):
        pres = etree.fromstring(self.parts['ppt/presentation.xml'])
        lst = pres.find('p:sldIdLst', NS)
        for c in list(lst):
            lst.remove(c)
        prels = etree.fromstring(self.parts['ppt/_rels/presentation.xml.rels'])
        for r in list(prels):
            if r.get('Type') == RT_SLIDE:
                prels.remove(r)
        for i, part in enumerate(slide_parts, 1):
            rid = f'rId{1000 + i}'
            el = etree.SubElement(lst, f'{{{P}}}sldId')
            el.set('id', str(255 + i)); el.set(f'{{{R}}}id', rid)
            rel = etree.SubElement(prels, f'{{{PKG}}}Relationship')
            rel.set('Id', rid); rel.set('Type', RT_SLIDE); rel.set('Target', rel_target(part, 'ppt/presentation.xml'))
        self.parts['ppt/presentation.xml'] = tostr(pres)
        self.parts['ppt/_rels/presentation.xml.rels'] = tostr(prels)
        types = etree.Element(f'{{{CT}}}Types', nsmap={None: CT})
        for ext, ct in sorted(self.defaults.items()):
            e = etree.SubElement(types, f'{{{CT}}}Default'); e.set('Extension', ext); e.set('ContentType', ct)
        for pn, ct in sorted(self.overrides.items()):
            if pn.lstrip('/') in self.parts:
                e = etree.SubElement(types, f'{{{CT}}}Override'); e.set('PartName', pn); e.set('ContentType', ct)
        self.parts['[Content_Types].xml'] = tostr(types)

    def check(self):
        problems = []
        for n, data in self.parts.items():
            if not n.endswith('.rels'):
                continue
            owner = '' if n == '_rels/.rels' else n.replace('/_rels/', '/')[:-5]
            for r in etree.fromstring(data):
                if r.get('TargetMode') == 'External':
                    continue
                t = resolve(owner, r.get('Target'))
                if t not in self.parts:
                    problems.append(f'{owner} -> missing {t}')
        for n in self.parts:
            if n in ('[Content_Types].xml',) or n.endswith('.rels'):
                continue
            ext = n.rsplit('.', 1)[-1].lower()
            if '/' + n not in self.overrides and ext not in self.defaults:
                problems.append(f'no content type: {n}')
        return problems

    def write(self, path):
        with zipfile.ZipFile(path, 'w') as z:
            order = ['[Content_Types].xml', '_rels/.rels'] + sorted(n for n in self.parts if n not in ('[Content_Types].xml', '_rels/.rels'))
            for n in order:
                stored = n.startswith(('ppt/media/', 'ppt/fonts/', 'ppt/embeddings/'))
                z.writestr(n, self.parts[n], compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)


# ---------------------------------------------------------------- transforms
SCALE_TAGS = {
    f'{{{A}}}off': ('x', 'y'), f'{{{A}}}ext': ('cx', 'cy'),
    f'{{{A}}}chOff': ('x', 'y'), f'{{{A}}}chExt': ('cx', 'cy'),
    f'{{{A}}}rPr': ('sz',), f'{{{A}}}defRPr': ('sz',), f'{{{A}}}endParaRPr': ('sz',),
    f'{{{A}}}ln': ('w',), f'{{{A}}}spcPts': ('val',), f'{{{A}}}buSzPts': ('val',),
    f'{{{A}}}bodyPr': ('lIns', 'tIns', 'rIns', 'bIns'),
    f'{{{A}}}gridCol': ('w',), f'{{{A}}}tr': ('h',), f'{{{A}}}tab': ('pos',),
}
for _lvl in ['pPr'] + [f'lvl{i}pPr' for i in range(1, 10)]:
    SCALE_TAGS[f'{{{A}}}{_lvl}'] = ('marL', 'marR', 'indent', 'defTabSz')


def scale(root, f):
    for el in root.iter():
        attrs = SCALE_TAGS.get(el.tag)
        if not attrs:
            continue
        for a in attrs:
            v = el.get(a)
            if v is not None and re.fullmatch(r'-?\d+', v):
                el.set(a, str(int(round(int(v) * f))))


INSET_DEFAULTS = {'lIns': 91440, 'rIns': 91440, 'tIns': 45720, 'bIns': 45720}


def fix_insets(root, f):
    """Make default text-box margins explicit and scaled, so shrunken shapes wrap like the originals."""
    for bp in root.iter(f'{{{A}}}bodyPr'):
        for k, v in INSET_DEFAULTS.items():
            if bp.get(k) is None:
                bp.set(k, str(int(round(v * f))))


def shapes_with_ph(root, types):
    out = []
    for sp in root.iter(f'{{{P}}}sp'):
        ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is not None and ph.get('type', 'body') in types:
            out.append(sp)
    return out


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(f'{{{A}}}t'))


def strip_bg(root):
    for bg in root.findall('p:cSld/p:bg', NS):
        bg.getparent().remove(bg)


def drop_ph(root, types):
    for sp in shapes_with_ph(root, types):
        sp.getparent().remove(sp)


def fix_title(root, inherit=True, sz=None, long_sz=2400, long_len=36):
    for sp in shapes_with_ph(root, ('title', 'ctrTitle')):
        if inherit:
            for x in sp.findall('p:spPr/a:xfrm', NS):
                x.getparent().remove(x)
            for rpr in sp.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr'):
                lang = rpr.get('lang')
                rpr.attrib.clear()
                for c in list(rpr):
                    rpr.remove(c)
                if lang:
                    rpr.set('lang', lang)
        s = sz or (long_sz if len(text_of(sp).strip()) > long_len else None)
        if s:
            for rpr in sp.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr'):
                rpr.set('sz', str(s))


SLDNUM_TXBODY = (f'<p:txBody xmlns:p="{P}" xmlns:a="{A}"><a:bodyPr anchorCtr="0" anchor="ctr" bIns="91425" lIns="91425" spcFirstLastPara="1" rIns="91425" wrap="square" tIns="91425"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
                 '<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="r"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr>'
                 '<a:fld id="{00000000-1234-1234-1234-123412341234}" type="slidenum"><a:rPr lang="en"/><a:t>‹#›</a:t></a:fld><a:endParaRPr/></a:p></p:txBody>')
SLDNUM_SP = (f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="9901" name="Slide Number"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph idx="12" type="sldNum"/></p:nvPr></p:nvSpPr>'
             '<p:spPr><a:xfrm><a:off x="8523541" y="4695623"/><a:ext cx="548700" cy="393600"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
             + SLDNUM_TXBODY + '</p:sp>')


def ensure_sldnum(root):
    sps = shapes_with_ph(root, ('sldNum',))
    if sps:
        for sp in sps:
            old = sp.find('p:txBody', NS)
            sp.replace(old, etree.fromstring(SLDNUM_TXBODY))
    else:
        root.find('p:cSld/p:spTree', NS).append(etree.fromstring(SLDNUM_SP))


def remove_bare_numbers(root):
    for sp in list(root.iter(f'{{{P}}}sp')):
        if sp.find('p:nvSpPr/p:nvPr/p:ph', NS) is None and re.fullmatch(r'\d{1,3}', text_of(sp).strip() or 'x'):
            sp.getparent().remove(sp)


SCHEME_ALIAS = {'tx1': 'dk1', 'bg1': 'lt1', 'tx2': 'dk2', 'bg2': 'lt2'}


def theme_colors(pkg, theme_part):
    root = etree.fromstring(pkg.read(theme_part))
    out = {}
    for el in root.find('.//a:clrScheme', NS):
        name = etree.QName(el).localname
        c = el[0]
        out[name] = c.get('val') if etree.QName(c).localname == 'srgbClr' else c.get('lastClr', '000000')
    return out


def resolve_scheme_colors(root, cmap):
    """Replace theme colour references with the source theme's RGB values."""
    for el in list(root.iter(f'{{{A}}}schemeClr')):
        name = el.get('val')
        rgb = cmap.get(SCHEME_ALIAS.get(name, name))
        if rgb is None:
            continue
        el.tag = f'{{{A}}}srgbClr'
        el.set('val', rgb)


RPR_AFTER_LATIN = {f'{{{A}}}{t}' for t in ('ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')}


def fix_default_text(root, sz, minor='Calibri', major='Calibri Light'):
    """Non-placeholder shapes: make inherited size and font explicit (source theme defaults)."""
    for sp in root.iter(f'{{{P}}}sp'):
        if sp.find('p:nvSpPr/p:nvPr/p:ph', NS) is not None:
            continue
        for rpr in sp.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr'):
            if rpr.get('sz') is None:
                rpr.set('sz', str(sz))
            latin = rpr.find('a:latin', NS)
            if latin is None:
                latin = etree.Element(f'{{{A}}}latin')
                latin.set('typeface', minor)
                pos = next((i for i, c in enumerate(rpr) if c.tag in RPR_AFTER_LATIN), len(rpr))
                rpr.insert(pos, latin)
            elif latin.get('typeface') == '+mn-lt':
                latin.set('typeface', minor)
            elif latin.get('typeface') == '+mj-lt':
                latin.set('typeface', major)
            for tag in ('ea', 'cs'):
                el = rpr.find(f'a:{tag}', NS)
                if el is not None and el.get('typeface', '').startswith('+m'):
                    el.set('typeface', minor)


def replace_text(root, pairs):
    for t in root.iter(f'{{{A}}}t'):
        for old, new in pairs:
            if t.text == old:
                t.text = new


def esc(s):
    return html.escape(s, quote=False)


def run(text, sz, b=False, i=False, color=None):
    attrs = f' lang="en" sz="{sz}"' + (' b="1"' if b else '') + (' i="1"' if i else '')
    fill = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else ''
    return f'<a:r><a:rPr{attrs}>{fill}</a:rPr><a:t>{esc(text)}</a:t></a:r>'


def para(runs, bullet=False, sz=1500, before=0, algn='l', lvl_indent=285750):
    if bullet:
        ppr = (f'<a:pPr marL="{lvl_indent}" indent="-{lvl_indent}" algn="{algn}"><a:spcBef><a:spcPts val="{before}"/></a:spcBef>'
               f'<a:buClr><a:srgbClr val="{ORANGE}"/></a:buClr><a:buSzPts val="{sz}"/><a:buChar char="●"/></a:pPr>')
    else:
        ppr = f'<a:pPr marL="0" indent="0" algn="{algn}"><a:spcBef><a:spcPts val="{before}"/></a:spcBef><a:buNone/></a:pPr>'
    return f'<a:p>{ppr}{runs}</a:p>'


def textbox(id_, name, x, y, cx, cy, paras, anchor='t', fill=None):
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    geom = 'roundRect' if fill else 'rect'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id_}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="{geom}">'
            f'<a:avLst><a:gd name="adj" fmla="val 6000"/></a:avLst></a:prstGeom>{fill_xml}<a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr anchor="{anchor}" lIns="137160" tIns="91425" rIns="137160" bIns="91425" wrap="square"><a:noAutofit/></a:bodyPr>'
            f'<a:lstStyle/>{paras}</p:txBody></p:sp>')


def title_only_sp(text, sz=None):
    rpr = f'<a:rPr lang="en"{" sz=%c%d%c" % (chr(34), sz, chr(34)) if sz else ""}/>'
    return ('<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="460950" y="0"/><a:ext cx="8222100" cy="767700"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            '<p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="91425" lIns="91425" spcFirstLastPara="1" rIns="91425" wrap="square" tIns="91425"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            f'<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr>{run_plain(text, rpr)}<a:endParaRPr/></a:p></p:txBody></p:sp>')


def run_plain(text, rpr):
    return f'<a:r>{rpr}<a:t>{esc(text)}</a:t></a:r>'


def new_slide(shapes):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + shapes + SLDNUM_SP.replace(f' xmlns:p="{P}" xmlns:a="{A}"', '') +
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>').encode('utf-8')


def credit_sp(text):
    return etree.fromstring(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="9902" name="Credit"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="4200000" y="4800000"/><a:ext cx="4250000" cy="250000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr anchor="b" lIns="0" tIns="0" rIns="0" bIns="0" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
        f'<a:p><a:pPr algn="r"><a:buNone/></a:pPr>{run(text, 900, i=True, color=LIGHT_GRAY)}</a:p></p:txBody></p:sp>')


def set_paragraph_text(sp, lines, sz=None):
    """Replace the runs of the first paragraph with `lines` separated by line breaks; drop other paragraphs."""
    tx = sp.find('p:txBody', NS)
    ps = tx.findall('a:p', NS)
    p0 = ps[0]
    for extra in ps[1:]:
        tx.remove(extra)
    for c in list(p0):
        if c.tag != f'{{{A}}}pPr':
            p0.remove(c)
    for i, line in enumerate(lines):
        line_sz = sz
        if isinstance(line, tuple):
            line, line_sz = line
        if i:
            br = etree.SubElement(p0, f'{{{A}}}br'); etree.SubElement(br, f'{{{A}}}rPr').set('lang', 'en')
        r = etree.SubElement(p0, f'{{{A}}}r')
        rpr = etree.SubElement(r, f'{{{A}}}rPr'); rpr.set('lang', 'en')
        if line_sz:
            rpr.set('sz', str(line_sz))
        etree.SubElement(r, f'{{{A}}}t').text = line
    end = etree.SubElement(p0, f'{{{A}}}endParaRPr')
    if sz:
        end.set('sz', str(sz))


# ---------------------------------------------------------------- content
def slide_sciml_definition():
    L = 460950; W = 3950000; G = 320200; Y = 950000; H = 2450000
    left = (para(run('Physics-based modeling', 1800, b=True, color=ORANGE)) +
            para(run('Governing equations from conservation laws: ODEs and PDEs', 1500, color=GRAY), bullet=True, before=800) +
            para(run('Numerical solvers: finite elements, finite differences, material point method', 1500, color=GRAY), bullet=True, before=600) +
            para(run('Accurate and interpretable, but each solve is expensive', 1500, color=GRAY), bullet=True, before=600) +
            para(run('Physics that is unknown or too complex stays out of the model', 1500, color=GRAY), bullet=True, before=600))
    right = (para(run('Data-driven machine learning', 1800, b=True, color=ORANGE)) +
             para(run('Learns a function from input-output examples', 1500, color=GRAY), bullet=True, before=800) +
             para(run('Fast at inference; no equations required', 1500, color=GRAY), bullet=True, before=600) +
             para(run('Needs large labelled datasets', 1500, color=GRAY), bullet=True, before=600) +
             para(run('No guarantee that predictions respect physics or extrapolate', 1500, color=GRAY), bullet=True, before=600))
    bottom = (para(run('Scientific machine learning fuses the two. ', 1600, b=True, color=GRAY) +
                   run('Physical laws enter the loss function (physics-informed neural networks), the architecture (graph networks, neural operators), '
                       'or the training loop (differentiable simulators). Data fills in what the equations leave unknown.', 1600, color=GRAY)))
    shapes = (title_only_sp('What is scientific machine learning?') +
              textbox(10, 'Physics column', L, Y, W, H, left) +
              textbox(11, 'Data column', L + W + G, Y, W, H, right) +
              textbox(12, 'SciML summary', L, Y + H + 150000, 2 * W + G, 1050000, bottom, anchor='ctr', fill='FBEFE6'))
    return new_slide(shapes)


MODULES = [
    'Foundations of machine learning for scientific computing',
    'Mathematical foundations: function spaces, inverse problems',
    'Physics-informed neural networks (PINNs)',
    'Neural ordinary differential equations',
    'Differentiable programming and physics simulation',
    'Operator learning I: DeepONet',
    'Operator learning II: Fourier neural operators, function encoders',
    'Graph neural networks for scientific simulation',
    'Transfer learning and few-shot learning',
    'Transformers in scientific machine learning',
    'Equation discovery: SINDy and symbolic regression',
    'Generative models and uncertainty quantification',
]


def slide_roadmap():
    L = 460950; W = 3950000; G = 320200; Y = 950000; H = 3650000
    def col(items, start):
        out = ''
        for k, m in enumerate(items):
            out += para(run(f'{start + k}.  ', 1500, b=True, color=ORANGE) + run(m, 1500, color=GRAY), before=700 if k else 0)
        return out
    shapes = (title_only_sp('Course roadmap: twelve modules') +
              textbox(10, 'Modules 1-6', L, Y, W, H, col(MODULES[:6], 1)) +
              textbox(11, 'Modules 7-12', L + W + G, Y, W, H, col(MODULES[6:], 7)))
    return new_slide(shapes)


def slide_logistics():
    items = [
        ('Assessment: ', 'homework 30%, exam 30%, final project 40%'),
        ('Homework: ', 'weekly assignments that pair derivations with implementation in Google Colab'),
        ('Final project: ', 'a conference-style paper, presentation, and reproducible code'),
        ('Frameworks: ', 'PyTorch and JAX, with automatic differentiation throughout'),
        ('Prerequisites: ', 'Python, linear algebra, calculus, basic probability; prior ML exposure recommended but not required'),
        ('Notes and notebooks: ', 'kks32-courses.github.io/sciml (GitHub: kks32-courses/sciml)'),
        ('Schedule, office hours, and policies: ', 'see the syllabus on Canvas'),
    ]
    body = ''.join(para(run(a, 1600, b=True, color=GRAY) + run(b, 1600, color=GRAY), bullet=True, before=900 if k else 0)
                   for k, (a, b) in enumerate(items))
    return new_slide(title_only_sp('Course logistics') + textbox(10, 'Logistics', 460950, 950000, 8222100, 3650000, body))


def slide_next_and_credits(ml_range):
    L = 460950; W = 3950000; G = 320200; Y = 950000; H = 3650000
    left = (para(run('Next lecture: multi-layer perceptrons', 1800, b=True, color=ORANGE)) +
            ''.join(para(run(t, 1500, color=GRAY), bullet=True, before=700) for t in [
                'From the perceptron to the multi-layer perceptron; activation functions and ReLU',
                'Universal approximation theorem',
                'Gradient descent and stochastic gradient descent',
                'Automatic differentiation',
                'Regularization',
            ]))
    right = (para(run('Credits', 1800, b=True, color=ORANGE)) +
             ''.join(para(run(t, 1300, color=GRAY), bullet=True, before=700) for t in [
                 f'Slides {ml_range}: adapted from Somdatta Goswami, EN.560.617 Deep Learning for Physical Systems, Johns Hopkins University (2024)',
                 'AI, machine learning, and deep learning diagram: Ehsan Haghighat, SciANN workshop, DesignSafe Academy (2021)',
                 'Lateral spreading study: Durante and Rathje (2021)',
                 'Research demonstrations: Kumar research group, The University of Texas at Austin (geoelements.org)',
             ]))
    return new_slide(title_only_sp('Next lecture and credits') +
                     textbox(10, 'Next lecture', L, Y, W, H, left) +
                     textbox(11, 'Credits', L + W + G, Y, W, H, right))


# ---------------------------------------------------------------- plan
# ('B'|'L'|'W', slide number, options) or ('NEW', builder) or ('DIV', title_lines, body_lines)
PLAN = [
    ('B', 1, {'title_slide': True}),
    # hook: what is possible, and what is missing
    ('W', 3, {}), ('W', 4, {}), ('W', 5, {}), ('W', 7, {}),
    ('B', 28, {'replace': [('Why do we need PINNs?', 'Why do we need scientific machine learning?')]}),
    ('NEW', slide_sciml_definition),
    # machine learning, brief (Goswami)
    ('DIV', ['Machine Learning'], ['A brief introduction', ('Slides adapted from Somdatta Goswami,', 1400), ('Johns Hopkins University (2024)', 1400)]),
    ('B', 3, {}),
    ('L', 10, {}), ('L', 11, {}), ('L', 12, {}), ('L', 16, {}), ('L', 17, {}), ('L', 18, {}),
    ('L', 14, {}), ('L', 15, {}), ('L', 36, {}), ('L', 37, {}),
    ('L', 24, {}), ('L', 27, {}), ('L', 35, {}), ('L', 40, {}), ('L', 41, {}),
    # machine learning in practice
    ('DIV', ['Machine Learning', 'in Practice'], ['Predicting liquefaction-induced lateral spreading']),
    ('B', 4, {}), ('B', 5, {}), ('B', 6, {}), ('B', 8, {}), ('B', 11, {}), ('B', 13, {}), ('B', 14, {}), ('B', 15, {}),
    # scientific machine learning: what is possible
    ('DIV', ['Scientific', 'Machine Learning'], ['What is possible today']),
    ('NEW', slide_roadmap),
    ('B', 35, {}), ('B', 36, {}),
    ('B', 29, {}), ('B', 30, {}), ('B', 33, {}),
    ('B', 37, {}), ('W', 18, {}), ('W', 28, {}),
    ('W', 30, {}), ('B', 46, {}), ('W', 33, {}),
    ('B', 55, {}), ('B', 54, {}), ('B', 57, {}), ('B', 66, {}),
    ('B', 47, {}), ('B', 48, {}),
    ('B', 63, {}), ('B', 61, {}),
    ('W', 43, {}),
    ('B', 64, {}), ('W', 12, {}), ('W', 13, {}), ('B', 70, {}),
    ('W', 41, {}), ('W', 42, {}),
    ('W', 8, {}), ('W', 49, {}), ('W', 52, {}), ('W', 54, {}), ('W', 55, {}), ('W', 56, {}),
    # logistics
    ('NEW', slide_logistics),
    ('B', 2, {}),
    ('NEW', 'credits'),
]

CREDIT_L = 'Adapted from S. Goswami, JHU EN.560.617 (2024)'


def main():
    pk = {k: Pkg(v) for k, v in SRC.items()}
    tgt = Target(pk['B'])
    l_colors = theme_colors(pk['L'], 'ppt/theme/theme1.xml')
    print('Lecture 1 theme colours:', l_colors)
    slide_parts = []
    l_positions = []
    idx = 0
    for item in PLAN:
        idx += 1
        kind = item[0]
        if kind == 'NEW':
            builder = item[1]
            if builder == 'credits':
                rng = f'{min(l_positions)}-{max(l_positions)}'
                xml = slide_next_and_credits(rng)
            else:
                xml = builder()
            slide_parts.append(tgt.add_slide_xml(idx, xml, LAYOUT_TITLE_ONLY))
            print(f'{idx:3d}  NEW   {text_of(shapes_with_ph(etree.fromstring(xml), ("title",))[0])}')
            continue
        if kind == 'DIV':
            root = etree.fromstring(pk['B'].read(pk['B'].slide(16)))
            set_paragraph_text(shapes_with_ph(root, ('title',))[0], item[1])
            set_paragraph_text(shapes_with_ph(root, ('body',))[0], item[2], sz=2800)
            ensure_sldnum(root)
            slide_parts.append(tgt.add_slide_xml(idx, tostr(root), LAYOUT_SECTION))
            print(f'{idx:3d}  DIV   {" ".join(item[1])} | {" ".join(x[0] if isinstance(x, tuple) else x for x in item[2])}')
            continue
        key, n, opts = item
        pkg = pk[key]

        def transform(root, key=key, opts=opts):
            if key == 'L':
                scale(root, 0.75)
                fix_insets(root, 0.75)
                strip_bg(root)
                drop_ph(root, ('dt', 'ftr'))
                remove_bare_numbers(root)
                resolve_scheme_colors(root, l_colors)
                fix_default_text(root, sz=1350)
                fix_title(root, inherit=True)
            if opts.get('replace'):
                replace_text(root, opts['replace'])
            if opts.get('title_slide'):
                replace_text(root, [('Krishna Kumar, The University of Texas at Austin',
                                     'Lecture 1: Introduction  ·  Krishna Kumar, The University of Texas at Austin')])
            ensure_sldnum(root)

        layout = None if key == 'B' else LAYOUT_TITLE_ONLY
        part = tgt.import_slide(pkg, key, n, idx, layout=layout, transform=transform)
        slide_parts.append(part)
        if key == 'L':
            l_positions.append(idx)
        title = ''
        root = etree.fromstring(tgt.parts[part])
        ts = shapes_with_ph(root, ('title', 'ctrTitle'))
        if ts:
            title = text_of(ts[0]).strip()
        print(f'{idx:3d}  {key}{n:<4d} {title[:70]}')

    tgt.finalize(slide_parts)
    problems = tgt.check()
    if problems:
        print('PROBLEMS:'); print('\n'.join(problems)); sys.exit(1)
    tgt.write(OUT)
    size = sum(len(v) for v in tgt.parts.values())
    print(f'\nwrote {OUT}: {len(slide_parts)} slides, {size/1e6:.0f} MB uncompressed')


if __name__ == '__main__':
    main()
