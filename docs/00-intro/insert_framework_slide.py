#!/usr/bin/env python3
"""Insert 'The organizing framework' slide after 'What is scientific machine learning?'."""
import html, posixpath, re, sys, zipfile
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CTNS = 'http://schemas.openxmlformats.org/package/2006/content-types'
NS = {'a': A, 'p': P, 'r': R}
CT_SLIDE = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
CT_NOTES = 'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'
LAYOUT = '../slideLayouts/slideLayout17.xml'
AFTER_TITLE = 'What is scientific machine learning?'
ORANGE, GRAY, RULE, TINT = 'BF5700', '424242', '424242', 'FBEFE6'
MATH_FONT = 'Cambria Math'

L_TITLES = {'Artificial Intelligence', 'Machine Learning', 'Types of Learning Tasks',
            'Task 1: Find if a number is odd or even', 'Supervised Learning == Function Approximation',
            'Two types of Supervised Learning', 'Deep Learning', 'How supervised learning Works?',
            'Labelled Datasets', 'Unsupervised Learning', 'Unsupervised Learning- K-means clustering',
            'Compare the Learning Methods', 'The Perceptron', 'Predicting with a Perceptron'}


def esc(s):
    return html.escape(s, quote=False)


def run(text, sz, kind='t', color=GRAY):
    """kind: t text, b bold text, m math (Cambria Math italic), mb math bold upright."""
    b = ' b="1"' if kind in ('b', 'mb') else ''
    i = ' i="1"' if kind == 'm' else ''
    font = MATH_FONT if kind in ('m', 'mb') else 'Roboto'
    return (f'<a:r><a:rPr lang="en-US" sz="{sz}"{b}{i}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{font}"/></a:rPr><a:t>{esc(text)}</a:t></a:r>')


def para(runs_xml, algn='l', before=0):
    return f'<a:p><a:pPr algn="{algn}"><a:spcBef><a:spcPts val="{before}"/></a:spcBef><a:buNone/></a:pPr>{runs_xml}</a:p>'


def textbox(id_, name, x, y, cx, cy, paras, anchor='t'):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id_}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr anchor="{anchor}" lIns="91440" tIns="45720" rIns="91440" bIns="45720" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>{paras}</p:txBody></p:sp>')


def title_sp(text):
    return ('<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="460950" y="0"/><a:ext cx="8222100" cy="767700"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            '<p:txBody><a:bodyPr anchor="b" lIns="91425" tIns="91425" rIns="91425" bIns="91425" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            f'<a:p><a:pPr algn="l"><a:buNone/></a:pPr><a:r><a:rPr lang="en"><a:latin typeface="Roboto"/></a:rPr><a:t>{esc(text)}</a:t></a:r></a:p></p:txBody></p:sp>')


SLDNUM = ('<p:sp><p:nvSpPr><p:cNvPr id="9901" name="Slide Number"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph idx="12" type="sldNum"/></p:nvPr></p:nvSpPr>'
          '<p:spPr><a:xfrm><a:off x="8523541" y="4695623"/><a:ext cx="548700" cy="393600"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
          '<p:txBody><a:bodyPr anchor="ctr" lIns="91425" tIns="91425" rIns="91425" bIns="91425" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
          '<a:p><a:pPr algn="r"><a:buNone/></a:pPr><a:fld id="{00000000-1234-1234-1234-123412341234}" type="slidenum"><a:rPr lang="en"><a:latin typeface="Roboto"/></a:rPr><a:t>‹#›</a:t></a:fld></a:p></p:txBody></p:sp>')


