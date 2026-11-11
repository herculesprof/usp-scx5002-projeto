# Roteiro do seminário: Linguagem como sistema complexo

Hercules Ramos · seminário pré-gravado · 18 minutos

## Como usar este roteiro

O texto tem cerca de 2.300 palavras e foi calculado para **18 minutos** lidos num ritmo calmo, de cerca de 130 palavras por minuto, com pequenas pausas para trocar de slide. Cada slide traz o tempo que ele ocupa e o tempo acumulado no fim dele, para você conferir o relógio durante a gravação.

- **[entre colchetes]** estão as ações: trocar de slide, apontar para uma parte do gráfico, fazer uma pausa.
- *Frases em itálico* são opcionais. Se estiver atrasado, pule-as; elas somam cerca de 1 minuto.
- Números foram escritos como se falam, para não tropeçar na leitura.

| Ponto de controle | Tempo acumulado |
| --- | --- |
| Fim da abertura (slide 5) | 3:45 |
| Fim da Ideia 1 (slide 8) | 7:05 |
| Fim da Ideia 2 (slide 11) | 10:40 |
| Fim da Ideia 3 (slide 15) | 16:05 |
| Fim do vídeo (slide 18) | 18:00 |

## Abertura

### Slide 1 · Capa · 20 s · acumulado 0:20

Olá. Meu nome é Hercules Ramos, sou aluno especial da disciplina Sistemas Complexos I, aqui na EACH. Neste seminário, eu trato a linguagem como um sistema complexo e uso os dez romances de Machado de Assis para discutir uma pergunta bem atual sobre inteligência artificial.

**[troque de slide]**

### Slide 2 · Uma pergunta, três ideias · 35 s · acumulado 0:55

A pergunta é esta: quando os grandes modelos de linguagem, como os que estão por trás dos chatbots, parecem ganhar uma habilidade de repente, isso é uma transição de fase, como a água que vira gelo? Ou é um efeito da régua que usamos para medir?

Para chegar lá, vou passar por três ideias, todas medidas nos romances de Machado. Primeiro, a previsibilidade do texto. Segundo, a lei de Zipf. E terceiro, a emergência, com um parâmetro de ordem definido e medido.

**[troque de slide]**

### Slide 3 · A linguagem é um sistema adaptativo · 50 s · acumulado 1:45

Por que tratar a linguagem como sistema complexo? Em 2009, um grupo de dez pesquisadores, entre eles John Holland, propôs exatamente isso.

**[aponte para os três blocos, da esquerda para a direita]**

Há muitos agentes, os falantes, que interagem sem nenhum controle central. Ninguém decide sozinho como a língua funciona. O uso repetido reforça certas formas e certos padrões. E desse uso nasce a estrutura: a gramática e as convenções, que depois voltam a moldar a forma como falamos. *É o mesmo ciclo de realimentação que vimos na unidade de auto-organização.*

Os modelos de linguagem aprendem essa estrutura a partir de textos. Por isso faz sentido compará-los com a língua.

**[troque de slide]**

### Slide 4 · Comparar o observável, não o mecanismo · 40 s · acumulado 2:25

Mas, antes dos dados, uma precaução. Quando eu comparar a linguagem humana com os modelos, vou comparar só o que dá para medir no texto: quanto o contexto reduz a incerteza, como as frequências das palavras se distribuem, e como o desempenho muda quando o modelo cresce.

Não vou supor que um cérebro e uma rede neural funcionem do mesmo jeito. Nem que estatísticas parecidas tenham a mesma causa. Na segunda ideia, vamos ver um exemplo concreto disso.

**[troque de slide]**

### Slide 5 · Do arquivo ao dado · 1 min 20 s · acumulado 3:45

Os dados são os dez romances de Machado de Assis, de "Ressurreição", de mil oitocentos e setenta e dois, a "Memorial de Aires", de mil novecentos e oito. Todos estão em domínio público.

**[aponte para a lista de passos]**

Antes de medir qualquer coisa, preparei o texto em cinco passos.

Um: li os arquivos na codificação original, para não perder os acentos.

Dois: tirei o que não é texto do autor. Os cabeçalhos da editora, setecentos e vinte e oito títulos de capítulo e a palavra "FIM" no final de cada livro. Os prefácios escritos pelo próprio Machado ficaram.

Três: para contar palavras, coloquei tudo em minúsculas, e uma palavra é uma sequência de letras. Formas como "diga-me" contam como uma palavra só.

Quatro: para medir letras, tirei os acentos e fiquei com vinte e sete símbolos, as vinte e seis letras e o espaço, como Shannon fez em mil novecentos e cinquenta e um.

Cinco: os modelos são treinados em nove romances e testados no décimo, que eles nunca viram. E isso se repete dez vezes, uma para cada romance.

**[aponte para os números à direita]**

