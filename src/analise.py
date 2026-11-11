"""Linguagem como sistema complexo: analise dos dez romances de Machado de Assis.

Uso: python src/analise.py [pasta_do_corpus] [arquivo_de_saida]

Analise revisada: pre-processamento explicito, Zipf com incertezas e modelos nulos,
entropia por validacao cruzada (modelos de n-gramas de caracteres) e parametro de ordem."""
import sys, os, re, json, glob, unicodedata, collections, time
import numpy as np

pasta = sys.argv[1] if len(sys.argv) > 1 else "data/raw/machado"
saida = sys.argv[2] if len(sys.argv) > 2 else "results/resultados.json"
rng = np.random.default_rng(42)
T0 = time.time()

# ------------------------------------------------------------------ 1. pre-processamento
arquivos = sorted(glob.glob(pasta + "/romance/marm*.txt"))
titulos = []
brutos, limpos = [], []
relatorio = []
for f in arquivos:
    txt = open(f, "rb").read().decode("cp1252", errors="replace")
    linhas = txt.split("\n")
    titulos.append(linhas[0].split(",")[1].strip() if "," in linhas[0] else linhas[0])
    # (a) cabecalho editorial: tudo ate o fim do(s) paragrafo(s) "Publicado ..." nas 40 primeiras linhas
    ult = None
    for i, l in enumerate(linhas[:40]):
        if re.match(r"^\s*Publicado", l):
            ult = i
    j = ult
    while j < len(linhas) and linhas[j].strip() != "":
        j += 1
    # paragrafo seguinte ao "Publicado em volume" (marm07) continua o cabecalho
    corpo = linhas[j:]
    if re.match(r"^\s*O\s*$", "\n".join(corpo[:3]).strip().split("\n")[0] if corpo else ""):
        pass
    # (b) linhas de titulo de capitulo e a marca final FIM
    n_cap = 0
    keep = []
    for l in corpo:
        if re.match(r"^\s*CAP[IÍ]TULO\b", l):
            n_cap += 1
            continue
        if re.match(r"^\s*(FIM|Fim)\s*$", l):
            continue
        keep.append(l)
    limpo = "\n".join(keep)
    brutos.append(txt)
    limpos.append(limpo)
    relatorio.append({"arquivo": os.path.basename(f), "titulo": titulos[-1],
                      "linhas_cabecalho": j, "titulos_capitulo_removidos": n_cap})

# marm07 tem um segundo paragrafo editorial ("O que aqui vai e justamente a edicao em livro.")
limpos = [re.sub(r"^\s*O\s+que aqui vai é justamente a edição em livro\.\s*", "", t) for t in limpos]

PAL = re.compile(r"[a-zà-öø-ÿ]+(?:-[a-zà-öø-ÿ]+)*")
def palavras(t):
    return PAL.findall(t.lower())

