# Log de limpeza - acidentes PRF 2025

Linhas na entrada: 72529 | linhas na saída: 72529 (nenhuma removida) | colunas: 38

| Item | Problema | Linhas afetadas | Decisão |
|---|---|---|---|
| 1 | Codificação latin-1, separador ';' e decimal ',' | 72529 | Leitura com encoding/decimal corretos; textos sem espaços nas pontas |
| 2 | km como texto com vírgula | 72529 | Convertido para número (float) |
| 3 | Data e horário separados, em texto | 72529 | Unidos em data_hora; criadas data, mes e hora |
| 4 | Nulos em classificacao_acidente | 1 | Preenchido pela regra: mortos>0 = Fatal; feridos>0 = Feridas; senão Sem Vítimas |
| 4 | Nulos em regional / delegacia / uop | 2 / 22 / 38 | Preenchidos com 'Não informado' (não afetam os KPIs principais) |
| 5 | BR = 0 (167) e sentido 'Não Informado' (167); coincidem em 167 linhas | 167 | BR 0 virou nulo (Int64) com flag_br_nao_identificada; sentido padronizado como 'Não informado' |
| 6 | Clima 'Ignorado' e categorias raras (Vento, Neve) | 1000 | 'Ignorado' renomeado para 'Não informado'; criada grupo_clima (originais mantidos) |
| 7 | pessoas diferente da soma das categorias (soma sempre maior) | 3823 | Linhas mantidas e sinalizadas. KPIs usam mortos e feridos (consistentes) e não pessoas |
| 8 | Classificação em desacordo com mortos/feridos | 0 | Corrigida pela mesma regra; valor original mantido em classificacao_original e linha marcada em flag_classificacao_inconsistente |

**Notas de validação**
- O item 8 (classificação em desacordo com as contagens) só pode ser medido depois do item 4, porque os nulos entram na comparação. Linha(s) com classificação nula: id 652519 (CE, 1 morto(s)).
- Total de mortos: 6043 antes e depois da limpeza. Acidentes fatais: 5209 antes, 5210 depois.
- Nenhuma linha removida; id continua único.
- A causa do item 7 (pessoas menor que a soma das categorias) é investigada em `relatorio_qualidade.md` (Passo 5).
