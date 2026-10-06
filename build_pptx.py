"""Build Moen_ICCFSS_2026_rack_standards.pptx from template.pptx with the same content as deck/slides.md.
    python3 build_pptx.py
Figures are read from deck/data (crops of the MH16.1 figures and the curves from deck/data/make_figs.jl).
Layouts used: Title Slide, Title and Content, Two Content, Title Only. Fonts follow the template theme (Aptos); only
sizes are set here. Equations are plain text in shaded boxes."""
import copy, os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "deck", "data")
OUT = os.path.join(HERE, "Moen_ICCFSS_2026_rack_standards.pptx")
ACCENT = RGBColor(0x15, 0x60, 0x82); ORANGE = RGBColor(0xE9, 0x71, 0x32); INK = RGBColor(0x0E, 0x28, 0x41); MUTED = RGBColor(0x4B, 0x56, 0x66)

prs = Presentation(os.path.join(HERE, "template.pptx"))
# drop the two sample slides of the template
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId); sldIdLst.remove(sldId)
L = {l.name: l for l in prs.slide_layouts}

def ph(slide, idx):
    for p in slide.placeholders:
        if p.placeholder_format.idx == idx: return p
    return None

def set_title(slide, text, size=32):
    t = slide.shapes.title; t.text = text
    for p in t.text_frame.paragraphs:
        for r in p.runs: r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = INK

def runs(par, text, size, bold=False, color=None, mono=False):
    """text with **bold** segments, `code` segments, and _{sub} / ^{super} scripts"""
    import re
    for seg in re.split(r"(\*\*.+?\*\*|`.+?`)", text):
        if not seg: continue
        b = bold
        if seg.startswith("**"): seg = seg[2:-2]; b = True
        elif seg.startswith("`"):
            r = par.add_run(); r.text = seg[1:-1]; r.font.name = "Consolas"; r.font.size = Pt(size)
            if color is not None: r.font.color.rgb = color
            continue
        for part in re.split(r"(_\{.+?\}|\^\{.+?\})", seg):
            if not part: continue
            r = par.add_run()
            if part[:2] in ("_{", "^{"):
                r.text = part[2:-1]; r.font._rPr.set("baseline", "-25000" if part[0] == "_" else "30000")
            else: r.text = part
            r.font.bold = b; r.font.size = Pt(size)
            if color is not None: r.font.color.rgb = color
            if mono: r.font.name = "Consolas"

def bullets(tf, items, size=18, sub=15, first=True):
    """items: list of str or (str, level)"""
    tf.word_wrap = True
    for k, it in enumerate(items):
        text, lvl = (it, 0) if isinstance(it, str) else it
        par = tf.paragraphs[0] if (k == 0 and first) else tf.add_paragraph()
        par.level = lvl
        runs(par, text, size if lvl == 0 else sub)
        par.space_after = Pt(4 if lvl == 0 else 2)

def textbox(slide, left, top, width, height, items, size=16, sub=14, color=None, bullet=True):
    tb = slide.shapes.add_textbox(left, top, width, height); tf = tb.text_frame; tf.word_wrap = True
    for k, it in enumerate(items):
        text, lvl = (it, 0) if isinstance(it, str) else it
        par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        runs(par, ("•  " if bullet else "") + text, size if lvl == 0 else sub, color=color)
        par.space_after = Pt(4)
    return tb

def code(slide, left, top, width, height, title, lines, size=11):
    box = slide.shapes.add_shape(1, left, top, width, height)   # rectangle
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xEE, 0xF1, 0xF5); box.line.color.rgb = RGBColor(0xD9, 0xDE, 0xE6)
    box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = False; tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.15); tf.margin_top = Inches(0.08)
    p = tf.paragraphs[0]; runs(p, title, size + 1, bold=True, color=INK); p.space_after = Pt(4)
    for ln in lines:
        p = tf.add_paragraph(); runs(p, ln, size, color=RGBColor(0x2B, 0x36, 0x48), mono=True); p.space_after = Pt(0)
    return box

