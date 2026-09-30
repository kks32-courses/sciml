#!/usr/bin/env python3
"""Post-edit fixes for lecture-01-introduction.pptx (operates on the PowerPoint-saved deck).

1. One font family (Roboto, the template's title font) on every run; math runs keep Cambria Math.
2. Goswami's orphan body placeholders (idx 4294967295) inherit white text from the master:
   give their runs and bullets explicit black.
3. Short single-word labels and ellipse shapes: no wrapping (Start, Stop, Validation ...).
4. Slide 2 title shortened to one line; credits slide range recomputed.
5. Speaker notes added to the four new content slides.
"""
import posixpath, re, sys, zipfile
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CTNS = 'http://schemas.openxmlformats.org/package/2006/content-types'
NS = {'a': A, 'p': P, 'r': R}
FONT = 'Roboto'
BLACK = '000000'
CT_NOTES = 'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'
RT_NOTES = R + '/notesSlide'

L_TITLES = {'Artificial Intelligence', 'Machine Learning', 'Types of Learning Tasks',
            'Task 1: Find if a number is odd or even', 'Supervised Learning == Function Approximation',
            'Two types of Supervised Learning', 'Deep Learning', 'How supervised learning Works?',
            'Labelled Datasets', 'Unsupervised Learning', 'Unsupervised Learning- K-means clustering',
            'Compare the Learning Methods', 'The Perceptron', 'Predicting with a Perceptron'}

NOTES = {
    'What is scientific machine learning?': [
        'Two ways to model a physical system. Physics-based: write the governing equations and solve them numerically. Accurate when the physics is known, but every solve is expensive and unknown physics is left out.',
        'Data-driven: learn the input-to-output map from examples. Fast at inference, but it needs a lot of data and nothing forces the prediction to obey physics. The lateral spreading example later in this lecture shows a model learning a physically wrong trend.',
        'Scientific machine learning combines the two. Physics enters the loss function (physics-informed neural networks, module 3), the architecture (graph networks and neural operators, modules 6 to 8), or the training loop (differentiable simulators, module 5). Data fills in what the equations leave unknown.',
    ],
    'Course roadmap: twelve modules': [
        'Modules 1 and 2 are foundations: neural networks, optimization, automatic differentiation, function spaces and inverse problems.',
        'Modules 3 to 8 are the core solvers: physics-informed neural networks, neural ODEs, differentiable simulators, DeepONet, Fourier neural operators and function encoders, graph network simulators.',
        'Modules 9 to 12 extend them: transfer and few-shot learning, transformers, equation discovery, generative models and uncertainty quantification.',
        'The rest of this lecture shows one result from most of these modules, so students see where the course is going before the mathematics starts.',
    ],
    'Course logistics': [
        'Assessment: 30 percent weekly homework, 30 percent exam, 40 percent final project.',
        'Each homework pairs a derivation with an implementation in Google Colab. The final project is a conference-style paper with a presentation and reproducible code.',
        'Prerequisites: Python, linear algebra, calculus and basic probability. Prior machine learning helps but is not required.',
        'Schedule, office hours and all policies are in the syllabus on Canvas. Notes and notebooks are on the course site.',
    ],
    'Next lecture and credits': [
        'Next lecture builds the multi-layer perceptron from the perceptron, introduces ReLU, states the universal approximation theorem, and covers gradient descent, automatic differentiation and regularization.',
        'Credits: the machine learning slides are adapted from Somdatta Goswami (Johns Hopkins, EN.560.617, 2024). The AI, ML and DL diagram is from Ehsan Haghighat. The lateral spreading study is Durante and Rathje (2021). The remaining demonstrations are from the Kumar research group.',
    ],
}

RPR_AFTER_LATIN = {f'{{{A}}}{t}' for t in ('ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')}
PPR_BEFORE_BUCLR = {f'{{{A}}}{t}' for t in ('lnSpc', 'spcBef', 'spcAft')}


def tostr(el):
    return etree.tostring(el, xml_declaration=True, encoding='UTF-8', standalone=True)


def rels_path(part):
    d, b = posixpath.split(part)
    return f'{d}/_rels/{b}.rels'


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(f'{{{A}}}t'))


def in_math(el):
    p = el.getparent()
    while p is not None:
        if p.tag.startswith(f'{{{M}}}'):
            return True
        p = p.getparent()
    return False


def set_font(el):
    for k in ('panose', 'pitchFamily', 'charset'):
        el.attrib.pop(k, None)
    el.set('typeface', FONT)


