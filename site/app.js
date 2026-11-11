/* Site do projeto "Linguagem como sistema complexo".
   Lê dados/resultados.json (gerado por src/analise.py) e dados/romances.json
   (gerado por src/extrair_trechos.py) e desenha os gráficos em SVG, sem bibliotecas. */
(() => {
  "use strict";

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const NS = "http://www.w3.org/2000/svg";
  const COR = { azul: "#0b5fa5", amarelo: "#f5b301", tinta: "#1a1a18", cinza: "#a8a59c", cinza2: "#8a877e", grade: "#ebe9e2", borda: "#d6d3ca", mudo: "#5b5952", azulClaro: "#e6eff7" };
  const H_MAX = Math.log2(27);

  const num = (v, casas = 0) => v.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
  const pct = (v, casas = 1) => num(v * 100, casas) + "%";
  const grande = (v) => {
    if (v >= 1e6) return num(v / 1e6, 1) + (v >= 2e6 ? " milhões" : " milhão");
    if (v >= 1e3) return num(Math.round(v / 1e3)) + " mil";
    return num(Math.round(v / 10) * 10);
  };
  const milhoes = grande;

  function svg(tag, attrs = {}, pai) {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    if (pai) pai.appendChild(el);
    return el;
  }
  function texto(pai, x, y, conteudo, attrs = {}) {
    const t = svg("text", { x, y, ...attrs }, pai);
    t.textContent = conteudo;
    return t;
  }
  // largura do desenho = largura real do contêiner (texto legível no celular)
  const largura = (sel, max) => Math.round(Math.max(340, Math.min(max, $(sel).clientWidth || max)));
  const escala = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);

  /* ------------------------------------------------------------------ navegação */
  function navegacao() {
    const topo = $("#topo");
    const links = $$(".topo nav a");
    addEventListener("scroll", () => topo.classList.toggle("rolado", scrollY > 10), { passive: true });
    const obs = new IntersectionObserver((entradas) => {
      for (const e of entradas) {
        if (!e.isIntersecting) continue;
        links.forEach((a) => a.classList.toggle("ativo", a.getAttribute("href") === "#" + e.target.id));
        const ativo = links.find((a) => a.classList.contains("ativo"));
        if (ativo) ativo.scrollIntoView({ block: "nearest", inline: "nearest" });
      }
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main > section[id]").forEach((s) => obs.observe(s));

    const rev = new IntersectionObserver((entradas) => {
      for (const e of entradas) if (e.isIntersecting) { e.target.classList.add("visivel"); rev.unobserve(e.target); }
    }, { rootMargin: "0px 0px -8% 0px" });
    $$(".secao > *:not(.rotulo):not(h2)").forEach((el) => { el.classList.add("revelar"); rev.observe(el); });
  }

  /* ------------------------------------------------------------------ capas */
  const CAPAS = {
    marm01: { fundo: "#f5b301", frente: "#1a1a18", acento: "#ffffff", forma: "circulo" },
    marm02: { fundo: "#f6f5f1", frente: "#1a1a18", acento: "#f5b301", forma: "quadro", linha: true },
    marm03: { fundo: "#0b5fa5", frente: "#f6f5f1", acento: "#f5b301", forma: "meia" },
    marm04: { fundo: "#ebe9e2", frente: "#1a1a18", acento: "#0b5fa5", forma: "faixas" },
    marm05: { fundo: "#1a1a18", frente: "#f6f5f1", acento: "#f5b301", forma: "quadro", linha: true },
    marm06: { fundo: "#f6f5f1", frente: "#1a1a18", acento: "#0b5fa5", forma: "grade" },
    marm07: { fundo: "#0b5fa5", frente: "#ffffff", acento: "#1a1a18", forma: "circulo" },
    marm08: { fundo: "#1a1a18", frente: "#f6f5f1", acento: "#0b5fa5", forma: "circulo", linha: true },
    marm09: { fundo: "#f5b301", frente: "#1a1a18", acento: "#0b5fa5", forma: "faixas" },
    marm10: { fundo: "#0a3d6b", frente: "#f6f5f1", acento: "#f5b301", forma: "meia" },
  };
  function capa(r) {
    const c = CAPAS[r.id];
    const el = document.createElement("div");
    el.className = "capa-livro";
    el.style.cssText = `--fundo:${c.fundo};--frente:${c.frente};--acento:${c.acento}`;
    el.setAttribute("aria-hidden", "true");
    el.innerHTML = `
      <span class="cl-forma forma-${c.forma}"></span>${c.linha ? '<span class="cl-linha"></span>' : ""}
      <span class="cl-autor">Machado de Assis</span>
      <span class="cl-titulo${r.titulo.length > 18 ? " longo" : ""}">${r.titulo}</span>
      <span class="cl-ano">${r.ano}<small>${r.fase}</small></span>`;
    return el;
  }

  /* ------------------------------------------------------------------ corpus e romances */
  let ROMANCES = [];
  let atual = 0;

  function corpus() {
    const alvo = $("#grafico-corpus");
    const max = Math.max(...ROMANCES.map((r) => r.palavras));
    ROMANCES.forEach((r, i) => {
      const b = document.createElement("button");
      b.className = "barra";
      b.type = "button";
      b.setAttribute("role", "listitem");
      b.setAttribute("aria-label", `${r.titulo}, ${r.ano}: ${num(r.palavras)} palavras. Abrir trecho.`);
      b.innerHTML = `<span class="barra-nome">${r.titulo}<small>${r.ano}</small></span>
        <span class="barra-trilho"><span class="barra-preench" style="background:${r.fase === "realista" ? COR.azul : COR.amarelo}"></span></span>
        <span class="barra-v">${num(r.palavras)}</span>`;
      b.addEventListener("click", () => abrir(i));
      alvo.appendChild(b);
    });
    const obs = new IntersectionObserver((e) => {
      if (!e[0].isIntersecting) return;
      $$(".barra-preench", alvo).forEach((el, i) => setTimeout(() => (el.style.width = (ROMANCES[i].palavras / max) * 100 + "%"), i * 60));
      obs.disconnect();
    }, { threshold: 0.3 });
    obs.observe(alvo);
  }

  function estante() {
    const alvo = $("#estante");
    ROMANCES.forEach((r, i) => {
      const b = document.createElement("button");
      b.className = "livro";
      b.type = "button";
      b.dataset.fase = r.fase;
      b.setAttribute("aria-label", `${r.titulo} (${r.ano}): abrir trecho e resumo`);
      b.appendChild(capa(r));
      const info = document.createElement("span");
      info.className = "livro-info";
      info.innerHTML = `<strong>${r.titulo}</strong><span>${r.data} · ${num(r.palavras)} palavras</span>`;
      b.appendChild(info);
      b.addEventListener("click", () => abrir(i));
      alvo.appendChild(b);
    });
    $$("[data-fase]").forEach((chip) => {
      if (!chip.classList.contains("chip")) return;
      chip.addEventListener("click", () => {
        $$(".chip[data-fase]").forEach((c) => c.classList.toggle("ativo", c === chip));
        const f = chip.dataset.fase;
        $$(".livro").forEach((l) => l.classList.toggle("oculto", f !== "todas" && l.dataset.fase !== f));
      });
    });
  }

  function abrir(i) {
    atual = (i + ROMANCES.length) % ROMANCES.length;
    const r = ROMANCES[atual];
    $("#modal-capa").replaceChildren(capa(r));
    $("#modal-rotulo").textContent = `${atual + 1} de ${ROMANCES.length} · fase ${r.fase} · ${r.data}`;
    $("#modal-titulo").textContent = r.titulo;
    $("#modal-trecho").textContent = r.trecho;
    $("#modal-resumo").textContent = r.resumo;
    $("#modal-numeros").innerHTML = `
      <div><strong>${num(r.palavras)}</strong>palavras</div>
      <div><strong>${num(r.alfa, 2)}</strong>α de Zipf (postos 10 a 1.000)</div>
      <div><strong>${pct(r.palavras / 525067)}</strong>do corpus</div>`;
    const m = $("#modal");
    if (!m.open) m.showModal();
    $(".modal-corpo", m).scrollTop = 0;
    m.scrollTop = 0;
  }
  function modal() {
    const m = $("#modal");
    $("#modal-fechar").addEventListener("click", () => m.close());
    $("#modal-ant").addEventListener("click", () => abrir(atual - 1));
    $("#modal-prox").addEventListener("click", () => abrir(atual + 1));
    m.addEventListener("click", (e) => { if (e.target === m) m.close(); });
    m.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") abrir(atual + 1);
      if (e.key === "ArrowLeft") abrir(atual - 1);
    });
  }

  /* ------------------------------------------------------------------ jogo */
  function para27(t) {
    return t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z]+/g, " ").replace(/\s+/g, " ").trim();
  }
  function jogo() {
    const fontes = ROMANCES.map((r) => ({ titulo: r.titulo, texto: para27(r.trecho) }));
    let fonte = fontes.findIndex((f) => f.titulo === "Dom Casmurro");
    let alvo = "", pos = 0, letras = 0, tentativas = 0, tentouAqui = [];
    const input = $("#jogo-input"), cursor = $("#jogo-cursor");

    function novo(i) {
      fonte = i;
      const t = fontes[i].texto;
      const ini = 0;
      alvo = t.slice(ini, ini + 150);
      alvo = alvo.slice(0, alvo.lastIndexOf(" ") > 100 ? alvo.lastIndexOf(" ") : alvo.length);
      pos = 0; letras = 0; tentativas = 0; tentouAqui = [];
      $("#jogo-fonte").textContent = fontes[i].titulo;
      // revela as primeiras palavras como contexto
      pos = alvo.indexOf(" ", 18) + 1;
      desenhar();
    }
    function desenhar(estado) {
      $("#jogo-feito").textContent = alvo.slice(0, pos);
      $("#jogo-resto").textContent = alvo.slice(pos + 1);
      const fim = pos >= alvo.length;
      cursor.textContent = fim ? "✓" : "?";
      cursor.className = "jogo-cursor" + (estado ? " " + estado : "");
      $("#jogo-letras").textContent = letras;
      $("#jogo-tentativas").textContent = tentativas;
      $("#jogo-media").textContent = letras ? num(tentativas / letras, 2) : "–";
      $("#jogo-tentou").textContent = fim
        ? `Fim do trecho. Sem contexto, um chute às cegas entre 27 símbolos levaria em média 14 tentativas por letra.`
        : tentouAqui.length ? "Já tentou: " + tentouAqui.map((c) => (c === " " ? "espaço" : c)).join(", ") : "";
    }
    function chutar(c) {
      if (pos >= alvo.length) return;
      c = para27(c) || (c === " " ? " " : "");
      if (c === "" || tentouAqui.includes(c)) return;
      tentativas++;
      if (c === alvo[pos]) {
        letras++; pos++; tentouAqui = [];
        desenhar("acerto");
      } else {
        tentouAqui.push(c);
        desenhar("erro");
      }
    }
    input.addEventListener("keydown", (e) => {
      if (e.key === " ") { e.preventDefault(); chutar(" "); }
    });
    input.addEventListener("input", () => {
      const v = input.value;
      input.value = "";
      if (v) chutar(v.slice(-1));
    });
    $("#jogo-dica").addEventListener("click", () => {
      if (pos >= alvo.length) return;
      tentativas += 27 - tentouAqui.length > 0 ? Math.ceil((27 - tentouAqui.length) / 2) : 1;
      letras++; pos++; tentouAqui = [];
      desenhar("acerto");
      input.focus({ preventScroll: true });
    });
    $("#jogo-novo").addEventListener("click", () => {
      novo((fonte + 1 + Math.floor(Math.random() * (fontes.length - 1))) % fontes.length);
      input.focus({ preventScroll: true });
    });
    $(".jogo-texto").addEventListener("click", () => input.focus({ preventScroll: true }));
    novo(fonte < 0 ? 0 : fonte);
  }

  /* ------------------------------------------------------------------ entropia */
  function entropia(R) {
    const H = R.caracteres.H;
    const W = largura("#grafico-entropia", 640), A = W < 560 ? 320 : 360, m = { e: 44, d: 16, t: 20, b: 50 };
    const x = escala(0, 8, m.e, W - m.d), y = escala(0, 5, A - m.b, m.t);
    const s = svg("svg", { viewBox: `0 0 ${W} ${A}`, role: "img", "aria-label": "Entropia cruzada em bits por caractere contra o número de letras de contexto: cai de 3,93 sem contexto para 1,93 com 5 letras e volta a subir depois." });
    for (let v = 0; v <= 5; v++) {
      svg("line", { x1: m.e, x2: W - m.d, y1: y(v), y2: y(v), stroke: v === 0 ? COR.cinza2 : COR.grade, "stroke-width": v === 0 ? 1.5 : 1 }, s);
      texto(s, m.e - 10, y(v) + 4, num(v), { "text-anchor": "end" });
    }
    for (let k = 0; k <= 8; k++) texto(s, x(k), A - m.b + 22, k, { "text-anchor": "middle" });
    texto(s, (m.e + W - m.d) / 2, A - 6, "letras de contexto (k)", { "text-anchor": "middle", class: "eixo-titulo" });
    texto(s, m.e, 10, "bits por caractere", { class: "eixo-titulo" });
    // referência: uniforme
    svg("line", { x1: m.e, x2: W - m.d, y1: y(H_MAX), y2: y(H_MAX), stroke: COR.cinza2, "stroke-dasharray": "6 6", "stroke-width": 1.5 }, s);
    texto(s, W - m.d, y(H_MAX) - 8, "sem informação: 4,75", { "text-anchor": "end" });
    svg("line", { x1: m.e, x2: W - m.d, y1: y(1), y2: y(1), stroke: COR.amarelo, "stroke-dasharray": "6 6", "stroke-width": 2 }, s);
    texto(s, W - m.d, y(1) - 8, "Shannon, inglês: ~1", { "text-anchor": "end" });
    // faixa entre romances
    const faixa = H.map((h) => `${x(h.k)},${y(h.max)}`).concat([...H].reverse().map((h) => `${x(h.k)},${y(h.min)}`));
    svg("polygon", { points: faixa.join(" "), fill: COR.azulClaro }, s);
    svg("polyline", { points: H.map((h) => `${x(h.k)},${y(h.media)}`).join(" "), fill: "none", stroke: COR.azul, "stroke-width": 3.5, "stroke-linejoin": "round" }, s);
    const guia = svg("line", { y1: m.t, y2: A - m.b, stroke: COR.tinta, "stroke-width": 1, "stroke-dasharray": "3 4" }, s);
    const pts = H.map((h) => {
      const c = svg("circle", { cx: x(h.k), cy: y(h.media), r: 6, fill: COR.azul, stroke: "#fff", "stroke-width": 2, style: "cursor:pointer" }, s);
      c.addEventListener("click", () => { slider.value = h.k; atualizar(); });
      return c;
    });
    $("#grafico-entropia").appendChild(s);

    const slider = $("#k-slider");
    function atualizar() {
      const k = +slider.value, h = H[k];
      $("#k-valor").textContent = k;
      $("#k-bits").textContent = num(h.media, 2);
      $("#k-medidor").style.width = (h.media / H_MAX) * 100 + "%";
      const red = 1 - h.media / H_MAX;
      const equiv = Math.pow(2, h.media);
      $("#k-texto").innerHTML = `Redundância de <strong>${pct(red, 0)}</strong>. Com ${k === 0 ? "nenhuma letra" : k === 1 ? "1 letra" : k + " letras"} de contexto, a incerteza equivale a escolher entre <strong>~${num(equiv, 1)}</strong> letras igualmente prováveis, em vez de 27.`;
      $("#k-faixa").textContent = `Entre os romances de teste: ${num(h.min, 2)} a ${num(h.max, 2)} bits.` + (k >= 6 ? " Contexto longo demais para o corpus: o modelo começa a decorar." : k === 5 ? " Melhor estimativa." : "");
      guia.setAttribute("x1", x(k)); guia.setAttribute("x2", x(k));
      pts.forEach((c, i) => { c.setAttribute("r", i === k ? 10 : 6); c.setAttribute("fill", i === k ? COR.tinta : COR.azul); });
    }
    slider.addEventListener("input", atualizar);
    atualizar();
  }

  /* ------------------------------------------------------------------ zipf */
  function zipf(R) {
    const series = {
      machado27: { pts: R.zipf_pts, cor: COR.azul, larg: 5, nome: "Machado de Assis" },
      ngrama4: { pts: R.nulos_pontos.ngrama4, cor: COR.tinta, larg: 2.5, tracejado: "8 6", nome: "Texto gerado por n-gramas" },
      aleatorio: { pts: R.nulos_pontos.aleatorio, cor: COR.cinza, larg: 3.5, nome: "Digitação aleatória" },
    };
    const W = largura("#grafico-zipf", 900), A = W < 600 ? 360 : 480, m = { e: 52, d: 20, t: 24, b: 56 };
    const lx = escala(0, Math.log10(30000), m.e, W - m.d), ly = escala(0, Math.log10(40000), A - m.b, m.t);
    const x = (v) => lx(Math.log10(v)), y = (v) => ly(Math.log10(v));
    const s = svg("svg", { viewBox: `0 0 ${W} ${A}`, role: "img", "aria-label": "Lei de Zipf em escala log-log: Machado, texto gerado por n-gramas e digitação aleatória têm inclinações quase iguais." });
    const sup = ["⁰", "¹", "²", "³", "⁴"];
    for (let e = 0; e <= 4; e++) {
      svg("line", { x1: x(10 ** e), x2: x(10 ** e), y1: m.t, y2: A - m.b, stroke: COR.grade }, s);
      svg("line", { x1: m.e, x2: W - m.d, y1: y(10 ** e), y2: y(10 ** e), stroke: e === 0 ? COR.cinza2 : COR.grade }, s);
      texto(s, x(10 ** e), A - m.b + 22, "10" + sup[e], { "text-anchor": "middle" });
      texto(s, m.e - 10, y(10 ** e) + 4, "10" + sup[e], { "text-anchor": "end" });
    }
    texto(s, (m.e + W - m.d) / 2, A - 8, "posto da palavra (1 = mais frequente)", { "text-anchor": "middle", class: "eixo-titulo" });
    texto(s, m.e, 12, "ocorrências", { class: "eixo-titulo" });
    const faixa = svg("rect", { y: m.t, height: A - m.b - m.t, fill: COR.amarelo, opacity: 0, rx: 6 }, s);
    const faixaTxt = texto(s, 0, m.t + 18, "", { "text-anchor": "middle", style: "font-weight:600;fill:#1a1a18" });
    // reta de referência com inclinação -1
    svg("line", { x1: x(1), y1: y(40000), x2: x(30000), y2: y(40000 / 30000), stroke: COR.borda, "stroke-width": 1.5, "stroke-dasharray": "2 6" }, s);
    if (W >= 600) texto(s, x(8000), y(40000 / 8000) + 22, "inclinação −1", { fill: COR.cinza2, "text-anchor": "middle" });

    const grupos = {};
    for (const [id, se] of Object.entries(series).reverse()) {
      const g = svg("g", { "data-serie": id, style: "transition:opacity .25s" }, s);
      svg("polyline", { points: se.pts.map((p) => `${x(p.posto)},${y(p.freq)}`).join(" "), fill: "none", stroke: se.cor, "stroke-width": se.larg, "stroke-linejoin": "round", ...(se.tracejado ? { "stroke-dasharray": se.tracejado } : {}) }, g);
      se.pts.forEach((p) => {
        const c = svg("circle", { cx: x(p.posto), cy: y(p.freq), r: id === "machado27" ? 6 : 4, fill: se.cor, stroke: "#fff", "stroke-width": id === "machado27" ? 2 : 0 }, g);
        if (id === "machado27") {
          c.style.cursor = "pointer";
          const mostra = () => dica(c, `<b>“${p.palavra}”</b> · posto ${num(p.posto)} · ${num(p.freq)} ocorrências`);
          c.addEventListener("mouseenter", mostra);
          c.addEventListener("focus", mostra);
          c.addEventListener("mouseleave", esconde);
          c.addEventListener("blur", esconde);
          c.setAttribute("tabindex", "0");
        }
      });
      grupos[id] = g;
    }
    const alvo = $("#grafico-zipf");
    alvo.appendChild(s);
    const caixa = $("#zipf-dica");
    function dica(el, html) {
      const r = el.getBoundingClientRect(), p = alvo.parentElement.getBoundingClientRect();
      caixa.innerHTML = html;
      caixa.hidden = false;
      caixa.style.left = r.left + r.width / 2 - p.left + "px";
      caixa.style.top = r.top - p.top + "px";
    }
    function esconde() { caixa.hidden = true; }

    $$(".chip[data-serie]").forEach((chip) =>
      chip.addEventListener("click", () => {
        chip.classList.toggle("ativo");
        grupos[chip.dataset.serie].style.opacity = chip.classList.contains("ativo") ? 1 : 0.06;
      })
    );

    $("#amostra-ngrama").textContent = "“" + R.nulos.ngrama4.amostra.split(" ").slice(0, 28).join(" ") + " …”";
    $("#pct-inexistentes").textContent = num(R.nulos.ngrama4.pct_tipos_inexistentes, 1) + "%";

    // escala de α por método
    const fx = R.zipf_faixas.filter((f) => f.faixa !== "1-10000");
    const ar = R.alfa_romance_resumo;
    const linhas = fx.map((f) => {
      const [a, b] = f.faixa.split("-").map(Number);
      return { nome: `Mínimos quadrados`, sub: `postos ${num(a)} a ${num(b)}`, alfa: f.alfa, ic: f.faixa === "10-5000" ? R.bootstrap.ols_10_5000_ic95 : null, faixa: [a, b] };
    });
    linhas.push({ nome: "Máxima verossimilhança", sub: `${num(R.mle.n_cauda)} palavras com ≥ ${R.mle.fmin} ocorrências`, alfa: R.mle.alfa, ic: R.bootstrap.mle_alfa_ic95, faixa: [1, R.mle.rank_fmin] });
    linhas.push({ nome: "Um romance por vez", sub: `postos 10 a 1.000 · média ${num(ar.media, 2)}`, alfa: ar.media, ic: [ar.min, ar.max], faixa: [10, 1000] });
    const ex = escala(0.92, 1.18, 0, 100);
    const tab = $("#tabela-alfa");
    const botoes = linhas.map((l) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "alfa-linha";
      b.innerHTML = `<span class="alfa-nome">${l.nome}<small>${l.sub}</small></span>
        <span class="alfa-trilho"><span class="alfa-um" style="left:${ex(1)}%"></span>
        ${l.ic ? `<span class="alfa-ic" style="left:${ex(l.ic[0])}%;width:${Math.max(ex(l.ic[1]) - ex(l.ic[0]), 1)}%"></span>` : ""}
        <span class="alfa-ponto" style="left:${ex(l.alfa)}%"></span></span>
        <span class="alfa-v">${num(l.alfa, 2)}</span>`;
      b.addEventListener("click", () => {
        const ativo = !b.classList.contains("ativo");
        botoes.forEach((o) => o.classList.remove("ativo"));
        b.classList.toggle("ativo", ativo);
        if (ativo) {
          faixa.setAttribute("x", x(l.faixa[0]));
          faixa.setAttribute("width", x(l.faixa[1]) - x(l.faixa[0]));
          faixa.setAttribute("opacity", 0.22);
          faixaTxt.setAttribute("x", (x(l.faixa[0]) + x(l.faixa[1])) / 2);
          faixaTxt.textContent = `α = ${num(l.alfa, 2)}`;
        } else {
          faixa.setAttribute("opacity", 0);
          faixaTxt.textContent = "";
        }
      });
      tab.appendChild(b);
      return b;
    });
    const eixo = document.createElement("div");
    eixo.className = "alfa-linha";
    eixo.style.cursor = "default";
    eixo.innerHTML = `<span></span><span class="alfa-trilho pequeno mudo" style="height:auto">${[0.95, 1, 1.05, 1.1, 1.15].map((v) => `<span style="position:absolute;left:${ex(v)}%;transform:translateX(-50%)">${num(v, 2)}</span>`).join("")}&nbsp;</span><span></span>`;
    tab.appendChild(eixo);
  }

  /* ------------------------------------------------------------------ parâmetro de ordem */
  function fase(R) {
    const C = R.caracteres;
    const P = C.params, phi = C.phi.map((p) => p.media);
    const medidos = Object.fromEntries(Object.entries(C.m).map(([L, v]) => [L, v.map((p) => p.media)]));
    const W = largura("#grafico-fase", 900), A = W < 600 ? 360 : 460, m = { e: 52, d: 24, t: 28, b: 56 };
    const x = escala(Math.log10(20), Math.log10(4e6), m.e, W - m.d), y = escala(0, 1, A - m.b, m.t);
    const s = svg("svg", { viewBox: `0 0 ${W} ${A}`, role: "img", "aria-label": "Em porcentagem do valor final, o acerto por letra cresce cedo e suave, enquanto o acerto exato de L letras fica em zero e sobe de repente nos maiores modelos." });
    for (const v of [0, 0.25, 0.5, 0.75, 1]) {
      svg("line", { x1: m.e, x2: W - m.d, y1: y(v), y2: y(v), stroke: v === 0 ? COR.cinza2 : v === 0.5 ? COR.cinza2 : COR.grade, "stroke-dasharray": v === 0.5 ? "8 6" : "", "stroke-width": v === 0.5 ? 1.5 : 1 }, s);
      texto(s, m.e - 10, y(v) + 4, num(v * 100) + "%", { "text-anchor": "end" });
    }
    texto(s, m.e + 8, y(0.5) - 8, "metade", {});
    [[100, "100"], [1e3, "1 mil"], [1e4, "10 mil"], [1e5, "100 mil"], [1e6, "1 milhão"]].forEach(([v, r]) => {
      svg("line", { x1: x(Math.log10(v)), x2: x(Math.log10(v)), y1: A - m.b, y2: A - m.b + 6, stroke: COR.cinza2 }, s);
      texto(s, x(Math.log10(v)), A - m.b + 24, r, { "text-anchor": "middle" });
    });
    texto(s, (m.e + W - m.d) / 2, A - 8, "número de parâmetros do modelo (escala log)", { "text-anchor": "middle", class: "eixo-titulo" });
    texto(s, m.e, 14, "% do valor alcançado pelo maior modelo", { class: "eixo-titulo" });

    const lx = P.map((p) => x(Math.log10(p)));
    const linha = (vals, attrs) => svg("polyline", { points: vals.map((v, i) => `${lx[i]},${y(v)}`).join(" "), fill: "none", "stroke-linejoin": "round", ...attrs }, s);
    const marcaMeioPrev = svg("line", { stroke: COR.tinta, "stroke-width": 1.5, "stroke-dasharray": "3 4" }, s);
    const prev = linha(phi, { stroke: COR.tinta, "stroke-width": 4, "stroke-dasharray": "12 8", style: "transition:all .3s" });
    const med = linha(phi, { stroke: COR.amarelo, "stroke-width": 5 });
    const medPts = svg("g", {}, s);
    const phiN = phi.map((v) => v / phi.at(-1));
    linha(phiN, { stroke: COR.azul, "stroke-width": 6 });
    phiN.forEach((v, i) => svg("circle", { cx: lx[i], cy: y(v), r: 7, fill: COR.azul, stroke: "#fff", "stroke-width": 2 }, s));
    $("#grafico-fase").appendChild(s);

    // ponto onde uma curva normalizada cruza 50%, interpolado em log(parâmetros)
    function meio(vals) {
      for (let i = 1; i < vals.length; i++) {
        if (vals[i] >= 0.5) {
          const a = Math.log10(P[i - 1]), b = Math.log10(P[i]);
          const t = (0.5 - vals[i - 1]) / (vals[i] - vals[i - 1]);
          return 10 ** (a + t * (b - a));
        }
      }
      return P.at(-1);
    }
    // para o texto, o modelo medido mais próximo do cruzamento (como no artigo)
    const proximo = (v) => P.reduce((a, b) => (Math.abs(Math.log10(b / v)) < Math.abs(Math.log10(a / v)) ? b : a));
    $("#meio-phi").textContent = "~" + grande(proximo(meio(phiN)));

    const slider = $("#l-slider");
    function atualizar() {
      const L = +slider.value;
      $("#l-valor").textContent = L;
      const pred = phi.map((v) => (v ** L) / (phi.at(-1) ** L));
      prev.setAttribute("points", pred.map((v, i) => `${lx[i]},${y(v)}`).join(" "));
      const temMedido = medidos[L] && L > 1;
      const serie = temMedido ? medidos[L].map((v) => v / medidos[L].at(-1)) : null;
      med.style.display = temMedido ? "" : "none";
      medPts.replaceChildren();
      if (temMedido) {
        med.setAttribute("points", serie.map((v, i) => `${lx[i]},${y(v)}`).join(" "));
        serie.forEach((v, i) => svg("circle", { cx: lx[i], cy: y(v), r: 5, fill: COR.amarelo, stroke: COR.tinta, "stroke-width": 1.5 }, medPts));
      }
      $("#chip-medido").style.opacity = temMedido ? 1 : 0.45;
      const mp = meio(serie || pred);
      marcaMeioPrev.setAttribute("x1", x(Math.log10(mp))); marcaMeioPrev.setAttribute("x2", x(Math.log10(mp)));
      marcaMeioPrev.setAttribute("y1", y(0.5)); marcaMeioPrev.setAttribute("y2", A - m.b);
      $("#meio-l").textContent = "~" + milhoes(proximo(mp));
      const fin = phi.at(-1) ** L;
      $("#phi-l-final").textContent = pct(fin, fin < 0.01 ? 2 : 1) + (temMedido ? ` (medido: ${pct(medidos[L].at(-1), medidos[L].at(-1) < 0.01 ? 2 : 1)})` : "");
    }
    slider.addEventListener("input", atualizar);
    atualizar();
  }

  /* ------------------------------------------------------------------ início */
  async function iniciar() {
    navegacao();
    modal();
    try {
      const [R, romances] = await Promise.all([
        fetch("dados/resultados.json").then((r) => r.json()),
        fetch("dados/romances.json").then((r) => r.json()),
      ]);
      ROMANCES = romances;
      corpus();
      estante();
      jogo();
      entropia(R);
      zipf(R);
      fase(R);
    } catch (e) {
      console.error(e);
      document.querySelectorAll(".grafico, .grafico-barras, .estante").forEach((el) => {
        el.innerHTML = '<p class="mudo">Não foi possível carregar os dados. Abra o site por um servidor (python src/montar_site.py e python -m http.server 8000 -d _site).</p>';
      });
    }
  }
  iniciar();
})();