def cell(runs_xml, header=False, last=False, first_col=False):
    ln_none = '<a:noFill/>'
    rule = f'<a:solidFill><a:srgbClr val="{RULE}"/></a:solidFill>'
    lnT = f'<a:lnT w="12700">{rule}</a:lnT>' if header else '<a:lnT><a:noFill/></a:lnT>'
    lnB = f'<a:lnB w="12700">{rule}</a:lnB>' if (header or last) else '<a:lnB><a:noFill/></a:lnB>'
    fill = f'<a:solidFill><a:srgbClr val="{TINT}"/></a:solidFill>' if header else '<a:noFill/>'
    return (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="l"><a:buNone/></a:pPr>{runs_xml}</a:p></a:txBody>'
            f'<a:tcPr marL="91440" marR="91440" marT="45720" marB="45720" anchor="ctr">'
            f'<a:lnL>{ln_none}</a:lnL><a:lnR>{ln_none}</a:lnR>{lnT}{lnB}{fill}</a:tcPr></a:tc>')


SZ = 1400
ROWS = [
    # mode, know runs, want runs
    ('Solve', [('ℒ', 'mb'), (', ', 't'), ('f', 'm'), (', domain, boundary conditions', 't')], [('Solution ', 't'), ('u', 'm')]),
    ('Learn operator', [('ℒ', 'mb'), ('; many inputs ', 't'), ('f', 'm')], [('Fast map ', 't'), ('𝒢', 'mb'), (': ', 't'), ('f', 'm'), (' ↦ ', 'm'), ('u', 'm')]),
    ('Invert', [('ℒ', 'mb'), (' up to parameters; partial data', 't')], [('Unknown parameters or fields', 't')]),
    ('Discover', [('Trajectories of ', 't'), ('u', 'm'), ('; ', 't'), ('ℒ', 'mb'), (' unknown', 't')], [('Governing law ', 't'), ('ℒ', 'mb')]),
    ('Control', [('ℒ', 'mb'), (' (or learned ', 't'), ('𝒢', 'mb'), ('); cost', 't')], [('Optimal policy', 't')]),
]


def table_xml():
    x, y = 460950, 1420000
    widths = [1650000, 3600000, 2972100]
    rh, hh = 320000, 300000
    rows = ''
    hdr = [run(t, SZ, 'b', ORANGE) for t in ('Mode', 'Know', 'Want')]
    rows += f'<a:tr h="{hh}">' + ''.join(cell(h, header=True) for h in hdr) + '</a:tr>'
    for k, (mode, know, want) in enumerate(ROWS):
        last = k == len(ROWS) - 1
        rows += (f'<a:tr h="{rh}">' + cell(run(mode, SZ, 'b'), last=last, first_col=True)
                 + cell(''.join(run(t, SZ, kind) for t, kind in know), last=last)
                 + cell(''.join(run(t, SZ, kind) for t, kind in want), last=last) + '</a:tr>')
    cy = hh + rh * len(ROWS)
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="20" name="Modes table"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{sum(widths)}" cy="{cy}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl><a:tblPr firstRow="1"/>'
            f'<a:tblGrid>{"".join(f"<a:gridCol w=%c%d%c/>" % (chr(34), w, chr(34)) for w in widths)}</a:tblGrid>{rows}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'), y + cy


def slide_xml():
    intro = para(run('Consider a physical system governed by ', 1500) + run('ℒ', 1500, 'mb') + run('u', 1500, 'm') + run(' = ', 1500, 'm') + run('f', 1500, 'm')
                 + run('. This one equation generates every computational problem in the course, depending on what you know and what you want.', 1500))
    tbl, tbl_bottom = table_xml()
    closing = para(run('These are not separate disciplines. They are projections of the same underlying system, connected by precise mathematical relationships. The course follows this dependency graph:', 1400))
    chain = para(run('Discover ', 1800) + run('ℒ', 1800, 'mb') + run('   →   Solve ', 1800) + run('ℒ', 1800, 'mb') + run('u', 1800, 'm') + run(' = ', 1800, 'm') + run('f', 1800, 'm')
                 + run('   →   Learn ', 1800) + run('𝒢', 1800, 'mb') + run(' = ', 1800, 'm') + run('ℒ', 1800, 'mb') + run('⁻¹', 1800, 'mb')
                 + run('   →   Control via ', 1800) + run('𝒢', 1800, 'mb'), algn='ctr')
    shapes = (title_sp('The organizing framework')
              + textbox(10, 'Intro', 460950, 850000, 8222100, 560000, intro)
              + tbl
              + textbox(11, 'Closing', 460950, tbl_bottom + 90000, 8222100, 560000, closing)
              + textbox(12, 'Dependency chain', 460950, tbl_bottom + 680000, 8222100, 420000, chain, anchor='ctr')
              + SLDNUM)
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + shapes + '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>').encode('utf-8')


