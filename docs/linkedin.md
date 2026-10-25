# Textos para o LinkedIn

## Título (headline)
Analista de Dados Jr | SQL • Power BI • Python • Automação de processos

## Sobre
Graduado em Análise e Desenvolvimento de Sistemas, com experiência em análise de dados, dashboards (Power BI e Looker Studio), SQL, Python e automação de processos com APIs e webhooks. Gosto de transformar dados brutos em informações claras para apoiar decisões, e de documentar o caminho: limpeza, validação e conclusões. Busco minha oportunidade como Analista de Dados Júnior.

Projeto em destaque: análise de 72 mil acidentes nas rodovias federais (dados abertos da PRF).

## Post de lançamento do projeto

Analisei os 72.529 acidentes registrados pela PRF nas rodovias federais em 2025. Alguns resultados:

• Às 3h da manhã, 16,5 pessoas morrem a cada 100 acidentes. Às 7h, 4,4. O pico de acidentes, porém, é às 18h.
• Sábado e domingo têm mais acidentes fatais (8,6% contra 6,5% nos dias úteis). Aos domingos, o álcool aparece em 10,4% dos acidentes.
• Colisão frontal e atropelamento de pedestre são 11% dos acidentes e 46% das mortes.
• Na Bahia, são 14,2 mortes por 100 acidentes. Em Santa Catarina, 5,3.

O que fiz no caminho: limpei a base (acentos quebrados, datas em texto, nulos), escrevi 19 testes automáticos de qualidade e achei 3.823 registros em que o total de pessoas não bate com a soma das categorias. Em vez de apagar, documentei e deixei esses campos fora das métricas. Depois, KPIs em SQL, análise em Python e um painel interativo.

Um limite importante: a base não tem volume de tráfego, então os números mostram onde há mais acidentes e mortes, não qual rodovia é mais perigosa.

Código, relatório de qualidade e painel: [link do GitHub]

#AnáliseDeDados #SQL #Python #PowerBI #DadosAbertos

## Como contar o projeto em entrevista (30 segundos)
"Peguei os dados abertos da PRF com 72 mil acidentes de 2025. Limpei a base, escrevi testes de qualidade e encontrei uma inconsistência em 5% dos registros, que documentei e tirei das métricas. Depois calculei os indicadores em SQL e analisei em Python. O principal achado é que madrugada e fim de semana são os momentos mais letais, e que colisão frontal e atropelamento concentram quase metade das mortes. Também deixei claro o limite: sem dados de tráfego, não dá para dizer qual rodovia é mais perigosa."
