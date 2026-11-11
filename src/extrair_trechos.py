"""Extrai o trecho de abertura de cada romance para o site.

Lê data/raw/machado/romance/marm01..10.txt (Windows-1252), pega os primeiros
parágrafos do primeiro capítulo (ou do corpo do texto, quando não há capítulos)
e junta com o resumo de docs/romances.md e os números de results/resultados.json.
Saída: site/dados/romances.json

Uso (a partir da raiz do repositório, depois de src/baixar_corpus.py):
    python src/extrair_trechos.py
"""
import json
import pathlib
import re

PASTA = pathlib.Path("data/raw/machado/romance")
RESUMOS = pathlib.Path("docs/romances.md")
RESULTADOS = pathlib.Path("results/resultados.json")
SAIDA = pathlib.Path("site/dados/romances.json")
MIN_CHARS, MAX_CHARS = 380, 720


def paragrafos(texto):
    blocos = re.split(r"\n\s*\n", texto)
    return [re.sub(r"\s+", " ", b).strip() for b in blocos if b.strip()]


def eh_titulo(p):
    letras = re.sub(r"[^A-Za-zÀ-ÿ]", "", p)
    data = re.match(r"^\d{1,2} de \w+$", p)
    return len(p) < 80 and (letras.isupper() or re.match(r"^CAP[IÍ]TULO", p) or data)


def trecho(arquivo):
    txt = arquivo.read_bytes().decode("cp1252").replace("\r", "")
    m = re.search(r"^\s*CAP[IÍ]TULO\b.*$", txt, re.M)
    if m:
        corpo = txt[m.start():]
    else:  # sem capítulos (diário do Memorial de Aires): começa na primeira data
        m = re.search(r"^\s*1[89]\d\d\s*$", txt, re.M)
        corpo = txt[m.end():]
    ps = [p for p in paragrafos(corpo) if not eh_titulo(p)]
    saida = ""
    for p in ps:
        p = p.replace("--", "—").replace("«", "“").replace("»", "”")
        saida = (saida + "\n\n" + p).strip()
        if len(saida) >= MIN_CHARS:
            break
    if len(saida) > MAX_CHARS:  # corta no fim de uma frase
        corte = max(saida.rfind(s, 0, MAX_CHARS) for s in (". ", "! ", "? ", "; "))
        saida = saida[: corte + 1].rstrip(";") + " […]"
    return saida


def main():
    resumos = {}
    for m in re.finditer(r"^\d+\. \*\*(.+?) \((.+?)\)\.\*\* (.+)$", RESUMOS.read_text(encoding="utf-8"), re.M):
        resumos[m.group(1)] = {"data": m.group(2), "resumo": m.group(3)}
    res = json.loads(RESULTADOS.read_text(encoding="utf-8"))
    romances = []
    for i, (pre, alfa) in enumerate(zip(res["preprocessamento"], res["alfa_romance"]), 1):
        titulo = pre["titulo"]
        info = resumos[titulo]
        romances.append({
            "id": f"marm{i:02d}",
            "titulo": titulo,
            "ano": int(re.match(r"\d{4}", info["data"]).group()),
            "data": info["data"],
            "fase": "romântica" if i <= 4 else "realista",
            "palavras": pre["palavras"],
            "alfa": alfa["alfa_10_1000"],
            "resumo": info["resumo"],
            "trecho": trecho(PASTA / pre["arquivo"]),
        })
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(romances, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(romances)} romances em {SAIDA}")


if __name__ == "__main__":
    main()