def para27(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = re.sub(r"[^a-z]+", " ", t)
    return re.sub(r" +", " ", t).strip()

pal_por_romance = [palavras(t) for t in limpos]
car_por_romance = [para27(t) for t in limpos]
for r, w, c in zip(relatorio, pal_por_romance, car_por_romance):
    r["palavras"] = len(w); r["caracteres27"] = len(c)
todas = [w for ws in pal_por_romance for w in ws]
N = len(todas)
freq = collections.Counter(todas)
V = len(freq)
f_sorted = np.array(sorted(freq.values(), reverse=True), dtype=float)
ranked = freq.most_common()
brutas_tokens = sum(len(palavras(t)) for t in brutos)

# ------------------------------------------------------------------ 2. Zipf
def ols_alpha(fs, lo, hi):
    fs = np.sort(np.asarray(fs, dtype=float))[::-1]
    hi = min(hi, len(fs))
    r = np.arange(1, len(fs) + 1)
    idx = np.unique(np.logspace(np.log10(lo), np.log10(hi), 200).astype(int)) - 1
    x, y = np.log10(r[idx]), np.log10(fs[idx])
    s, b = np.polyfit(x, y, 1)
    yhat = s * x + b
    r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return -s, b, r2

faixas = [(1, 100), (10, 1000), (10, 5000), (100, 10000), (1, 10000)]
zipf_faixas = []
for lo, hi in faixas:
    a, b, r2 = ols_alpha(f_sorted, lo, hi)
    zipf_faixas.append({"faixa": f"{lo}-{hi}", "alfa": round(a, 3), "r2": round(r2, 4)})

# MLE discreto (Clauset, Shalizi e Newman 2009) para a distribuicao de frequencias P(f) ~ f^-beta
def mle_beta(fs, fmin):
    x = fs[fs >= fmin]
    n = len(x)
    beta = 1 + n / np.sum(np.log(x / (fmin - 0.5)))
    return beta, n
def ks(fs, fmin, beta):
    x = np.sort(fs[fs >= fmin])
    n = len(x)
    emp = 1 - np.arange(n) / n                     # P(F >= x_i)
    teo = ((x - 0.5) / (fmin - 0.5)) ** (1 - beta)
    return np.max(np.abs(emp - teo))
fs_int = f_sorted.copy()
melhor = None
for fmin in range(1, 201):
    if (fs_int >= fmin).sum() < 50:
        break
    beta, n = mle_beta(fs_int, fmin)
    d = ks(fs_int, fmin, beta)
    if melhor is None or d < melhor[0]:
        melhor = (d, fmin, beta, n)
ks_d, fmin_opt, beta_hat, n_tail = melhor
alpha_mle = 1 / (beta_hat - 1)
# rank correspondente a fmin
rank_fmin = int((f_sorted >= fmin_opt).sum())

# bootstrap (reamostragem multinomial das ocorrencias)
p = f_sorted / f_sorted.sum()
boot_ols, boot_mle = [], []
for _ in range(500):
    fb = rng.multinomial(N, p)
    fb = fb[fb > 0].astype(float)
    boot_ols.append(ols_alpha(fb, 10, 5000)[0])
    bb, _ = mle_beta(fb, fmin_opt)
    boot_mle.append(1 / (bb - 1))
ci = lambda v: [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)]

# por romance
alfa_romance = []
for t, ws in zip(titulos, pal_por_romance):
    fr = np.array(sorted(collections.Counter(ws).values(), reverse=True), dtype=float)
    a, _, r2 = ols_alpha(fr, 10, 1000)
    alfa_romance.append({"titulo": t, "palavras": len(ws), "alfa_10_1000": round(a, 3)})
ar = np.array([x["alfa_10_1000"] for x in alfa_romance])

# pontos para o grafico (Machado, palavras com acento)
zipf_pts = []
for k in [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]:
    if k <= V:
        zipf_pts.append({"posto": k, "freq": int(f_sorted[k - 1]), "palavra": ranked[k - 1][0]})

# ------------------------------------------------------------------ 3. modelos de caracteres
ALF = " abcdefghijklmnopqrstuvwxyz"
lut = np.zeros(256, dtype=np.int64)
for i, ch in enumerate(ALF):
    lut[ord(ch)] = i
def enc(s):
    return lut[np.frombuffer(s.encode("ascii"), dtype=np.uint8)]
seqs = [enc(c) for c in car_por_romance]
A = 27
KMAX = 8

def ctx_codes(s, j):
    """codigo do contexto de comprimento j que precede cada posicao t >= KMAX"""
    n = len(s)
    c = np.zeros(n - KMAX, dtype=np.int64)
    for d in range(1, j + 1):
        c = c * A + s[KMAX - d: n - d]
    return c