def fix_fonts(root):
    changed = 0
    for r in list(root.iter(f'{{{A}}}r', f'{{{A}}}fld', f'{{{A}}}br')):
        if in_math(r):
            continue
        if r.find('a:rPr', NS) is None:
            rpr = etree.Element(f'{{{A}}}rPr'); rpr.set('lang', 'en')
            r.insert(0, rpr)
    for rpr in root.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr', f'{{{A}}}defRPr'):
        if in_math(rpr):
            continue
        latin = rpr.find('a:latin', NS)
        if latin is not None and latin.get('typeface') == 'Cambria Math':
            continue
        if latin is None:
            latin = etree.Element(f'{{{A}}}latin')
            pos = next((i for i, c in enumerate(rpr) if c.tag in RPR_AFTER_LATIN), len(rpr))
            rpr.insert(pos, latin)
        if latin.get('typeface') != FONT:
            changed += 1
        set_font(latin)
        for tag in ('ea', 'cs'):
            el = rpr.find(f'a:{tag}', NS)
            if el is not None and el.get('typeface') != 'Cambria Math':
                set_font(el)
    return changed


def fix_orphan_placeholders(root):
    n = 0
    for sp in root.iter(f'{{{P}}}sp'):
        ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is None or ph.get('idx') != '4294967295':
            continue
        n += 1
        for rpr in sp.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr'):
            sf = rpr.find('a:solidFill', NS)
            if sf is None:
                sf = etree.Element(f'{{{A}}}solidFill')
                c = etree.SubElement(sf, f'{{{A}}}srgbClr'); c.set('val', BLACK)
                ln = rpr.find('a:ln', NS)
                rpr.insert(rpr.index(ln) + 1 if ln is not None else 0, sf)
            elif etree.QName(sf[0]).localname == 'schemeClr':
                sf.remove(sf[0])
                c = etree.SubElement(sf, f'{{{A}}}srgbClr'); c.set('val', BLACK)
        for p in sp.iter(f'{{{A}}}p'):
            ppr = p.find('a:pPr', NS)
            if ppr is None:
                ppr = etree.Element(f'{{{A}}}pPr'); p.insert(0, ppr)
            if ppr.find('a:buNone', NS) is not None or ppr.find('a:buClr', NS) is not None:
                continue
            bu = etree.Element(f'{{{A}}}buClr')
            c = etree.SubElement(bu, f'{{{A}}}srgbClr'); c.set('val', BLACK)
            idx = 0
            for i, ch in enumerate(ppr):
                if ch.tag in PPR_BEFORE_BUCLR:
                    idx = i + 1
            ppr.insert(idx, bu)
    return n


def fix_wrap(root):
    n = 0
    for sp in root.iter(f'{{{P}}}sp'):
        if sp.find('p:nvSpPr/p:nvPr/p:ph', NS) is not None:
            continue
        txt = text_of(sp).strip()
        geom = sp.find('p:spPr/a:prstGeom', NS)
        single = bool(txt) and ' ' not in txt and len(txt) <= 14
        if single or (geom is not None and geom.get('prst') == 'ellipse' and txt):
            bp = sp.find('p:txBody/a:bodyPr', NS)
            if bp is not None and bp.get('wrap') != 'none':
                bp.set('wrap', 'none'); n += 1
    return n


def sp_with_text(root, needle, startswith=False):
    for sp in root.iter(f'{{{P}}}sp'):
        t = text_of(sp).strip()
        if (t.startswith(needle) if startswith else t == needle):
            yield sp


def set_wrap_none(sp):
    bp = sp.find('p:txBody/a:bodyPr', NS)
    if bp is not None:
        bp.set('wrap', 'none')


def set_sz(sp, sz, only=None):
    for rpr in sp.iter(f'{{{A}}}rPr', f'{{{A}}}endParaRPr'):
        if only is None or rpr.get('sz') == only:
            rpr.set('sz', str(sz))


def para_xml(runs):
    """runs: list of (text, bold, italic)."""
    out = '<a:p xmlns:a="%s"><a:pPr marL="0" indent="0"><a:spcBef><a:spcPts val="600"/></a:spcBef><a:buNone/></a:pPr>' % A
    for t, b, i in runs:
        attrs = ' lang="en-US" sz="1600"' + (' b="1"' if b else '') + (' i="1"' if i else '')
        out += f'<a:r><a:rPr{attrs}><a:solidFill><a:srgbClr val="000000"/></a:solidFill></a:rPr><a:t>{t}</a:t></a:r>'
    return out + '</a:p>'