No fim, são quinhentas e vinte e cinco mil palavras, trinta e uma mil delas diferentes, e cerca de dois vírgula nove milhões de letras. *Essas escolhas mexem um pouco nos resultados, e todas estão descritas no artigo.*

**[troque de slide]**

## Ideia 1 · Previsibilidade

### Slide 6 · Entropia como jogo de sim ou não · 1 min 5 s · acumulado 4:50

Primeira ideia: previsibilidade.

Imagine um jogo. Alguém esconde a próxima letra de um texto, e você tenta descobrir qual é fazendo perguntas de sim ou não. É uma vogal? Vem antes do "m"? A entropia é o número médio de perguntas que você precisa fazer. A unidade dessa medida é o bit: um bit é uma pergunta de sim ou não bem escolhida.

**[aponte para os três cartões, da esquerda para a direita]**

Se você não sabe nada, e os vinte e sete símbolos são igualmente prováveis, precisa de cerca de quatro vírgula setenta e cinco perguntas. Se você sabe que o espaço e a letra "a" são comuns, e que o "z" é raro, já precisa de menos: em Machado, três vírgula noventa e três.

**[aponte para o exemplo "pens"]**

E se você conhece as letras anteriores, precisa de bem menos. Depois de "p, e, n, s", a próxima letra é quase sempre "a". A diferença entre o máximo e o valor real se chama redundância: é a parte do texto que a estrutura da língua já decidiu por nós.

**[troque de slide]**

### Slide 7 · Com 5 letras de contexto: 1,93 bit · 1 min 25 s · acumulado 6:15

Para medir isso em Machado, treinei modelos simples. Eles olham as k letras anteriores e calculam a chance de cada letra seguinte. Fiz isso com k de zero a oito. Cada modelo foi treinado em nove romances e avaliado no décimo.

**[aponte para o eixo horizontal, depois para a curva]**

No eixo horizontal está quantas letras de contexto o modelo usa. No eixo vertical, quantos bits ele precisa, em média, para acertar a letra verdadeira. Sem contexto, três vírgula noventa e três. A curva desce depressa.

**[aponte para o ponto azul]**

Com cinco letras de contexto, chega a um vírgula noventa e três bit por letra. Entre os dez romances de teste, o valor varia de um vírgula oitenta e seis a dois vírgula zero um. Isso quer dizer que pelo menos cinquenta e nove por cento do texto é redundante.

Repare que, com mais de cinco letras, a curva volta a subir. Combinações tão longas ficam raras demais nos dados, e o modelo passa a decorar em vez de generalizar. Então, um vírgula noventa e três é um limite superior, imposto pelo tamanho do corpus e pela simplicidade do modelo, e não pela língua.

**[aponte para a linha de baixo]**

*Shannon, com leitores humanos de inglês e contexto longo, chegou perto de um bit. A comparação é só indicativa, porque são línguas e métodos diferentes.*

**[troque de slide]**

### Slide 8 · Do jogo de Shannon ao treino de LLMs · 50 s · acumulado 7:05

Essa medida liga a língua aos modelos de linguagem.

**[aponte para o cartão da esquerda, depois para o da direita]**

Shannon estimou a entropia do inglês pedindo a pessoas que adivinhassem a próxima letra, conhecendo o texto anterior. Um modelo de linguagem é treinado exatamente nessa tarefa: prever o próximo pedaço de texto. E o que ele minimiza no treino é a entropia cruzada, a mesma grandeza que acabamos de medir.

Por isso dá para comparar humanos, modelos simples como os meus e grandes modelos com a mesma régua, em bits.

**[aponte para a faixa amarela]**

Mas atenção: é a mesma tarefa, não o mesmo mecanismo. Um leitor humano, uma tabela de contagens e uma rede neural podem chegar a números parecidos por caminhos completamente diferentes.

**[troque de slide]**

## Ideia 2 · Lei de Zipf

### Slide 9 · Poucas palavras comuns, muitas raras · 1 min 20 s · acumulado 8:25

Segunda ideia: a lei de Zipf.

Em qualquer texto grande, poucas palavras são usadíssimas, e uma multidão de palavras é rara.

**[aponte para os dois cartões]**

Em Machado, só cinco palavras, "a", "que", "de", "e" e "o", somam dezessete por cento de tudo o que ele escreveu nesses romances. E quase metade das palavras diferentes aparece uma única vez.

O linguista George Zipf notou uma regularidade nisso. Quando a posição de uma palavra no ranking multiplica por dez, a frequência dela se divide por cerca de dez. Em Machado, a palavra na posição cem aparece quinhentas e sessenta e oito vezes. A da posição mil, cinquenta e seis vezes.

**[aponte para a última coluna da tabela]**

