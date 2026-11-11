"""Monta a apresentação em um único HTML (e, opcionalmente, em PDF).

Os slides ficam em apresentacao/slides/<id>.html, um <section> por arquivo,
na ordem definida em apresentacao/deck.json. O <aside> de cada slide guarda
as notas do apresentador.

Uso:
    python src/montar_apresentacao.py          # gera apresentacao/apresentacao.html
    python src/montar_apresentacao.py --pdf    # também gera apresentacao/apresentacao.pdf (requer playwright)
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path("apresentacao")
LOGO_BLOB = "/_blob/10125f8775de1b7829e38b79d3752348"

CSS = """
@font-face { font-family: "Space Grotesk"; src: url(assets/fonts/space-grotesk-latin-wght-normal.woff2) format("woff2"); font-weight: 300 700; }
@font-face { font-family: "Inter"; src: url(assets/fonts/inter-latin-wght-normal.woff2) format("woff2"); font-weight: 100 900; }
* { box-sizing: border-box; margin: 0; }
html, body { background: #2b2b28; }
body { font-family: Inter, Arial, sans-serif; color: #1a1a18; }
.palco { width: 1920px; height: 1080px; overflow: hidden; margin: 0 auto 40px; transform-origin: top left; }
section { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
section > aside { display: none; }
h1, h2, h3, p { font-weight: inherit; }
h1 { font-size: 96px; font-weight: 600; line-height: 1.1; }
h2 { font-size: 64px; font-weight: 600; line-height: 1.15; }
h3 { font-size: 44px; font-weight: 600; line-height: 1.2; }
p { font-size: 32px; line-height: 1.4; }
ul, ol { padding-left: 1.2em; }
li { margin: 0.15em 0; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #d6d3ca; padding: 0.35em 0.6em; text-align: left; vertical-align: top; }
th { font-weight: 600; }
hr { border: none; height: 0; }
x-shape { display: block; }
x-shape[kind="arrow-right"] { clip-path: polygon(0 30%, 60% 30%, 60% 0, 100% 50%, 60% 100%, 60% 70%, 0 70%); }
x-shape[kind="line"] { height: 0 !important; background: none; border-left: none !important; border-right: none !important; border-bottom: none !important; }
.notas { width: 1920px; margin: -24px auto 60px; padding: 24px 32px; background: #f6f5f1; font-size: 22px; line-height: 1.5; border-radius: 8px; }
body.sem-notas .notas { display: none; }
@media print {
  @page { size: 1920px 1080px; margin: 0; }
  html, body { background: none; }
  .palco { margin: 0; transform: none !important; page-break-after: always; }
  .notas { display: none; }
}
"""

JS = """
function ajustar() {
  const w = window.innerWidth - 32;
  const s = Math.min(1, w / 1920);
  document.querySelectorAll('.palco').forEach(p => {
    p.style.transform = 'scale(' + s + ')';
    p.style.marginBottom = (40 - 1080 * (1 - s)) + 'px';
  });
  document.querySelectorAll('.notas').forEach(n => { n.style.width = (1920 * s) + 'px'; });
}
window.addEventListener('resize', ajustar);
window.addEventListener('load', ajustar);
"""


def main():
    deck = json.loads((BASE / "deck.json").read_text(encoding="utf-8"))
    partes = []
    for i, sid in enumerate(deck["order"], 1):
        html = (BASE / "slides" / f"{sid}.html").read_text(encoding="utf-8")
        html = html.replace(LOGO_BLOB, "assets/usp-logo.png")
        nota = re.search(r"<aside>(.*?)</aside>", html, re.S)
        partes.append(f'<div class="palco">{html}</div>')
        if nota:
            partes.append(f'<div class="notas"><b>Slide {i} · notas:</b> {nota.group(1).strip()}</div>')
    titulo = deck.get("title", "Apresentação")
    doc = (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{titulo}</title><style>{CSS}</style><script>{JS}</script></head>"
        "<body>" + "\n".join(partes) + "</body></html>"
    )
    saida = BASE / "apresentacao.html"
    saida.write_text(doc, encoding="utf-8")
    print(f"{len(deck['order'])} slides em {saida}")

    if "--pdf" in sys.argv:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            nav = p.chromium.launch()
            pag = nav.new_page(viewport={"width": 1920, "height": 1080})
            pag.goto(saida.resolve().as_uri())
            pag.add_style_tag(content=".notas{display:none!important}.palco{transform:none!important;margin:0!important}")
            pag.wait_for_timeout(500)
            pag.pdf(path=str(BASE / "apresentacao.pdf"), width="1920px", height="1080px", print_background=True)
            nav.close()
        print(f"PDF em {BASE / 'apresentacao.pdf'}")


if __name__ == "__main__":
    main()
