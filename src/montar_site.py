"""Monta o site do projeto em _site/, pronto para o GitHub Pages.

Copia site/ (HTML, CSS, JS e dados dos romances) e junta os arquivos do
projeto que o site usa: results/resultados.json, as figuras, as fontes e o
logo da apresentação e o PDF dos slides. Só usa a biblioteca padrão.

Uso (a partir da raiz do repositório):
    python src/montar_site.py
    python -m http.server 8000 -d _site     # para ver em http://localhost:8000
"""
import pathlib
import shutil

DESTINO = pathlib.Path("_site")
COPIAS = {
    "site": "",
    "results/resultados.json": "dados/resultados.json",
    "figuras": "figuras",
    "apresentacao/assets": "assets",
    "apresentacao/apresentacao.pdf": "apresentacao.pdf",
    "docs/prints": "prints",
}


def main():
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    for origem, alvo in COPIAS.items():
        o, d = pathlib.Path(origem), DESTINO / alvo
        if o.is_dir():
            shutil.copytree(o, d, dirs_exist_ok=True)
        else:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(o, d)
    (DESTINO / ".nojekyll").touch()
    n = sum(1 for p in DESTINO.rglob("*") if p.is_file())
    print(f"site montado em {DESTINO}/ ({n} arquivos)")


if __name__ == "__main__":
    main()
