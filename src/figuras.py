"""Gera as figuras do artigo a partir de results/resultados.json.

Uso: python src/figuras.py [results/resultados.json] [pasta_de_saida]
"""
import json
import math
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ENTRADA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results/resultados.json")
SAIDA = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "figuras")
SAIDA.mkdir(parents=True, exist_ok=True)

TINTA, CINZA, CINZA_CLARO, AZUL = "#1a1a18", "#5b5952", "#a8a59c", "#0b5fa5"
plt.rcParams.update({
    "font.size": 11, "axes.edgecolor": CINZA_CLARO, "axes.labelcolor": CINZA,
    "xtick.color": CINZA, "ytick.color": CINZA, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#ebe9e2",
    "figure.dpi": 150, "savefig.bbox": "tight",
})

d = json.loads(ENTRADA.read_text(encoding="utf-8"))
car = d["caracteres"]


def br(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


# 1. Entropia cruzada por tamanho do contexto ------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ks = [r["k"] for r in car["H"]]
med = [r["media"] for r in car["H"]]
lo = [r["media"] - r["min"] for r in car["H"]]
hi = [r["max"] - r["media"] for r in car["H"]]
melhor = min(range(len(med)), key=lambda i: med[i])
ax.errorbar(ks, med, yerr=[lo, hi], color=CINZA_CLARO, ecolor=CINZA, marker="o", mfc=CINZA, mec=CINZA, capsize=3)
ax.plot([ks[melhor]], [med[melhor]], "o", color=AZUL, ms=10, zorder=5)
ax.annotate(f"mínimo: {br(med[melhor])}", (ks[melhor], med[melhor]), xytext=(0, 18), textcoords="offset points", ha="center", color=AZUL)
ax.axhline(math.log2(27), ls="--", color=CINZA_CLARO)
ax.text(8.35, math.log2(27), f"sem informação: {br(math.log2(27))}", va="center", color=CINZA, fontsize=9)
ax.axhline(1.0, ls="--", color=CINZA_CLARO)
ax.text(8.35, 1.0, "Shannon, inglês: ≈ 1", va="center", color=CINZA, fontsize=9)
ax.set_ylim(0, 5.2)
ax.set_xticks(ks)
ax.set_xlabel("letras de contexto usadas pelo modelo")
ax.set_ylabel("bits por caractere")
ax.set_title(f"Com {ks[melhor]} letras de contexto, a incerteza cai para {br(med[melhor])} bit por caractere", loc="left", color=TINTA, fontsize=12)
fig.savefig(SAIDA / "entropia_contexto.png")
plt.close(fig)

# 2. Zipf: Machado e modelos nulos -------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.6))
estilos = {
    "aleatorio": ("Digitação aleatória", CINZA_CLARO, "-", 2.5),
    "machado27": ("Machado de Assis", AZUL, "-", 3.5),
    "ngrama4": ("Texto gerado por n-gramas", TINTA, "--", 1.5),
}
for chave, (nome, cor, ls, lw) in estilos.items():
    pts = d["nulos_pontos"][chave]
    alfa = d["nulos"][chave]["alfa"]
    ax.loglog([p["posto"] for p in pts], [p["freq"] for p in pts], ls=ls, color=cor, lw=lw, marker="o", ms=3, label=f"{nome} (α = {br(alfa)})")
ax.set_xlabel("posição da palavra no ranking")
ax.set_ylabel("ocorrências")
ax.legend(frameon=False)
ax.set_title("Três textos, mesma inclinação: α ≈ 1 não identifica o mecanismo", loc="left", color=TINTA, fontsize=12)
fig.savefig(SAIDA / "zipf_modelos_nulos.png")
plt.close(fig)

# 3. Zipf em Machado com a reta ajustada por máxima verossimilhança ---------------
fig, ax = plt.subplots(figsize=(7.5, 4.6))
pts = d["zipf_pts"]
ax.loglog([p["posto"] for p in pts], [p["freq"] for p in pts], "o", color=AZUL)
for p in pts:
    if p["palavra"] in ("a", "nada", "confesso", "frugalidade"):
        ax.annotate(p["palavra"], (p["posto"], p["freq"]), xytext=(6, 6), textcoords="offset points", fontsize=9, color=TINTA)
faixas = ", ".join(f"{f['faixa']}: {br(f['alfa'])}" for f in d["zipf_faixas"])
ax.set_xlabel("posição da palavra no ranking")
ax.set_ylabel("ocorrências")
ax.set_title(f"Lei de Zipf em Machado: α = {br(d['mle']['alfa'])} (máxima verossimilhança)", loc="left", color=TINTA, fontsize=12)
fig.text(0.01, -0.02, f"Mínimos quadrados por faixa de postos: {faixas}", fontsize=8, color=CINZA)
fig.savefig(SAIDA / "zipf_machado.png")
plt.close(fig)

# 4. Parâmetro de ordem e acerto exato ----------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.6))
params = car["params"]
estilos_L = {"1": (AZUL, "-", 3, "acerto por letra (φ)"), "3": (CINZA_CLARO, "-", 2, "3 letras seguidas"),
             "5": (CINZA, "-", 2, "5 letras seguidas"), "10": (TINTA, "--", 2.5, "10 letras seguidas")}
for L, (cor, ls, lw, nome) in estilos_L.items():
    v = [r["media"] for r in car["m"][L]]
    ax.semilogx(params, [x / v[-1] * 100 for x in v], ls=ls, color=cor, lw=lw, marker="o", ms=4,
                label=f"{nome}: máx. {br(v[-1] * 100, 1)}%")
ax.axhline(50, ls=":", color=CINZA_CLARO)
ax.set_ylim(-3, 105)
ax.set_xlabel("número de parâmetros do modelo")
ax.set_ylabel("% do valor no maior modelo")
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.set_title("Mesmos modelos, métricas diferentes: o salto só aparece no acerto exato", loc="left", color=TINTA, fontsize=12)
fig.savefig(SAIDA / "parametro_de_ordem.png")
plt.close(fig)

print(f"figuras gravadas em {SAIDA}/")