def picture(slide, name, left, top, width, height, caption=None, csize=11):
    path = os.path.join(DATA, name); w, h = Image.open(path).size
    scale = min(width / w, height / h); pw, phh = int(w * scale), int(h * scale)
    pic = slide.shapes.add_picture(path, left + (width - pw) // 2, top, pw, phh)
    if caption:
        tb = slide.shapes.add_textbox(left, top + phh + Inches(0.05), width, Inches(0.5)); tf = tb.text_frame; tf.word_wrap = True
        runs(tf.paragraphs[0], caption, csize, color=MUTED); tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    return pic

def table(slide, left, top, width, rows, col_widths=None, size=12, head_size=10, hl=None):
    nr, nc = len(rows), len(rows[0])
    shp = slide.shapes.add_table(nr, nc, left, top, width, Inches(0.3) * nr); tbl = shp.table
    if col_widths:
        tot = sum(col_widths)
        for j, cw in enumerate(col_widths): tbl.columns[j].width = int(width * cw / tot)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = tbl.cell(i, j); c.text = ""; p = c.text_frame.paragraphs[0]
            runs(p, val, head_size if i == 0 else size, bold=(i == 0) or (hl == (i, j)), color=(ACCENT if hl == (i, j) else None))
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            c.margin_top = c.margin_bottom = Inches(0.03)
    return tbl

def content_slide(title, items, size=18, sub=15):
    s = prs.slides.add_slide(L["Title and Content"]); set_title(s, title)
    bullets(ph(s, 1).text_frame, items, size, sub); return s

def two_content(title):
    s = prs.slides.add_slide(L["Two Content"]); set_title(s, title)
    a, b = ph(s, 1), ph(s, 2)
    geo = [(x.left, x.top, x.width, x.height) for x in (a, b)]
    return s, a, b, geo

def remove(shape): shape._element.getparent().remove(shape._element)

EQ = os.path.join(DATA, "eq")
_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"

def text_height(text, size, width_in, indent=0.0):
    """rough wrapped height (in) of one paragraph; Arial metrics +10% stand in for Aptos"""
    import re
    from PIL import ImageFont
    f = ImageFont.truetype(_FONT, int(size * 10)); plain = re.sub(r"\*\*|`|[_^]\{|\}", "", text)
    avail = (width_in - indent - 0.25) * 720; lines, cur = 1, 0
    for w in plain.split():
        ww = 1.1 * f.getlength(w + " ")
        if cur + ww > avail: lines += 1; cur = ww
        else: cur += ww
    return lines * size * 1.2 / 72

def stack(slide, left, top, width, items, size=15, color=None):
    """place text paragraphs and LaTeX equation images top to bottom; items: str, ("•", str) or ("eq", name).
    Returns the bottom edge (EMU)."""
    y = top
    for it in items:
        if isinstance(it, tuple) and it[0] == "eq":
            path = os.path.join(EQ, it[1] + ".png"); pw, phh = Image.open(path).size
            w_in, h_in = pw / 600, phh / 600; scale = min(1.0, (width / 914400 - 0.3) / w_in)
            pic = slide.shapes.add_picture(path, left + Inches(0.15), y + Inches(0.02), Inches(w_in * scale), Inches(h_in * scale))
            y = pic.top + pic.height + Inches(0.08)
        else:
            bullet = isinstance(it, tuple); text = it[1] if bullet else it
            h = text_height(("•  " if bullet else "") + text, size, width / 914400)
            tb = slide.shapes.add_textbox(left, y, width, Inches(h)); tf = tb.text_frame; tf.word_wrap = True
            tf.margin_top = tf.margin_bottom = 0
            runs(tf.paragraphs[0], ("•  " if bullet else "") + text, size, color=color if color is not None else RGBColor(0x2B, 0x36, 0x48))
            y = y + Inches(h + 0.08)
    return y

def panel(slide, left, top, width, title, items, size=15):
    """shaded panel with a bold title and a stack() body; returns its bottom edge (EMU)"""
    box = slide.shapes.add_shape(1, left, top, width, Inches(1))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xEE, 0xF1, 0xF5); box.line.color.rgb = RGBColor(0xD9, 0xDE, 0xE6)
    box.shadow.inherit = False
    tb = slide.shapes.add_textbox(left + Inches(0.05), top + Inches(0.06), width, Inches(0.35))
    runs(tb.text_frame.paragraphs[0], title, size - 1, bold=True, color=INK)
    bottom = stack(slide, left + Inches(0.05), top + Inches(0.5), width - Inches(0.1), items, size)
    box.height = bottom - top + Inches(0.05)
    return box.top + box.height

