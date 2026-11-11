"""Gera um print (PNG) de cada slide para o README.

Abre apresentacao/apresentacao.html no Chromium (Playwright), fotografa cada
slide em 1920 x 1080 e salva uma versão reduzida (1280 x 720) em
docs/prints/slide-NN-<id>.png, na ordem de apresentacao/deck.json.

Uso (a partir da raiz do repositório):
    python src/montar_apresentacao.py   # garante o HTML atualizado
    python src/gerar_prints.py          # requer: pip install playwright && playwright install chromium
"""
import io
import json
import pathlib

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = pathlib.Path("apresentacao")
SAIDA = pathlib.Path("docs/prints")
LARGURA, ALTURA = 1280, 720


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    ordem = json.loads((BASE / "deck.json").read_text(encoding="utf-8"))["order"]
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1920, "height": 1080})
        pag.goto((BASE / "apresentacao.html").resolve().as_uri())
        pag.add_style_tag(content=".notas{display:none!important}.palco{transform:none!important;margin:0!important}")
        pag.wait_for_timeout(800)
        palcos = pag.query_selector_all(".palco")
        for i, (palco, sid) in enumerate(zip(palcos, ordem), 1):
            img = Image.open(io.BytesIO(palco.screenshot())).convert("RGB")
            img.thumbnail((LARGURA, ALTURA), Image.LANCZOS)
            img.save(SAIDA / f"slide-{i:02d}-{sid}.png", optimize=True)
        nav.close()
    print(f"{len(ordem)} prints em {SAIDA}")


if __name__ == "__main__":
    main()