def tweak(root, title):
    log = []
    if title == 'The Perceptron':
        for sp in root.iter(f'{{{P}}}sp'):
            ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
            if ph is not None and ph.get('idx') == '4294967295':
                off = sp.find('p:spPr/a:xfrm/a:off', NS)
                off.set('y', str(int(off.get('y')) + 300000)); log.append('label moved down')
    if title == 'Predicting with a Perceptron':
        for sp in sp_with_text(root, 'Multiply each input', startswith=True):
            set_sz(sp, 1500); log.append('multiply text 15pt')
    if title == 'Labelled Datasets':
        for lab in ('Train', 'Validation', 'Test'):
            for sp in sp_with_text(root, lab):
                set_sz(sp, 1400); set_wrap_none(sp); log.append(f'{lab} 14pt')
    if title == 'Two types of Supervised Learning':
        for sp in root.iter(f'{{{P}}}sp'):
            ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
            if ph is not None and ph.get('idx') == '4294967295':
                set_sz(sp, 1600, only='1800'); log.append('body 16pt')
    if title == 'Task 1: Find if a number is odd or even':
        for sp in root.iter(f'{{{P}}}sp'):
            g = sp.find('p:spPr/a:prstGeom', NS)
            if g is not None and g.get('prst') == 'diamond':
                set_wrap_none(sp); log.append('diamond nowrap')
    if title == 'Recommended Books':
        for sp in sp_with_text(root, 'https://www.deeplearningbook.org', startswith=True):
            set_wrap_none(sp); log.append('url nowrap')
    if title == 'System ID: Inverse maps are ill posed':
        for sp in sp_with_text(root, 'ill-conditioning'):
            set_wrap_none(sp); log.append('label nowrap')
    if title == 'Supervised Learning == Function Approximation':
        tree = root.find('p:cSld/p:spTree', NS)
        for pic in list(tree.iter(f'{{{P}}}pic')):
            off = pic.find('p:spPr/a:xfrm/a:off', NS)
            if off is not None and int(off.get('y')) > 3500000:
                pic.getparent().remove(pic); log.append('equation image removed')
        for sp in list(sp_with_text(root, 'Testing (inference)', startswith=True)):
            sp.getparent().remove(sp); log.append('old testing box removed')
        for sp in sp_with_text(root, 'Training (learning)', startswith=True):
            tx = sp.find('p:txBody', NS)
            for p in tx.findall('a:p', NS):
                tx.remove(p)
            tx.append(etree.fromstring(para_xml([
                ('Training (learning): ', True, False),
                ('given a dataset D = {(x\u2081, y\u2081), \u2026, (x\u2099, y\u2099)}, find a prediction function y = f\u0303(x) that approximates f(x) = E[Y | X = x].', False, False)])))
            tx.append(etree.fromstring(para_xml([
                ('Testing (inference): ', True, False),
                ('apply f\u0303(x) to a new test example.', False, False)])))
            ext = sp.find('p:spPr/a:xfrm/a:ext', NS); ext.set('cy', '1200000')
            log.append('equations rewritten as text')
    return log


def title_sp(root):
    for sp in root.iter(f'{{{P}}}sp'):
        ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is not None and ph.get('type') in ('title', 'ctrTitle'):
            return sp
    return None


def set_text_runs(sp, new_text):
    """Keep the first run of the first paragraph, drop the rest, set its text."""
    tx = sp.find('p:txBody', NS)
    ps = tx.findall('a:p', NS)
    for extra in ps[1:]:
        tx.remove(extra)
    p0 = ps[0]
    runs = p0.findall('a:r', NS)
    for extra in list(p0):
        if extra.tag in (f'{{{A}}}r', f'{{{A}}}br', f'{{{A}}}fld') and extra is not runs[0]:
            p0.remove(extra)
    runs[0].find('a:t', NS).text = new_text


