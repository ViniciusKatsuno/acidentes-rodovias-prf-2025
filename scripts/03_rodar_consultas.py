"""
Passo 4b - Executa cada consulta de kpis.sql, salva CSVs e um resumo em Markdown.
Uso: python 03_rodar_consultas.py <banco.db> <kpis.sql> <pasta_saida> <resumo.md>
"""
import re, sqlite3, sys, os
import pandas as pd

db, sql_path, out_dir, md_path = sys.argv[1:5]
os.makedirs(out_dir, exist_ok=True)
texto = open(sql_path, encoding="utf-8").read()
blocos = re.split(r"^-- name: (\S+)\s*$", texto, flags=re.M)[1:]
con = sqlite3.connect(db)
md = ["# Resultados dos KPIs - acidentes PRF 2025\n"]
for nome, corpo in zip(blocos[0::2], blocos[1::2]):
    sql = "\n".join(l for l in corpo.splitlines() if not l.strip().startswith("--"))
    df = pd.read_sql_query(sql, con)
    df.to_csv(os.path.join(out_dir, f"{nome}.csv"), index=False, encoding="utf-8-sig")
    md.append(f"\n## {nome}\n\n{df.to_markdown(index=False)}\n")
    print(nome, df.shape)
open(md_path, "w", encoding="utf-8").write("\n".join(md))
