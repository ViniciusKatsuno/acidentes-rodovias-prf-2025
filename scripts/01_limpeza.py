"""
Passo 3 - Limpeza e tratamento dos dados de acidentes da PRF (2025).

Uso:  python 01_limpeza.py <csv_bruto> <csv_tratado> <log_md>

Princípio: NÃO apagar linhas. Todo problema é corrigido por regra clara
ou apenas sinalizado em uma coluna flag_*, preservando o valor original.
"""
import sys
import pandas as pd

bruto, tratado, log_path = sys.argv[1:4]
log = []  # (item, problema, linhas afetadas, decisão)

# ---------------------------------------------------------------- Item 1
# Arquivo em ISO-8859-1, separador ';' e decimal ','. Sem isso os acentos quebram.
df = pd.read_csv(bruto, sep=";", encoding="latin-1", decimal=",", dtype={"km": str})
n0 = len(df)
for c in df.select_dtypes(include=["object", "string"]).columns:
    df[c] = df[c].str.strip()
log.append((1, "Codificação latin-1, separador ';' e decimal ','", n0,
            "Leitura com encoding/decimal corretos; textos sem espaços nas pontas"))

# ---------------------------------------------------------------- Item 2
# km vem como texto com vírgula ("546,2").
df["km"] = pd.to_numeric(df["km"].str.replace(",", ".", regex=False), errors="coerce")
log.append((2, "km como texto com vírgula", n0, "Convertido para número (float)"))

# ---------------------------------------------------------------- Item 3
# Data e horário separados, como texto.
df["data_hora"] = pd.to_datetime(df["data_inversa"] + " " + df["horario"], format="%Y-%m-%d %H:%M:%S")
df["data"] = df["data_hora"].dt.date
df["mes"] = df["data_hora"].dt.month
df["hora"] = df["data_hora"].dt.hour
df["dia_semana"] = df["dia_semana"].str.capitalize()
df = df.drop(columns=["data_inversa", "horario"])
log.append((3, "Data e horário separados, em texto", n0,
            "Unidos em data_hora; criadas data, mes e hora"))

# ---------------------------------------------------------------- Item 4
# Nulos em classificacao_acidente, regional, delegacia, uop.
df["classificacao_original"] = df["classificacao_acidente"]
n_nulo_class = int(df["classificacao_acidente"].isna().sum())

def classificar(r):
    if r["mortos"] > 0:
        return "Com Vítimas Fatais"
    if r["feridos"] > 0:
        return "Com Vítimas Feridas"
    return "Sem Vítimas"

# Regra: a classificação deve refletir as contagens (mortos/feridos) do próprio registro.
regra = df.apply(classificar, axis=1)
# ---------------------------------------------------------------- Item 8
# Classificação em desacordo com as contagens de vítimas.
df["flag_classificacao_inconsistente"] = (
    df["classificacao_original"].notna() & (df["classificacao_original"] != regra)
)
n_incons_class = int(df["flag_classificacao_inconsistente"].sum())
df["classificacao_acidente"] = regra
log.append((4, "Nulos em classificacao_acidente", n_nulo_class,
            "Preenchido pela regra: mortos>0 = Fatal; feridos>0 = Feridas; senão Sem Vítimas"))
log.append((8, "Classificação em desacordo com mortos/feridos", n_incons_class,
            "Corrigida pela mesma regra; valor original mantido em classificacao_original e linha marcada em flag_classificacao_inconsistente"))

n_loc = {}
for c in ["regional", "delegacia", "uop"]:
    n_loc[c] = int(df[c].isna().sum())
    df[c] = df[c].fillna("Não informado")
log.append((4, "Nulos em regional / delegacia / uop",
            f"{n_loc['regional']} / {n_loc['delegacia']} / {n_loc['uop']}",
            "Preenchidos com 'Não informado' (não afetam os KPIs principais)"))