def main():
    z = zipfile.ZipFile(SRC)
    parts = {n: z.read(n) for n in z.namelist()}
    pres = etree.fromstring(parts['ppt/presentation.xml'])
    prels = etree.fromstring(parts['ppt/_rels/presentation.xml.rels'])
    rid2t = {r.get('Id'): r.get('Target') for r in prels}
    order = ['ppt/' + rid2t[s.get(f'{{{R}}}id')] for s in pres.find('p:sldIdLst', NS)]
    ct = etree.fromstring(parts['[Content_Types].xml'])
    notes_nums = [int(m.group(1)) for n in parts for m in [re.match(r'ppt/notesSlides/notesSlide(\d+)\.xml$', n)] if m]
    next_notes = max(notes_nums) + 1
    notes_tmpl = parts['ppt/notesSlides/notesSlide1.xml']

    l_slides = []
    roots = {}
    for i, part in enumerate(order, 1):
        root = etree.fromstring(parts[part])
        rels = etree.fromstring(parts[rels_path(part)])
        layout = next(r.get('Target') for r in rels if r.get('Type').endswith('/slideLayout'))
        ts = title_sp(root)
        title = text_of(ts).strip() if ts is not None else ''
        is_l = title in L_TITLES and layout.endswith('slideLayout17.xml')
        if is_l:
            l_slides.append(i)
        roots[part] = (root, rels, title, is_l, i)

    l_range = f'{min(l_slides)}-{max(l_slides)}'
    print('Goswami slides detected:', l_slides, '->', l_range)

    for part, (root, rels, title, is_l, i) in roots.items():
        log = tweak(root, title)
        if is_l:
            log.append(f'orphans={fix_orphan_placeholders(root)}')
            log.append(f'nowrap={fix_wrap(root)}')
        log.append(f'fonts={fix_fonts(root)}')
        if title == 'Why do we need scientific machine learning?':
            set_text_runs(title_sp(root), 'Why scientific machine learning?')
            log.append('title shortened')
        if title == 'Next lecture and credits':
            for t in root.iter(f'{{{A}}}t'):
                if t.text and t.text.startswith('Slides 10-24'):
                    t.text = t.text.replace('Slides 10-24', f'Slides {l_range}'); log.append('credits range')
        if title in NOTES and not any(r.get('Type') == RT_NOTES for r in rels):
            nroot = etree.fromstring(notes_tmpl)
            body = next(sp for sp in nroot.iter(f'{{{P}}}sp')
                        if (ph := sp.find('p:nvSpPr/p:nvPr/p:ph', NS)) is not None and ph.get('type') == 'body')
            tx = body.find('p:txBody', NS)
            for p in tx.findall('a:p', NS):
                tx.remove(p)
            for para in NOTES[title]:
                p = etree.SubElement(tx, f'{{{A}}}p')
                ppr = etree.SubElement(p, f'{{{A}}}pPr'); ppr.set('marL', '0'); ppr.set('indent', '0')
                etree.SubElement(ppr, f'{{{A}}}buNone')
                r = etree.SubElement(p, f'{{{A}}}r')
                etree.SubElement(r, f'{{{A}}}rPr').set('lang', 'en')
                etree.SubElement(r, f'{{{A}}}t').text = para
            nname = f'ppt/notesSlides/notesSlide{next_notes}.xml'; next_notes += 1
            parts[nname] = tostr(nroot)
            nrels = etree.Element(f'{{{PKG}}}Relationships', nsmap={None: PKG})
            e = etree.SubElement(nrels, f'{{{PKG}}}Relationship'); e.set('Id', 'rId1'); e.set('Type', R + '/notesMaster'); e.set('Target', '../notesMasters/notesMaster1.xml')
            e = etree.SubElement(nrels, f'{{{PKG}}}Relationship'); e.set('Id', 'rId2'); e.set('Type', R + '/slide'); e.set('Target', '../slides/' + posixpath.basename(part))
            parts[rels_path(nname)] = tostr(nrels)
            o = etree.SubElement(ct, f'{{{CTNS}}}Override'); o.set('PartName', '/' + nname); o.set('ContentType', CT_NOTES)
            used = {int(r.get('Id')[3:]) for r in rels if r.get('Id', '').startswith('rId') and r.get('Id')[3:].isdigit()}
            e = etree.SubElement(rels, f'{{{PKG}}}Relationship'); e.set('Id', f'rId{max(used) + 1}'); e.set('Type', RT_NOTES); e.set('Target', '../notesSlides/' + posixpath.basename(nname))
            log.append('notes added')
        parts[part] = tostr(root)
        parts[rels_path(part)] = tostr(rels)
        print(f'{i:3d} {"L" if is_l else " "} {title[:44]:46s} {" ".join(log)}')

    parts['[Content_Types].xml'] = tostr(ct)
    with zipfile.ZipFile(OUT, 'w') as zo:
        names = ['[Content_Types].xml'] + [n for n in parts if n != '[Content_Types].xml']
        for n in names:
            stored = n.startswith(('ppt/media/', 'ppt/fonts/', 'ppt/embeddings/'))
            zo.writestr(n, parts[n], compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