def source(slide, left, top, width, text):
    tb = slide.shapes.add_textbox(left, top, width, Inches(0.4)); tb.text_frame.word_wrap = True
    runs(tb.text_frame.paragraphs[0], text, 11, color=MUTED); return tb

TITLE = "Recent updates to ANSI MH16.1: perforated rack member design and the Direct Strength Method"
URL = "runtosolve.github.io/ICCFSS2026_MoenRackStandards"

def title_slide():
    s = prs.slides.add_slide(L["Title Slide"])
    set_title(s, TITLE, 34)
    sub = ph(s, 1); sub.text = ""
    runs(sub.text_frame.paragraphs[0], "Cristopher D. Moen", 22, color=INK)
    p = sub.text_frame.add_paragraph(); runs(p, "RunToSolve LLC", 18, color=MUTED)
    p = sub.text_frame.add_paragraph(); runs(p, "Wei-Wen Yu International Specialty Conference on Cold-Formed Steel Structures, Madison, Wisconsin", 14, color=MUTED)
    s.shapes.add_picture(os.path.join(DATA, "qr.png"), Inches(11.4), Inches(5.6), Inches(1.5), Inches(1.5))
    tb = s.shapes.add_textbox(Inches(8.9), Inches(7.05), Inches(4.2), Inches(0.3))
    runs(tb.text_frame.paragraphs[0], URL, 9, color=MUTED); tb.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT

# ───────────────────────────── 1 title ─────────────────────────────
title_slide()

# ───────────────────────────── 2 motivation ─────────────────────────────
s = content_slide("Three editions of MH16.1 in eleven years", [
    "**ANSI MH16.1** (RMI) is the specification for industrial steel storage racks, referenced by ASCE 7 §15.5.3 and the IBC",
    "Rack uprights are roll-formed, thin, open, and **perforated along their full length**, so local, distortional, and global buckling interact",
    "The 2021 edition rewrote the member design chapter around elastic buckling analysis; the 2023 edition kept it",
    "This talk: what changed from 2012 to 2023 and where the Direct Strength Method enters"], 17, 14)
b0 = ph(s, 1); b0.left, b0.top, b0.width, b0.height = Inches(0.92), Inches(1.9), Inches(11.5), Inches(2.5)
picture(s, "fig_timeline.png", Inches(1.4), Inches(4.8), Inches(10.5), Inches(1.8))

# ───────────────────────────── 3 2012 baseline ─────────────────────────────
s, a, b, geo = two_content("MH16.1-2012: effective area and the stub-column Q factor")
remove(a); remove(b); (l, t, w, h) = geo[0]; (l2, t2, w2, h2) = geo[1]
panel(s, l, t, w, "Compression (§4.1.3.1)", [
    ("•", "Effective area from the stub-column test:"), ("eq", "ae"),
    ("•", "P_{n} = A_{e} F_{n}, with F_{n} from AISI S100 on the **gross, unperforated** section"),
    ("•", "Q = stub column strength / (F_{y} A_{net,min}) ≤ 1  (§9.2.2)")])
y = panel(s, l2, t2, w2, "Flexure (§4.1.2)", [("eq", "se"),
    ("•", "Round corners for A and I; sharp corners permitted for J, C_{w}, r_{o}")])
panel(s, l2, y + Inches(0.2), w2, "Distortional (§4.1.3.2)", [
    ("•", "One sentence: certain open sections \"shall be checked … by testing or rational analysis\""),
    ("•", "No equations, no elastic buckling load")])
textbox(s, l, Inches(6.1), Inches(11.5), Inches(0.5), [
    "Frame stability by the effective length method: down-aisle K_{x} = 1.7 for unbraced racks, K_{t} = 0.8"], 14, color=MUTED, bullet=False)