# ---------------------------------------------------------------- Item 5
# BR igual a 0 e sentido 'Não Informado'.
df["flag_br_nao_identificada"] = df["br"] == 0
df["br"] = df["br"].where(df["br"] != 0).astype("Int64")
n_br = int(df["flag_br_nao_identificada"].sum())
n_sent = int((df["sentido_via"] == "Não Informado").sum())
n_ambos = int(((df["sentido_via"] == "Não Informado") & df["flag_br_nao_identificada"]).sum())
df["sentido_via"] = df["sentido_via"].replace({"Não Informado": "Não informado"})
log.append((5, f"BR = 0 ({n_br}) e sentido 'Não Informado' ({n_sent}); coincidem em {n_ambos} linhas",
            n_br, "BR 0 virou nulo (Int64) com flag_br_nao_identificada; sentido padronizado como 'Não informado'"))

# ---------------------------------------------------------------- Item 6
# Clima 'Ignorado' e categorias raras.
n_ign = int((df["condicao_metereologica"] == "Ignorado").sum())
df["condicao_metereologica"] = df["condicao_metereologica"].replace({"Ignorado": "Não informado"})
agrupar = {
    "Céu Claro": "Bom tempo", "Sol": "Bom tempo",
    "Nublado": "Nublado",
    "Chuva": "Chuva", "Garoa/Chuvisco": "Chuva",
    "Nevoeiro/Neblina": "Baixa visibilidade",
    "Vento": "Outros", "Neve": "Outros",
    "Não informado": "Não informado",
}
df["grupo_clima"] = df["condicao_metereologica"].map(agrupar)
log.append((6, "Clima 'Ignorado' e categorias raras (Vento, Neve)", n_ign,
            "'Ignorado' renomeado para 'Não informado'; criada grupo_clima (originais mantidos)"))

# ---------------------------------------------------------------- Item 7
# pessoas diferente da soma de ilesos + feridos + mortos + ignorados.
df["pessoas_soma_categorias"] = df["ilesos"] + df["feridos"] + df["mortos"] + df["ignorados"]
df["flag_pessoas_inconsistente"] = df["pessoas"] != df["pessoas_soma_categorias"]
n_pes = int(df["flag_pessoas_inconsistente"].sum())
log.append((7, "pessoas diferente da soma das categorias (soma sempre maior)", n_pes,
            "Linhas mantidas e sinalizadas. KPIs usam mortos e feridos (consistentes) e não pessoas"))

# ------------------------------------------------------------- Validações
assert len(df) == n0, "linhas perdidas"
assert df["id"].is_unique
assert df[["data_hora", "uf", "classificacao_acidente", "km", "latitude", "longitude"]].notna().all().all()
assert (df["feridos"] == df["feridos_leves"] + df["feridos_graves"]).all()

df = df.sort_values("data_hora").reset_index(drop=True)
df.to_csv(tratado, index=False, encoding="utf-8-sig")

with open(log_path, "w", encoding="utf-8") as f:
    f.write("# Log de limpeza - acidentes PRF 2025\n\n")
    f.write(f"Linhas na entrada: {n0} | linhas na saída: {len(df)} (nenhuma removida) | colunas: {df.shape[1]}\n\n")
    f.write("| Item | Problema | Linhas afetadas | Decisão |\n|---|---|---|---|\n")
    for it, p, n, d in sorted(log, key=lambda x: x[0]):
        f.write(f"| {it} | {p} | {n} | {d} |\n")
    ids_nulos = df.loc[df["classificacao_original"].isna(), ["id", "uf", "mortos"]]
    fat_antes = int((df["classificacao_original"] == "Com Vítimas Fatais").sum())
    fat_depois = int((df["classificacao_acidente"] == "Com Vítimas Fatais").sum())
    f.write("\n**Notas de validação**\n")
    f.write("- O item 8 (classificação em desacordo com as contagens) só pode ser medido depois do item 4, porque os nulos entram na comparação. "
            f"Linha(s) com classificação nula: {', '.join(f'id {r.id} ({r.uf}, {r.mortos} morto(s))' for r in ids_nulos.itertuples())}.\n")
    f.write(f"- Total de mortos: {int(df['mortos'].sum())} antes e depois da limpeza. Acidentes fatais: {fat_antes} antes, {fat_depois} depois.\n")
    f.write("- Nenhuma linha removida; id continua único.\n")
    f.write("- A causa do item 7 (pessoas menor que a soma das categorias) é investigada em `relatorio_qualidade.md` (Passo 5).\n")
print("OK", len(df), df.shape[1])
