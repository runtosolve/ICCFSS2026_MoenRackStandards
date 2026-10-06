"""Typeset the PowerPoint equations with LaTeX into deck/data/eq/*.png (transparent, 600 dpi, slide ink color).
    python3 deck/data/make_eqs.py
Needs pdflatex and pdftoppm. build_pptx.py places each image at its natural size (20 pt math)."""
import os, subprocess, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "eq"); os.makedirs(OUT, exist_ok=True)
DPI = 600; INK = (0x2B, 0x36, 0x48)

EQS = {
    "ae":   r"A_e = \left[1 - (1 - Q)\left(\frac{F_n}{F_y}\right)^{Q}\right] A_{\mathrm{net,min}}",
    "se":   r"S_e = S_{\mathrm{net,min}}\,(0.5 + Q/2)",
    "tg":   r"t_g = k_g\, t \left(\frac{L_{np}}{L}\right)",
    "td":   r"t_d = k_d\, t \left(\frac{L_{np}}{L}\right)^{1/3}",
    "pne":  r"P_{ne} = \begin{cases} 0.658^{\lambda_c^2}\, P_y & \lambda_c \le 1.5 \\[4pt] \dfrac{0.877}{\lambda_c^2}\, P_y & \lambda_c > 1.5 \end{cases} \qquad \lambda_c = \sqrt{P_y / P_{cre}}",
    "pnlg": r"P_{nlg} = P_{ne}\left[1 - (1 - Q)\left(\frac{P_{ne}}{P_y}\right)^{\frac{Q}{1-Q}}\right], \quad Q < 1",
    "pnld": r"P_{nld} = \left[1 - 0.25\left(\frac{P_{crd}}{P_{ne}}\right)^{0.6}\right]\left(\frac{P_{crd}}{P_{ne}}\right)^{0.6} P_{ne}",
    "mnlg": r"M_{nlg} = M_{ne}\left[1 - \tfrac{1}{2}(1 - Q)\left(\frac{M_{ne}}{M_y}\right)^{\frac{Q}{1-Q}}\right], \quad Q < 1",
    "mnld": r"M_{nld} = \left[1 - 0.22\left(\frac{M_{crd}}{M_{ne}}\right)^{0.5}\right]\left(\frac{M_{crd}}{M_{ne}}\right)^{0.5} M_{ne}",
}

TEX = r"""\documentclass[border=3pt]{standalone}
\usepackage{amsmath}
\begin{document}
\fontsize{20}{24}\selectfont$\displaystyle %s$
\end{document}
"""

for name, body in EQS.items():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "eq.tex"), "w") as f: f.write(TEX % body)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "eq.tex"], cwd=tmp, check=True,
                       stdout=subprocess.DEVNULL)
        subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", "-singlefile", "eq.pdf", "eq"], cwd=tmp, check=True)
        g = Image.open(os.path.join(tmp, "eq.png")).convert("L")
    alpha = g.point(lambda v: 255 - v)                      # ink coverage -> opacity
    im = Image.new("RGBA", g.size, INK + (0,)); im.putalpha(alpha)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)
    print(name, im.size)