def treinar(s):
    n = len(s)
    nxt = s[KMAX:]
    uni = np.bincount(nxt, minlength=A).astype(float)
    tabelas = []
    for j in range(1, KMAX + 1):
        c = ctx_codes(s, j)
        jk, jc = np.unique(c * A + nxt, return_counts=True)
        ck, ct = np.unique(c, return_counts=True)
        tk, tt = np.unique(jk // A, return_counts=True)   # mesmas chaves que ck
        tabelas.append((jk, jc, ck, ct, tt))
    return uni, tabelas

def busca(keys, vals, q):
    idx = np.searchsorted(keys, q)
    idx = np.clip(idx, 0, len(keys) - 1)
    ok = keys[idx] == q
    return np.where(ok, vals[idx], 0), ok, idx

def avaliar(modelo, s):
    uni, tabelas = modelo
    nxt = s[KMAX:]
    T = len(nxt)
    P = np.tile((uni + 1) / (uni.sum() + A), (T, 1))           # ordem 0: unigrama
    res = []
    def metricas(P):
        pc = P[np.arange(T), nxt]
        pred = P.argmax(1)
        ok = pred == nxt
        return pc, ok
    res.append(metricas(P))
    cand = np.arange(A, dtype=np.int64)
    for j in range(1, KMAX + 1):
        jk, jc, ck, ct, tt = tabelas[j - 1]
        c = ctx_codes(s, j)
        tot, temctx, idx = busca(ck, ct, c)
        tipos = np.where(temctx, tt[idx], 0).astype(float)
        cnt, _, _ = busca(jk, jc, (c[:, None] * A + cand[None, :]))
        den = (tot + tipos)[:, None]
        Pn = np.where(temctx[:, None], (cnt + tipos[:, None] * P) / np.maximum(den, 1), P)
        P = Pn
        res.append(metricas(P))
    return res, nxt

def parametros(modelo):
    uni, tabelas = modelo
    out = [A]
    acc = A
    for (jk, jc, ck, ct, tt) in tabelas:
        acc += len(jk)
        out.append(acc)
    return out

L_LIST = [1, 3, 5, 10]
dobras = []
for i in range(len(seqs)):
    treino = np.concatenate([np.concatenate([seqs[k], [0]]) for k in range(len(seqs)) if k != i])
    teste = seqs[i]
    mod = treinar(treino)
    res, nxt = avaliar(mod, teste)
    prms = parametros(mod)
    linha = []
    sp = (nxt == 0)
    for k, (pc, ok) in enumerate(res):
        H = float(-np.mean(np.log2(pc)))
        phi = float(ok.mean())
        inc = np.concatenate([[0], np.cumsum(~ok)])
        mL = {}
        for L in L_LIST:
            m = (inc[L:] - inc[:-L]) == 0
            mL[L] = float(m.mean())
        # completar a palavra inteira (todas as letras e o espaco final), a partir do inicio da palavra
        ini = np.where((~sp[1:]) & sp[:-1])[0] + 1
        fimp = np.where(sp)[0]
        pos = np.searchsorted(fimp, ini)
        valid = pos < len(fimp)
        ini, fe = ini[valid], fimp[pos[valid]]
        pal_ok = (inc[fe + 1] - inc[ini]) == 0
        linha.append({"k": k, "params": int(prms[k]), "H": H, "phi": phi,
                      "pmean": float(pc.mean()),
                      "m": {str(L): mL[L] for L in L_LIST}, "palavra": float(pal_ok.mean())})
    dobras.append({"teste": titulos[i], "res": linha})
    print(f"dobra {i} ok {time.time()-T0:.0f}s", file=sys.stderr)

def resumo(chave, sub=None):
    out = []
    for k in range(KMAX + 1):
        v = np.array([(d["res"][k][chave] if sub is None else d["res"][k][chave][sub]) for d in dobras])
        out.append({"k": k, "media": float(v.mean()), "min": float(v.min()), "max": float(v.max()),
                    "dp": float(v.std(ddof=1))})
    return out
params_med = [float(np.mean([d["res"][k]["params"] for d in dobras])) for k in range(KMAX + 1)]

# ------------------------------------------------------------------ 4. modelos nulos para Zipf
s_all = " ".join(car_por_romance)
w27 = s_all.split()
fr27 = np.array(sorted(collections.Counter(w27).values(), reverse=True), dtype=float)
a27 = ols_alpha(fr27, 10, 5000)

# (a) digitacao aleatoria com as frequencias de caracteres de Machado
seq_all = enc(s_all)
pch = np.bincount(seq_all, minlength=A) / len(seq_all)
rand = rng.choice(A, size=len(seq_all), p=pch)
rand_s = "".join(ALF[i] for i in rand)
wr = rand_s.split()
frr = np.array(sorted(collections.Counter(wr).values(), reverse=True), dtype=float)
ar_ = ols_alpha(frr, 10, 5000)
top_rand = [w for w, _ in collections.Counter(wr).most_common(8)]

# (b) texto gerado por modelo de n-gramas (contexto de 4 caracteres, maxima verossimilhanca)
KG = 4
ctx = collections.defaultdict(collections.Counter)
for t in range(KG, len(s_all)):
    ctx[s_all[t - KG:t]][s_all[t]] += 1
import bisect
tab = {}
for h, cnt in ctx.items():
    ch = list(cnt.keys()); v = np.array(list(cnt.values()), dtype=float)
    tab[h] = (ch, (np.cumsum(v) / v.sum()).tolist())
gen = list(s_all[:KG])
u = rng.random(len(s_all)).tolist()
h = s_all[:KG]
for t in range(len(s_all) - KG):
    ch, cp = tab[h]
    c = ch[min(bisect.bisect_left(cp, u[t]), len(ch) - 1)]
    gen.append(c)
    h = h[1:] + c
gen_s = "".join(gen)
wg = gen_s.split()
frg = np.array(sorted(collections.Counter(wg).values(), reverse=True), dtype=float)
ag = ols_alpha(frg, 10, 5000)
_v27 = set(w27)
vocab_novo = sum(1 for w in set(wg) if w not in _v27)

def pontos_zipf(fr):
    return [{"posto": k, "freq": int(fr[k - 1])} for k in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000] if k <= len(fr)]