# ───────────────────────────── 4 strips ─────────────────────────────
s, a, b, geo = two_content("MH16.1-2021 §8.2.1: perforations become reduced-thickness strips")
remove(a); remove(b); (l, t, w, h) = geo[0]; (l2, t2, w2, h2) = geo[1]
stack(s, l, t, w, [
    ("•", "Section properties use **round corners** for everything, including J and C_{w} (sharp corners are unconservative for torsion)"),
    ("•", "Each strip of web or flange that contains perforations is replaced by a solid strip of reduced thickness"),
    ("•", "**Global and local** buckling, k_{g} = 0.6:"), ("eq", "tg"),
    ("•", "**Distortional** buckling, k_{d} = 0.8:"), ("eq", "td"),
    ("•", "L_{np} is the solid length between holes, L the pitch")], 16)
picture(s, "fig_strips.png", l2, t2, w2, Inches(2.6), "Source: ANSI MH16.1-2023, Figure 8.2-1, example of perforation strips in a column")
textbox(s, l2, t2 + Inches(3.2), w2, Inches(1.2), [
    "One idealized section feeds the frame model (§7.2.4), the global buckling check, and the finite strip model for P_{crd} and M_{crd}"], 15)

# ───────────────────────────── 5 compression ─────────────────────────────
s, a, b, geo = two_content("MH16.1-2021/2023 §8.2.2: perforated compression members")
remove(a); remove(b); (l, t, w, h) = geo[0]; (l2, t2, w2, h2) = geo[1]
y = panel(s, l, t - Inches(0.2), w, "Global (8.2-3, 8.2-4)", [("eq", "pne"),
    "P_{y} = F_{y} A_{netg}; P_{cre} with K, L from §10.2, §10.3"])
panel(s, l, y + Inches(0.2), w, "Local + global (8.2-5, 8.2-6)", [("eq", "pnlg"),
    "P_{nlg} = P_{ne} if Q ≥ 1 (split out as its own equation in 2023)"])
y = panel(s, l2, t2 - Inches(0.2), w2, "Distortional + global (8.2-7, 8.2-8)", [("eq", "pnld"),
    "for λ_{d} = √(P_{ne} / P_{crd}) > 0.561, else P_{nld} = P_{ne}"])
stack(s, l2, y + Inches(0.25), w2, [
    ("•", "**P_{n} = min(P_{nlg}, P_{nld})**"),
    ("•", "P_{crd}: elastic distortional buckling \"in accordance with ANSI/AISI S100\" on the t_{d} section"),
    ("•", "Hot-rolled and closed sections: P_{nlg} only")], 16, color=INK)

# ───────────────────────────── 6 local ─────────────────────────────
s, a, b, geo = two_content("Local buckling: still the stub column, in a new form")
remove(a); (l, t, w, h) = geo[0]
picture(s, "fig_local_global.png", l, t, w, Inches(3.4),
        "Both forms with F_{n}/F_{y} = P_{ne}/P_{y} on the same area basis. 2012 used A_{net,min}; 2021 uses A_{netg} from the strip section.")
bullets(b.text_frame, [
    "Local buckling is **not** a DSM check: there is no P_{crℓ}. The perforation and local slenderness effects both come from the **stub-column test** (§13.2.3, Q = P_{test} / (F_{y} A_{netg}) ≤ 1, interpolated between t_{min} and t_{max})",
    "The 2021 exponent Q/(1 − Q) makes the local penalty fade as the column becomes globally slender, the same trend as the DSM local–global curve",
    "For a given Q, the new form is less severe at intermediate λ_{c}"], 16, 14)

# ───────────────────────────── 7 distortional ─────────────────────────────
s, a, b, geo = two_content("Distortional buckling: the Direct Strength Method piece")
bullets(a.text_frame, [
    "New in 2021: an explicit distortional check with an elastic buckling load, P_{crd} or M_{crd}, the DSM ingredient",
    "Same 0.25 / 0.6 coefficients and 0.561 limit as the AISI S100 distortional curve, but **anchored at P_{ne} instead of P_{y}**",
    "That captures distortional–global interaction, which tests and FE studies on perforated uprights showed (Casafont, Pastor, Roure, Bonada, Peköz)",
    "At λ_{c} = 0 the two agree; at intermediate slenderness MH16.1 is lower, and both reach P_{ne} for slender columns"], 16, 14)
remove(b); (l2, t2, w2, h2) = geo[1]
picture(s, "fig_dist_curve.png", l2, t2, w2, Inches(3.4), "Example with P_{crd} = 0.6 P_{y}")