Na tabela, multiplicando a posição pelo número de vezes, o resultado fica parecido, entre quarenta e oito mil e cinquenta e nove mil. Isso é uma lei de potência, com expoente perto de um. *É a mesma família de relações que aparece no tamanho das cidades e das empresas.*

Mas a regra não é perfeita, principalmente nas pontas. E é aí que entra a pergunta da incerteza.

**[troque de slide]**

### Slide 10 · Quanto vale α? · 1 min · acumulado 9:25

Quanto vale o expoente em Machado? A resposta honesta é: depende de como se mede.

**[aponte para a primeira e a quarta linha da tabela]**

Ajustando uma reta só nas cem palavras mais comuns, dá zero vírgula noventa e sete. Nas posições de cem a dez mil, dá um vírgula catorze.

**[aponte para a linha da máxima verossimilhança]**

O método de máxima verossimilhança, que é o recomendado para leis de potência, dá um vírgula zero zero, com intervalo de zero vírgula noventa e nove a um vírgula zero dois. Analisando cada romance separadamente, os valores vão de zero vírgula noventa e nove a um vírgula zero quatro.

**[aponte para os dois cartões de baixo]**

Reamostrando o texto quinhentas vezes, a incerteza estatística é pequena: cerca de dois centésimos. A incerteza que pesa é a do método, de zero vírgula noventa e sete a um vírgula catorze. Então, o resumo justo é: alfa igual a um, mais ou menos um décimo.

E mesmo um valor bem medido ainda deixa uma pergunta: o que ele prova?

**[troque de slide]**

### Slide 11 · Até um texto aleatório segue Zipf · 1 min 15 s · acumulado 10:40

Para testar isso, comparei Machado com dois textos artificiais do mesmo tamanho.

**[aponte para a legenda "Digitação aleatória"]**

O primeiro é uma digitação aleatória. Cada letra e cada espaço são sorteados com as frequências de Machado. Não há gramática, nem sentido, nem memória.

**[aponte para a legenda "Texto gerado por n-gramas"]**

O segundo é gerado por um modelo que sorteia cada letra olhando as quatro anteriores. De longe, parece português. Mas setenta e nove por cento das palavras diferentes que ele produz não existem.

**[aponte para as três linhas do gráfico]**

No gráfico, a linha tracejada do texto gerado quase cobre a de Machado, e a da digitação aleatória corre paralela, mais abaixo. Os expoentes são um vírgula zero quatro, um vírgula zero sete e um vírgula zero cinco. Praticamente iguais.

*Isso já era conhecido desde George Miller, em mil novecentos e cinquenta e sete: palavras curtas surgem com mais frequência ao acaso, e isso basta para produzir uma lei de potência.*

A conclusão é que alfa perto de um, sozinho, não identifica o mecanismo que gerou o texto e não é prova de criticalidade. É exatamente o cuidado do início: estatísticas iguais, mecanismos diferentes.

**[pausa breve]** **[troque de slide]**

## Ideia 3 · Emergência

### Slide 12 · Habilidades que "surgem" com a escala · 1 min 5 s · acumulado 11:45

Terceira ideia: emergência.

Em dois mil e vinte e dois, Wei e colegas chamaram de emergente uma habilidade que não existe nos modelos menores e aparece nos maiores.

**[aponte para os três números, de cima para baixo]**

Por exemplo: somar números de três dígitos aparece no GPT-3 com treze bilhões de parâmetros. Somar números de quatro e cinco dígitos, só com cento e setenta e cinco bilhões. Uma tarefa sobre o sentido das palavras, só no PaLM, com quinhentos e quarenta bilhões. Abaixo desses tamanhos, o desempenho é de chute, e os autores falam em transição de fase.

**[aponte para o cartão da direita]**

Em dois mil e vinte e três, Schaeffer e colegas apontaram um detalhe. Essas habilidades aparecem em métricas de tudo ou nada, como o acerto exato, que só conta a resposta inteira certa. Se cada símbolo sai certo com chance p, uma resposta de L símbolos sai inteira certa com chance p elevado a L. E isso transforma uma melhora suave numa subida brusca.

Para decidir quem tem razão, precisamos de uma ferramenta da disciplina: o parâmetro de ordem.

**[troque de slide]**

### Slide 13 · Definindo o parâmetro de ordem · 1 min 25 s · acumulado 13:10

Na unidade de transições de fase, o modelo de Ising separa duas coisas. A variável de controle, a temperatura, que nós mexemos. E o parâmetro de ordem, a magnetização, que mede o estado do sistema. A transição acontece quando a magnetização muda de repente numa temperatura crítica.

**[aponte para a tabela, linha a linha]**

Vou fazer o mesmo com modelos de linguagem pequenos, que eu consigo treinar: modelos que preveem a próxima letra olhando as k anteriores, com k de zero a oito.

