#!/usr/bin/env bash
# Reproduz todo o pipeline a partir do CSV bruto da PRF.
# Pré-requisito: colocar datatran2025.csv em dados/brutos/
set -euo pipefail
cd "$(dirname "$0")"

python scripts/01_limpeza.py dados/brutos/datatran2025.csv dados/tratados/acidentes_prf_2025_tratado.csv docs/log_limpeza.md
python scripts/02_carga_sqlite.py dados/tratados/acidentes_prf_2025_tratado.csv dados/acidentes_prf.db
python scripts/03_rodar_consultas.py dados/acidentes_prf.db sql/kpis.sql dados/resultados docs/resultados_kpis.md
python scripts/04_auditoria_qualidade.py dados/tratados/acidentes_prf_2025_tratado.csv docs/relatorio_qualidade.md docs/linhas_suspeitas.csv
echo "Pipeline concluído. Para o notebook: jupyter lab notebooks/analise_acidentes_prf_2025.ipynb"