NOTES = [
    'One equation, L u = f, organizes the whole course. L is the governing operator, f the forcing, u the state. Which quantities are known and which are wanted picks the mode.',
    'Solve: L, f, domain and boundary conditions are known and we want u. Physics-informed neural networks and neural ODEs live here.',
    'Learn operator: we want a fast map G from any forcing f to the solution u. DeepONet, Fourier neural operators, function encoders and graph network simulators live here.',
    'Invert: L is known up to parameters and only partial data is available. Inverse problems, differentiable simulators and uncertainty quantification live here.',
    'Discover: only trajectories of u are known and the law itself is wanted. SINDy and symbolic regression live here.',
    'Control: given L, or a learned G, and a cost, we want the optimal policy. The world-model slides at the end of this lecture show this mode.',
    'The chain Discover, Solve, Learn, Control is the dependency order: each mode uses the output of the previous one.',
]


def tostr(el):
    return etree.tostring(el, xml_declaration=True, encoding='UTF-8', standalone=True)


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(f'{{{A}}}t'))


def main():
    z = zipfile.ZipFile(SRC)
    parts = {n: z.read(n) for n in z.namelist()}
    pres = etree.fromstring(parts['ppt/presentation.xml'])
    prels = etree.fromstring(parts['ppt/_rels/presentation.xml.rels'])
    ct = etree.fromstring(parts['[Content_Types].xml'])
    rid2t = {r.get('Id'): r.get('Target') for r in prels}
    lst = pres.find('p:sldIdLst', NS)
    sld_ids = list(lst)
    order = ['ppt/' + rid2t[s.get(f'{{{R}}}id')] for s in sld_ids]

    def title_of(part):
        root = etree.fromstring(parts[part])
        for sp in root.iter(f'{{{P}}}sp'):
            ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
            if ph is not None and ph.get('type') in ('title', 'ctrTitle'):
                return text_of(sp).strip()
        return ''

    titles = [title_of(p) for p in order]
    pos = titles.index(AFTER_TITLE) + 1
    print('inserting after slide', pos, titles[pos - 1])

    n = max(int(m.group(1)) for k in parts for m in [re.match(r'ppt/slides/slide(\d+)\.xml$', k)] if m) + 1
    name = f'ppt/slides/slide{n}.xml'
    parts[name] = slide_xml()
    rels = etree.Element(f'{{{PKG}}}Relationships', nsmap={None: PKG})
    e = etree.SubElement(rels, f'{{{PKG}}}Relationship'); e.set('Id', 'rId1'); e.set('Type', R + '/slideLayout'); e.set('Target', LAYOUT)
    # notes
    nn = max(int(m.group(1)) for k in parts for m in [re.match(r'ppt/notesSlides/notesSlide(\d+)\.xml$', k)] if m) + 1
    nname = f'ppt/notesSlides/notesSlide{nn}.xml'
    nroot = etree.fromstring(parts['ppt/notesSlides/notesSlide1.xml'])
    body = next(sp for sp in nroot.iter(f'{{{P}}}sp') if (ph := sp.find('p:nvSpPr/p:nvPr/p:ph', NS)) is not None and ph.get('type') == 'body')
    tx = body.find('p:txBody', NS)
    for p in tx.findall('a:p', NS):
        tx.remove(p)
    for t in NOTES:
        p = etree.SubElement(tx, f'{{{A}}}p'); ppr = etree.SubElement(p, f'{{{A}}}pPr'); ppr.set('marL', '0'); ppr.set('indent', '0'); etree.SubElement(ppr, f'{{{A}}}buNone')
        r = etree.SubElement(p, f'{{{A}}}r'); etree.SubElement(r, f'{{{A}}}rPr').set('lang', 'en'); etree.SubElement(r, f'{{{A}}}t').text = t
    parts[nname] = tostr(nroot)
    nrels = etree.Element(f'{{{PKG}}}Relationships', nsmap={None: PKG})
    e = etree.SubElement(nrels, f'{{{PKG}}}Relationship'); e.set('Id', 'rId1'); e.set('Type', R + '/notesMaster'); e.set('Target', '../notesMasters/notesMaster1.xml')
    e = etree.SubElement(nrels, f'{{{PKG}}}Relationship'); e.set('Id', 'rId2'); e.set('Type', R + '/slide'); e.set('Target', '../slides/' + posixpath.basename(name))
    parts[f'ppt/notesSlides/_rels/notesSlide{nn}.xml.rels'] = tostr(nrels)
    e = etree.SubElement(rels, f'{{{PKG}}}Relationship'); e.set('Id', 'rId2'); e.set('Type', R + '/notesSlide'); e.set('Target', '../notesSlides/' + posixpath.basename(nname))
    parts[f'ppt/slides/_rels/slide{n}.xml.rels'] = tostr(rels)
    for pn, c in ((name, CT_SLIDE), (nname, CT_NOTES)):
        o = etree.SubElement(ct, f'{{{CTNS}}}Override'); o.set('PartName', '/' + pn); o.set('ContentType', c)
    # register in presentation
    new_id = max(int(s.get('id')) for s in sld_ids) + 1
    new_rid = 'rId' + str(max(int(r.get('Id')[3:]) for r in prels if r.get('Id')[3:].isdigit()) + 1)
    sid = etree.Element(f'{{{P}}}sldId'); sid.set('id', str(new_id)); sid.set(f'{{{R}}}id', new_rid)
    lst.insert(pos, sid)
    rel = etree.SubElement(prels, f'{{{PKG}}}Relationship'); rel.set('Id', new_rid); rel.set('Type', R + '/slide'); rel.set('Target', 'slides/' + posixpath.basename(name))
    parts['ppt/presentation.xml'] = tostr(pres)
    parts['ppt/_rels/presentation.xml.rels'] = tostr(prels)
    parts['[Content_Types].xml'] = tostr(ct)
    # credits range: Goswami slides shift by one
    order.insert(pos, name); titles.insert(pos, 'The organizing framework')
    def is_goswami(part, t):
        rels_xml = parts.get(f'ppt/slides/_rels/{posixpath.basename(part)}.rels', b'')
        return t in L_TITLES and b'slideLayout17.xml' in rels_xml
    l_idx = [i + 1 for i, (part, t) in enumerate(zip(order, titles)) if is_goswami(part, t)]
    rng = f'{min(l_idx)}-{max(l_idx)}'
    for part, t in zip(order, titles):
        if t == 'Next lecture and credits':
            root = etree.fromstring(parts[part]); changed = False
            for tt in root.iter(f'{{{A}}}t'):
                if tt.text and re.match(r'Slides \d+-\d+', tt.text):
                    tt.text = re.sub(r'Slides \d+-\d+', f'Slides {rng}', tt.text); changed = True
            parts[part] = tostr(root); print('credits range ->', rng, changed)
    with zipfile.ZipFile(OUT, 'w') as zo:
        for k in ['[Content_Types].xml'] + [k for k in parts if k != '[Content_Types].xml']:
            stored = k.startswith(('ppt/media/', 'ppt/fonts/', 'ppt/embeddings/'))
            zo.writestr(k, parts[k], compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)
    print('wrote', OUT, 'slides:', len(order))


if __name__ == '__main__':
    main()