A variável de controle é o tamanho do modelo, medido pelo número de parâmetros, de vinte e sete a dois vírgula sete milhões.

O parâmetro de ordem, que chamo de fi, é a fração das letras do romance de teste que o modelo acerta. Ele é contínuo e não depende do tamanho da tarefa.

E a métrica de tarefa é o acerto exato: acertar L letras seguidas, o que vale aproximadamente fi elevado a L.

**[aponte para a faixa escura]**

O critério é o da física: só haveria transição se o próprio fi mudasse de repente num tamanho crítico, com a sua taxa de variação crescendo sem limite ali.

**[troque de slide]**

### Slide 14 · O salto só aparece no acerto exato · 2 min · acumulado 15:10

Este é o resultado principal. **[pausa breve]**

**[aponte para o eixo horizontal, depois para o vertical]**

O eixo horizontal é o tamanho do modelo, do menor ao maior. Cada curva mostra quanto do seu valor final ela já alcançou.

**[aponte para a linha azul]**

A linha azul é o parâmetro de ordem, o acerto por letra. Ela sobe cedo e devagar: vai de dezoito a cinquenta e nove e meio por cento, e metade do ganho já acontece com uns quatrocentos e cinquenta parâmetros.

**[aponte para a linha preta tracejada]**

A linha preta tracejada são os mesmos modelos, avaliados por acerto exato de dez letras seguidas. Ela fica em zero até uns vinte e cinco mil parâmetros, e só chega à metade com uns setecentos e sessenta mil. Olhando só para ela, eu diria que uma habilidade surgiu de repente num modelo grande.

**[aponte para as linhas cinza]**

As curvas cinza, para três e cinco letras, ficam no meio. Quanto mais longa a resposta exigida, mais tarde e mais brusco parece o salto. *E os números batem com a fórmula: fi elevado a dez dá zero vírgula cinquenta e seis por cento, e o valor medido é zero vírgula setenta e três.*

**[aponte para o número 0,12]**

Agora, o critério da física. A taxa de variação de fi tem um máximo largo, de zero vírgula doze por década de tamanho, e depois cai. Nada cresce sem limite. Não há ponto crítico. O que existe é uma saturação suave.

**[troque de slide]**

### Slide 15 · O salto está na régua, não no sistema · 55 s · acumulado 16:05

O que eu concluo disso?

**[aponte para os três cartões, da esquerda para a direita]**

No parâmetro de ordem, a mudança é suave e satura: não há ponto crítico. Na métrica de acerto exato aparece um salto, mas ele vem da régua, porque o acerto exato vale cerca de fi elevado a L.

Para afirmar que um grande modelo de linguagem passa por uma transição de fase, seria preciso mostrar o salto num parâmetro contínuo, por exemplo a probabilidade média do símbolo correto, e mostrar que ele fica mais abrupto quando o sistema cresce, como numa transição de verdade.

**[aponte para a faixa amarela]**

E um limite importante: o meu modelo não é um grande modelo de linguagem. O experimento mostra o efeito da métrica. Ele não prova que toda emergência seja ilusória.

**[troque de slide]**

## Fechamento

### Slide 16 · Três ideias para levar · 1 min 15 s · acumulado 17:20

Para fechar, três ideias.

**[aponte para o item 1]**

Primeira: o texto de Machado é muito previsível. Com cinco letras de contexto, um modelo simples precisa de um vírgula noventa e três bit por letra, contra quatro vírgula setenta e cinco sem nenhuma informação. Ou seja, pelo menos cinquenta e nove por cento do texto é redundante.

**[aponte para o item 2]**

Segunda: a frequência das palavras segue a lei de Zipf, com expoente um, mais ou menos um décimo, conforme o método. Mas um texto aleatório também segue. O expoente, sozinho, não revela o mecanismo.

**[aponte para o item 3]**

Terceira: quando definimos um parâmetro de ordem e uma variável de controle, o salto de desempenho aparece só na métrica de acerto exato. Por isso, a emergência nos grandes modelos de linguagem deve ser tratada como uma hipótese a testar, com as ferramentas de transições de fase.

*Os limites do trabalho, um único autor, modelos simples e uma única variável de controle, estão no artigo, junto com todos os métodos.*

**[troque de slide]**

### Slide 17 · Referências · 15 s · acumulado 17:35

As referências que usei estão aqui, e as completas, com links, estão no artigo.

**[deixe o slide parado por cerca de 10 segundos, em silêncio]** **[troque de slide]**

### Slide 18 · Obrigado · 25 s · acumulado 18:00

Obrigado pela atenção. Os métodos, os dados e todos os resultados estão no artigo que acompanha este vídeo.

Deixo uma pergunta para a discussão: se a emergência depende da métrica, qual seria o melhor parâmetro de ordem para um grande modelo de linguagem?

**[pausa de 2 segundos e encerre a gravação]**
