"""
Passo 4a - Carrega a base tratada em um banco SQLite.
Uso: python 02_carga_sqlite.py <csv_tratado> <banco.db>
"""
import sqlite3, sys
import pandas as pd

csv, db = sys.argv[1:3]
df = pd.read_csv(csv)
df["data_hora"] = pd.to_datetime(df["data_hora"]).dt.strftime("%Y-%m-%d %H:%M:%S")

con = sqlite3.connect(db)
df.to_sql("acidentes", con, if_exists="replace", index=False)
# Índices nas colunas mais usadas em filtros e agrupamentos
for col in ["uf", "br", "municipio", "hora", "mes", "causa_acidente"]:
    con.execute(f"CREATE INDEX IF NOT EXISTS idx_acidentes_{col} ON acidentes({col})")
con.commit()
n = con.execute("SELECT COUNT(*) FROM acidentes").fetchone()[0]
print(f"Tabela acidentes criada com {n} linhas")
con.close()