out = {
    "preprocessamento": relatorio,
    "tokens_brutos": brutas_tokens, "tokens": N, "tipos": V,
    "hapax": int((f_sorted == 1).sum()),
    "top5_pct": round(100 * f_sorted[:5].sum() / N, 1),
    "top": [(w, c) for w, c in ranked[:10]],
    "zipf_faixas": zipf_faixas,
    "mle": {"fmin": fmin_opt, "rank_fmin": rank_fmin, "n_cauda": int(n_tail), "beta": round(beta_hat, 3),
            "alfa": round(alpha_mle, 3), "ks": round(ks_d, 4)},
    "bootstrap": {"ols_10_5000_ic95": ci(boot_ols), "mle_alfa_ic95": ci(boot_mle)},
    "alfa_romance": alfa_romance,
    "alfa_romance_resumo": {"media": round(float(ar.mean()), 3), "dp": round(float(ar.std(ddof=1)), 3),
                            "min": round(float(ar.min()), 3), "max": round(float(ar.max()), 3)},
    "zipf_pts": zipf_pts,
    "nulos": {"machado27": {"alfa": round(a27[0], 3), "r2": round(a27[2], 4), "tipos": len(fr27)},
              "aleatorio": {"alfa": round(ar_[0], 3), "r2": round(ar_[2], 4), "tipos": len(frr), "top": top_rand,
                            "p_espaco": round(float(pch[0]), 4)},
              "ngrama4": {"alfa": round(ag[0], 3), "r2": round(ag[2], 4), "tipos": len(frg),
                          "pct_tipos_inexistentes": round(100 * vocab_novo / len(frg), 1),
                          "amostra": gen_s[5000:5400]}},
    "nulos_pontos": {"machado27": pontos_zipf(fr27), "aleatorio": pontos_zipf(frr), "ngrama4": pontos_zipf(frg)},
    "caracteres": {"params": params_med, "H": resumo("H"), "phi": resumo("phi"), "pmean": resumo("pmean"),
                   "m": {str(L): resumo("m", str(L)) for L in L_LIST}, "palavra": resumo("palavra")},
    "segundos": round(time.time() - T0),
}
import os
os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
with open(saida, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f"resultados gravados em {saida} ({out['segundos']} s)")