# ───────────────────────────── 8 FSM ─────────────────────────────
s, a, b, geo = two_content("Finite strip analysis on the strip section")
remove(a); (l, t, w, h) = geo[0]
picture(s, "fig_cufsm.png", l, t, w, Inches(2.6),
        "Source: ANSI MH16.1-2023 Commentary, Figure C8.2-5. CUFSM: local minimum at 80 mm (load factor 14.92), distortional at 700 mm (10.63)")
bullets(b.text_frame, [
    "Commentary C8: the \"most suitable design approach would be to use finite strip analysis combined with the expressions given\"",
    "Workflow",
    ("build the round-corner section with t_{d} in the perforated strips", 1),
    ("run CUFSM (or any S100 Appendix 2 analysis)", 1),
    ("read P_{crd} at the distortional minimum", 1),
    ("the same model with t_{g} gives the global section properties", 1),
    "Basis: tests, shell FE and FSM studies on perforated uprights (Casafont et al., ASCE J. Struct. Eng. 2013, \"Design of steel storage rack columns via the Direct Strength Method\")"], 16, 14)

# ───────────────────────────── 9 flexure ─────────────────────────────
s, a, b, geo = two_content("MH16.1-2021/2023 §8.2.3: flexure follows the same pattern")
remove(a); remove(b); (l, t, w, h) = geo[0]; (l2, t2, w2, h2) = geo[1]
y1 = panel(s, l, t, w, "Local + global (8.2-9, 8.2-10)", [("eq", "mnlg"),
    "M_{y} = F_{y} S_{fy}, with S_{fy} on the reduced-thickness section"])
y2 = panel(s, l2, t2, w2, "Distortional + global (8.2-11, 8.2-12)", [("eq", "mnld"),
    "for λ_{d} = √(M_{ne} / M_{crd}) > 0.673, else M_{nld} = M_{ne}"])
stack(s, l, max(y1, y2) + Inches(0.3), Inches(11.5), [
    ("•", "M_{n} = min(M_{nlg}, M_{nld}) for open cold-formed sections bending about the axis of symmetry; hot-rolled and closed sections use M_{nlg}"),
    ("•", "The coefficients match the AISI S100 flexural distortional curve, anchored at M_{ne} like compression"),
    ("•", "M_{crd} comes from finite strip analysis on the t_{d} section, as for P_{crd}")], 16, color=INK)

# ───────────────────────────── 10 stability ─────────────────────────────
s, a, b, geo = two_content("MH16.1-2021: from effective length to direct analysis")
bullets(a.text_frame, [
    "**§7.2: second-order analysis with notional loads** replaces the effective length method",
    ("N_{i} = 0.004 αY_{i} with the stiffness reduction τ_{b}, or 0.005 αY_{i} without; minimum 0.002 αY_{i}", 1),
    ("B_{2} = 1 / (1 − α P_{Δ} / (R_{m} H L))", 1),
    ("semi-rigid beam-to-column connections modeled with springs", 1),
    "Down-aisle K_{x} = 1.0 (§10.2.1)",
    "Member and frame models use the same hole-reduced section properties"], 16, 14)
bullets(b.text_frame, [
    "**Connectors from cyclic tests** (§13.5): design moment 0.75 M_{max}; stiffness is the secant at 0.8 M_{conn,d}",
    "New tests: base fixity (§13.6) and frame bracing (§13.7); portal and upright frame tests removed",
    "Seismic aligned to ASCE 7-16; redundancy factor for multiple rows; overstrength design of base plates and anchors (§11.3)",
    "ISO-style reorganization of the whole document"], 16, 14)

# ───────────────────────────── 11 closing copy of the title slide ─────────────────────────────
title_slide()

# carry the template's date and slide-number footers onto every slide (copied from each slide's layout)
from pptx.enum.shapes import PP_PLACEHOLDER
for k, s in enumerate(prs.slides, 1):
    for lp in s.slide_layout.placeholders:
        if lp.placeholder_format.type in (PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.SLIDE_NUMBER):
            el = copy.deepcopy(lp._element); s.shapes._spTree.append(el)
    for sh in s.placeholders:
        if sh.placeholder_format.type == PP_PLACEHOLDER.DATE and sh.has_text_frame:
            sh.text_frame.text = "October 6–7, 2026"
prs.save(OUT); print("wrote", OUT, len(prs.slides), "slides")
