# Montando o painel no Power BI Desktop

Tempo estimado: cerca de 1 hora. Os arquivos aqui foram escritos sem abrir o Power BI Desktop, então vale conferir cada medida ao criá-la.

## 1. Importar os dados
1. **Obter dados > Texto/CSV** e escolha `dados/tratados/acidentes_prf_2025_tratado.csv`.
2. Em **Origem do arquivo**, selecione **65001: Unicode (UTF-8)**.
3. Antes de carregar, clique em **Transformar dados** e confira os tipos:
   - `km`, `latitude`, `longitude`: **Número decimal**. O arquivo usa **ponto** como separador decimal. Se os valores aparecerem errados, use *Transformar > Tipo de dados > Usar localidade* e escolha **Inglês (Estados Unidos)**.
   - `data`: **Data**. `data_hora`: **Data/Hora**.
   - `br`: **Número inteiro** (tem valores em branco, e isso é esperado).
4. Renomeie a consulta/tabela para **`acidentes`** (as medidas usam esse nome).
5. **Fechar e aplicar**.

## 2. Modelo
1. Crie a tabela `Calendario` e a coluna `Ordem Dia` (código em `medidas.dax`).
2. Relacione `Calendario[Date]` com `acidentes[data]` (muitos para um, filtro em uma direção).
3. Selecione a coluna `dia_semana` e, em **Ferramentas de coluna**, use **Classificar por coluna > Ordem Dia**.
4. Marque `Calendario` como tabela de datas.
5. Crie as demais medidas de `medidas.dax`.

## 3. Páginas sugeridas

**Página 1: Visão geral**
- Cartões: `Total Acidentes`, `Total Mortos`, `Mortos por 100 Acidentes`, `% Acidentes Fatais`.
- Segmentações: `uf`, `dia_semana`.
- Colunas: `Total Acidentes` por mês (eixo `Calendario[Nome do Mes]`, ordenado por `Mes`).
- Mapa ou barras por `uf` com `Total Mortos`.

**Página 2: Quando acontecem**
- Colunas por `hora`: `Total Acidentes`, e outra com `Mortos por 100 Acidentes`.
- Colunas por `dia_semana`: `Mortos por 100 Acidentes`.
- Cartão: `% Mortos no Fim de Semana`.

**Página 3: Causas e tipos**
- Barras horizontais por `causa_acidente` com `Letalidade (min. 30 acidentes)`, top 10.
- Barras por `tipo_acidente` com a mesma medida.
- Filtro visual: `Total Acidentes` maior ou igual a 500 nos rankings gerais.

**Página 4: Estados e rodovias**
- Matriz com `uf`, `Total Acidentes`, `Total Mortos`, `Mortos por 100 Acidentes`, `Diferença para o Brasil (p.p.)`.
- Barras por `br` (filtrar `br` não vazio) com `Total Mortos`.

## 4. Cores
Use uma cor principal (azul) e uma de destaque (laranja) só para o que importa, como a madrugada e o fim de semana. Evite um gráfico multicolorido.

## 5. Boas práticas
- Dê títulos que descrevam o recorte, como "Mortos por 100 acidentes, por hora".
- Deixe uma nota na página com a definição de letalidade e o aviso de que não há dados de tráfego.
- Publique uma captura de tela ou o link do relatório no LinkedIn e no README.
