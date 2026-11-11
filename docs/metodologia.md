# Metodologia técnica

Todo o estudo foi feito em **Python 3** com **NumPy** e a biblioteca padrão. Não foram usadas bibliotecas de PLN nem de aprendizado de máquina: os modelos de linguagem foram implementados do zero, com contagens vetorizadas em NumPy. A análise completa roda em cerca de 1 minuto e é reproduzível (semente aleatória fixa, 42).

## Ferramentas

| Ferramenta | Uso |
| --- | --- |
| Python 3 | Linguagem de todo o processamento |
| NumPy | Contagens (`np.unique`, `np.bincount`, `np.searchsorted`), ajustes (`np.polyfit`), sorteios e reamostragens (`Generator.multinomial`, `Generator.choice`) |
| `re`, `unicodedata` | Limpeza do texto: expressões regulares e remoção de acentos |
| `collections`, `glob`, `json`, `bisect` | Contagem de palavras, leitura dos arquivos, saída dos resultados e geração do texto artificial |
| Matplotlib | Figuras do artigo (`src/figuras.py`) |
| Playwright (Chromium) | Exportação opcional da apresentação para PDF (`src/montar_apresentacao.py --pdf`) |

## Etapas

1. **Dados.** Corpus "machado" do NLTK, baixado como .zip do repositório de dados do NLTK (`src/baixar_corpus.py`). Um .txt por romance, codificação Windows-1252.
2. **Pré-processamento.** Remoção dos cabeçalhos editoriais (até o parágrafo "Publicado ..."), das 728 linhas "CAPÍTULO ..." e da marca "FIM". Palavras: minúsculas, letras com acento e hífen interno. Caracteres: sem acentos, alfabeto de 27 símbolos (26 letras e espaço).
3. **Lei de Zipf.**
   - Mínimos quadrados em escala log-log, em cinco faixas de postos, com pontos espaçados logaritmicamente.
   - Máxima verossimilhança para lei de potência discreta (Clauset, Shalizi e Newman, 2009), com f_min escolhido pela distância de Kolmogorov-Smirnov; α = 1/(β − 1).
   - Bootstrap: 500 reamostragens multinomiais das ocorrências.
   - Ajuste separado em cada romance (postos 10 a 1.000).
4. **Modelos nulos.** Digitação aleatória (caracteres i.i.d. com as frequências de Machado) e texto gerado por um modelo de máxima verossimilhança com contexto de 4 letras; o mesmo ajuste de Zipf aplicado aos três textos.
5. **Entropia.** Modelos de n-gramas de caracteres com contexto k = 0 a 8 e interpolação de Witten-Bell. Validação cruzada por romance (treino em 9, teste no 10º, 10 rodadas). Medida: entropia cruzada em bits por caractere.
6. **Parâmetro de ordem.** Nos mesmos modelos: acerto por caractere φ (previsão mais provável) e acerto exato de L letras seguidas (L = 1, 3, 5, 10). Tamanho do modelo = número de contagens armazenadas (27 a 2,7 milhões). Suscetibilidade dφ/d(log₁₀ N) por diferenças finitas. O acerto de palavras inteiras também é calculado, mas não entrou nos resultados.

## Versão inicial (pasta `legado/`)

Antes do feedback do professor, a análise (`legado/analise_v1.py`) usava:

- entropia estimada no próprio texto de treino (valores otimistas, como 1,66 bit com 5 letras);
- compressão bzip2 e LZMA como cota superior da entropia;
- informação mútua entre caracteres distantes (corpus pequeno demais para medir a cauda).

Esses métodos foram substituídos pela validação cruzada e pelo experimento do parâmetro de ordem.

## Limites técnicos

- Nenhum modelo de linguagem grande foi treinado ou avaliado.
- Os resultados dependem das escolhas de pré-processamento descritas acima.
- Com outra semente aleatória, os valores sorteados (bootstrap e modelos nulos) podem variar levemente.
