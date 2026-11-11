# Proposta do seminário e feedback do professor

## Proposta enviada

**Linguagem como sistema complexo: leis de potência, informação e emergência, do texto humano aos grandes modelos de linguagem**

Esta proposta trata a linguagem natural como um sistema complexo adaptativo e os grandes modelos de linguagem (LLMs) como sistemas complexos artificiais que a aprendem prevendo o próximo símbolo. Com as ferramentas estudadas na disciplina, o trabalho examina quatro assinaturas de complexidade na língua e nos modelos: a redundância informacional medida pela entropia de Shannon; as leis de potência de Zipf e Heaps, ao lado das leis de escala dos modelos; as correlações de longo alcance associadas à criticidade; e o debate sobre as "habilidades emergentes" dos LLMs. Um experimento próprio com os dez romances de Machado de Assis mede essas regularidades em português. A pergunta central é se a emergência observada em LLMs é uma transição de fase real ou um efeito da métrica escolhida. O argumento do trabalho é que essa questão depende, antes de tudo, da escolha do parâmetro de ordem, no sentido da teoria de transições de fase.

**Referências da proposta**

- BECKNER, C. et al. (The "Five Graces Group"). Language is a complex adaptive system: position paper. *Language Learning*, v. 59, supl. 1, p. 1-26, 2009. DOI: 10.1111/j.1467-9922.2009.00532.x.
- WEI, J. et al. Emergent abilities of large language models. *Transactions on Machine Learning Research*, 2022. Disponível em: https://arxiv.org/abs/2206.07682.

## Feedback do professor (resumo)

A proposta foi **aprovada com recomendação de reduzir o escopo**.

Pontos fortes:

- O experimento com os romances de Machado de Assis fornece material próprio e resultados concretos.
- A pergunta sobre emergência real ou efeito da métrica é bem formulada.
- A proposta conecta observações quantitativas a uma questão conceitual sobre transições de fase.

Ajustes pedidos:

1. Selecionar duas ou três ideias centrais, em vez de reunir entropia, Zipf, Heaps, correlações de longo alcance, leis de escala e emergência.
2. Explicar o pré-processamento do corpus e apresentar incertezas ou faixas de ajuste; um expoente próximo de 1, isoladamente, não demonstra um mecanismo específico nem criticalidade.
3. Definir com precisão o parâmetro de ordem proposto e mostrar como ele muda com uma variável de controle.
4. Ao comparar linguagem humana e LLMs, destacar semelhanças observáveis sem pressupor que os mecanismos geradores sejam os mesmos.

Formato: poucas figuras; entropia e leis de potência introduzidas de modo intuitivo; turma com estudantes de Exatas, Biológicas e Humanas; seminário pré-gravado de cerca de 20 minutos, sem ultrapassar esse tempo.

## Como cada ajuste foi atendido

| Ajuste | O que foi feito | Onde |
| --- | --- | --- |
| 1. Escopo | Três ideias: previsibilidade, lei de Zipf e emergência. Saíram Heaps, correlações de longo alcance, criticalidade e leis de escala detalhadas | Artigo, Seção 1; slides 2 e 16 |
| 2. Pré-processamento e incertezas | Seis passos documentados com números; α por cinco faixas, máxima verossimilhança, bootstrap e por romance; dois modelos nulos | Artigo, Seções 2 e 4; slides 5, 10 e 11 |
| 3. Parâmetro de ordem | φ = acerto por caractere; variável de controle g = log₁₀ do número de parâmetros; métrica m_L = acerto exato de L letras; critério de suscetibilidade | Artigo, Seção 5; slides 13 e 14 |
| 4. Observável, não mecanismo | Seção e slide dedicados; tabela do que cada semelhança não autoriza concluir | Artigo, Seções 1 e 6.1; slides 4 e 8 |
| Formato | 3 figuras no deck; entropia como jogo de sim ou não; Zipf com tabela posição × frequência; roteiro de 18 minutos | Slides 6, 7, 9, 11, 14; `docs/roteiro.md` |
