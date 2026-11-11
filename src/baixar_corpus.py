"""Baixa o corpus "machado" (NLTK) e extrai em data/raw/machado.

Uso: python src/baixar_corpus.py
"""
import io
import pathlib
import urllib.request
import zipfile

URL = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/machado.zip"
DESTINO = pathlib.Path("data/raw")


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    print(f"baixando {URL}")
    with urllib.request.urlopen(URL) as resp:
        dados = resp.read()
    with zipfile.ZipFile(io.BytesIO(dados)) as zf:
        for nome in zf.namelist():
            alvo = (DESTINO / nome).resolve()
            if DESTINO.resolve() not in alvo.parents and alvo != DESTINO.resolve():
                raise ValueError(f"caminho suspeito no zip: {nome}")
        zf.extractall(DESTINO)
    romances = sorted((DESTINO / "machado" / "romance").glob("marm*.txt"))
    print(f"{len(romances)} romances em {DESTINO / 'machado' / 'romance'}")


if __name__ == "__main__":
    main()
