# Relatório de qualidade dos dados - acidentes PRF 2025

Base auditada: 72.529 registros. 38 colunas (após a limpeza do Passo 3).

| Teste | Severidade | Regra | Linhas que violam | % da base | Resultado |
|---|---|---|---:|---:|---|
| T01 | CRÍTICO | id é único | 0 | 0.00% | APROVADO |
| T02 | CRÍTICO | data dentro de 2025 | 0 | 0.00% | APROVADO |
| T03 | CRÍTICO | hora entre 0 e 23 | 0 | 0.00% | APROVADO |
| T04 | CRÍTICO | UF é uma das 27 válidas | 0 | 0.00% | APROVADO |
| T05 | CRÍTICO | contagens de pessoas e veículos não são negativas | 0 | 0.00% | APROVADO |
| T06 | CRÍTICO | pelo menos 1 veículo e 1 pessoa por acidente | 0 | 0.00% | APROVADO |
| T07 | CRÍTICO | feridos = feridos_leves + feridos_graves | 0 | 0.00% | APROVADO |
| T08 | CRÍTICO | classificação coerente com mortos/feridos | 0 | 0.00% | APROVADO |
| T09 | CRÍTICO | pessoas >= ilesos + feridos + mortos | 0 | 0.00% | APROVADO |
| T10 | ATENÇÃO | pessoas = ilesos + feridos + mortos + ignorados | 3823 | 5.27% | ATENÇÃO |
| T11 | ATENÇÃO | pessoas >= veículos (cada veículo com pelo menos 1 pessoa registrada) | 2884 | 3.98% | ATENÇÃO |
| T12 | ATENÇÃO | fase do dia coerente com a hora (Pleno dia à 0-4h ou Plena Noite às 9-15h) | 188 | 0.26% | ATENÇÃO |
| T13 | CRÍTICO | coordenadas dentro do território brasileiro | 0 | 0.00% | APROVADO |
| T14 | ATENÇÃO | coordenada a mais de 3 graus (~330 km) da mediana do próprio município (GPS ou município errado, ou município muito extenso) | 40 | 0.06% | ATENÇÃO |
| T15 | CRÍTICO | km entre 0 e 4.500 (maior extensão de uma BR) | 0 | 0.00% | APROVADO |
| T16 | ATENÇÃO | possíveis registros duplicados (mesma hora, local, tipo, causa e vítimas) | 6 | 0.01% | ATENÇÃO |
| T17 | INFO | acidente com 20 ou mais pessoas (possível outlier real) | 150 | 0.21% | INFO |
| T18 | INFO | BR não identificada (BR = 0 na origem) | 167 | 0.23% | INFO |
| T19 | INFO | clima não informado | 1000 | 1.38% | INFO |

## Investigação: por que `pessoas` é menor que a soma das categorias?

- Linhas afetadas: **3823** (5.3%).
- `pessoas` nunca é menor que ilesos + feridos + mortos (violações: 0). A diferença aparece só quando o campo `ignorados` entra na soma.
- Todas as linhas afetadas têm `ignorados` > 0 (True), contra 23.3% nas demais; e `ignorados` é sempre maior ou igual ao excesso (True).
- Todas têm 2 ou mais veículos (True), contra 65.6% nas demais.
- **Hipótese (não confirmada):** em acidentes com vários veículos, parte das pessoas classificadas como `ignorados` também está contada em outra categoria, ou `pessoas` não registra todos os ocupantes. A base não traz um dicionário que permita confirmar; seria preciso consultar a PRF.
- **Decisão:** os KPIs do projeto usam `mortos` e `feridos`, que passam em todos os testes críticos. `ignorados` e `pessoas` não são usados em métricas.

## Conclusão

Todos os testes **críticos** passaram. Os itens de ATENÇÃO foram mantidos na base e ficam listados em `linhas_suspeitas.csv` para revisão, sem exclusão.
