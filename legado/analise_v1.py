import sys, re, math, json, glob, bz2, lzma, collections
import numpy as np

pasta = sys.argv[1]
arquivos = sorted(glob.glob(pasta + "/romance/marm*.txt"))
textos = []
for f in arquivos:
    raw = open(f, "rb").read()
    t = raw.decode("cp1252", errors="replace")
    textos.append(t)
texto = "\n".join(textos).lower()

# --- tokens (palavras) ---
palavras = re.findall(r"[a-zà-öø-ÿ]+(?:-[a-zà-öø-ÿ]+)*", texto)
N = len(palavras)
freq = collections.Counter(palavras)
V = len(freq)
ranked = freq.most_common()
top = [(w, c, round(100 * c / N, 2)) for w, c in ranked[:15]]
hapax = sum(1 for w, c in ranked if c == 1)

# Zipf: ajuste log-log por mínimos quadrados, postos 1..10000 (pontos espaçados em log)
r = np.arange(1, V + 1)
f = np.array([c for _, c in ranked], dtype=float)
def fit(lo, hi):
    idx = np.unique(np.logspace(np.log10(lo), np.log10(hi), 200).astype(int)) - 1
    s, b = np.polyfit(np.log10(r[idx]), np.log10(f[idx]), 1)
    return -s, b
alpha, b = fit(1, min(10000, V))
alpha_mid, _ = fit(10, min(5000, V))
zipf_pts = []
for k in [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]:
    if k <= V:
        zipf_pts.append({"posto": int(k), "freq": int(f[k - 1]), "palavra": ranked[k - 1][0]})

# Heaps: V(n) = K n^beta
pts = []
seen = set()
marks = set(np.unique(np.logspace(3, np.log10(N), 30).astype(int)))
for i, w in enumerate(palavras, 1):
    seen.add(w)
    if i in marks:
        pts.append((i, len(seen)))
pts = np.array(pts, dtype=float)
beta, logK = np.polyfit(np.log10(pts[:, 0]), np.log10(pts[:, 1]), 1)
heaps_pts = [{"n": int(a), "V": int(v)} for a, v in pts[::3]]

# --- caracteres: alfabeto de 27 símbolos (letras sem acento + espaço), como Shannon ---
mapa = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüç", "aaaaaeeeeiiiiooooouuuuc")
c = texto.translate(mapa)
c = re.sub(r"[^a-z]+", " ", c)
c = re.sub(r" +", " ", c).strip()
L = len(c)

def cond_entropy(n):
    # F_n = H(n-grama) - H((n-1)-grama), em bits por caractere
    def H(k):
        if k == 0:
            return 0.0
        cnt = collections.Counter(c[i:i + k] for i in range(L - k + 1))
        tot = sum(cnt.values())
        return -sum(v / tot * math.log2(v / tot) for v in cnt.values())
    return H(n) - H(n - 1)

F = {n: round(cond_entropy(n), 3) for n in range(1, 7)}
F0 = round(math.log2(27), 3)

# Compressão como cota superior da entropia (bits por caractere)
b = c.encode("ascii")
bz = len(bz2.compress(b, 9)) * 8 / L
xz = len(lzma.compress(b, preset=9 | lzma.PRESET_EXTREME)) * 8 / L

# Informação mútua entre caracteres a distância d (estilo Lin e Tegmark)
arr = np.frombuffer(b, dtype=np.uint8)
alf = {ch: i for i, ch in enumerate(sorted(set(c)))}
lut = np.zeros(256, dtype=np.int64)
for ch, i in alf.items():
    lut[ord(ch)] = i
x = lut[arr]
K = len(alf)
p1 = np.bincount(x, minlength=K) / len(x)
def mi(d):
    a, bb = x[:-d], x[d:]
    joint = np.bincount(a * K + bb, minlength=K * K).reshape(K, K).astype(float)
    joint /= joint.sum()
    nz = joint > 0
    return float((joint[nz] * np.log2(joint[nz] / np.outer(p1, p1)[nz])).sum())
ds = [1, 2, 3, 5, 8, 13, 20, 30, 50, 80, 130, 200, 300, 500, 800, 1300, 2000]
mis = [{"d": d, "mi": mi(d)} for d in ds]
# viés de amostra finita: MI de um embaralhamento
rng = np.random.default_rng(0)
xs = x.copy(); rng.shuffle(xs)
a, bb = xs[:-1], xs[1:]
joint = np.bincount(a * K + bb, minlength=K * K).reshape(K, K).astype(float); joint /= joint.sum()
nz = joint > 0
vies = float((joint[nz] * np.log2(joint[nz] / np.outer(p1, p1)[nz])).sum())
dd = np.array([m["d"] for m in mis if 5 <= m["d"] <= 300], dtype=float)
mm = np.array([m["mi"] - vies for m in mis if 5 <= m["d"] <= 300])
s_mi, _ = np.polyfit(np.log10(dd), np.log10(mm), 1)
# comparação: ajuste exponencial no mesmo intervalo (log-linear)
s_exp, _ = np.polyfit(dd, np.log10(mm), 1)
res_pow = np.polyfit(np.log10(dd), np.log10(mm), 1, full=True)[1]
res_exp = np.polyfit(dd, np.log10(mm), 1, full=True)[1]

out = {
    "romances": len(arquivos), "tokens": N, "tipos": V, "hapax": hapax,
    "hapax_pct": round(100 * hapax / V, 1),
    "top": top, "zipf_alpha_1_10000": round(alpha, 3), "zipf_alpha_10_5000": round(alpha_mid, 3),
    "zipf_pts": zipf_pts,
    "heaps_beta": round(beta, 3), "heaps_K": round(10 ** logK, 2), "heaps_pts": heaps_pts,
    "chars": L, "F0": F0, "F": F, "bzip2_bpc": round(bz, 3), "xz_bpc": round(xz, 3),
    "mi": [{"d": m["d"], "mi": round(m["mi"], 6)} for m in mis], "mi_vies": round(vies, 7),
    "mi_expoente": round(s_mi, 3), "mi_residuo_potencia": float(res_pow[0]), "mi_residuo_exponencial": float(res_exp[0]),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
