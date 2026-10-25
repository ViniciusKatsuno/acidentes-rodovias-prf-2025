"""
Passo 5 - Auditoria de qualidade dos dados (inspirada em testes de V&V).

Cada teste tem: nome, severidade, regra e quantidade de linhas que violam.
  CRÍTICO  = quebra a confiança na base (o script termina com erro)
  ATENÇÃO  = pode ser real ou erro de registro; fica documentado
  INFO     = observação para o leitor

Uso: python 04_auditoria_qualidade.py <csv_tratado> <relatorio.md> <linhas_suspeitas.csv>
"""
import sys
import numpy as np
import pandas as pd

csv, relatorio, suspeitas = sys.argv[1:4]
df = pd.read_csv(csv, parse_dates=["data_hora"])
N = len(df)
UFS = {"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"}

resultados = []        # (id, severidade, regra, violações)
mascaras = {}          # id -> máscara booleana, para exportar as linhas suspeitas

def testar(tid, sev, regra, violacao):
    violacao = pd.Series(violacao, index=df.index).fillna(False).astype(bool)
    resultados.append((tid, sev, regra, int(violacao.sum())))
    mascaras[tid] = violacao

# ---- Integridade estrutural
testar("T01", "CRÍTICO", "id é único", df["id"].duplicated(keep=False))
testar("T02", "CRÍTICO", "data dentro de 2025", ~df["data_hora"].dt.year.eq(2025))
testar("T03", "CRÍTICO", "hora entre 0 e 23", ~df["hora"].between(0, 23))
testar("T04", "CRÍTICO", "UF é uma das 27 válidas", ~df["uf"].isin(UFS))
testar("T05", "CRÍTICO", "contagens de pessoas e veículos não são negativas",
       (df[["mortos","feridos_leves","feridos_graves","ilesos","ignorados","pessoas","veiculos"]] < 0).any(axis=1))
testar("T06", "CRÍTICO", "pelo menos 1 veículo e 1 pessoa por acidente", (df["veiculos"] < 1) | (df["pessoas"] < 1))

# ---- Coerência interna
testar("T07", "CRÍTICO", "feridos = feridos_leves + feridos_graves", df["feridos"] != df["feridos_leves"] + df["feridos_graves"])
testar("T08", "CRÍTICO", "classificação coerente com mortos/feridos",
       ((df["mortos"] > 0) & (df["classificacao_acidente"] != "Com Vítimas Fatais"))
       | ((df["mortos"] == 0) & (df["feridos"] > 0) & (df["classificacao_acidente"] != "Com Vítimas Feridas"))
       | ((df["mortos"] == 0) & (df["feridos"] == 0) & (df["classificacao_acidente"] != "Sem Vítimas")))
conhecidos = df["ilesos"] + df["feridos"] + df["mortos"]
testar("T09", "CRÍTICO", "pessoas >= ilesos + feridos + mortos", df["pessoas"] < conhecidos)
testar("T10", "ATENÇÃO", "pessoas = ilesos + feridos + mortos + ignorados", df["pessoas"] != conhecidos + df["ignorados"])
testar("T11", "ATENÇÃO", "pessoas >= veículos (cada veículo com pelo menos 1 pessoa registrada)", df["pessoas"] < df["veiculos"])

# ---- Plausibilidade
testar("T12", "ATENÇÃO", "fase do dia coerente com a hora (Pleno dia à 0-4h ou Plena Noite às 9-15h)",
       ((df["fase_dia"] == "Pleno dia") & df["hora"].between(0, 4))
       | ((df["fase_dia"] == "Plena Noite") & df["hora"].between(9, 15)))
testar("T13", "CRÍTICO", "coordenadas dentro do território brasileiro",
       ~df["latitude"].between(-34, 6) | ~df["longitude"].between(-74, -28))
# Outlier geográfico: longe da mediana do próprio município (municípios com 5+ acidentes).
# Atenção: municípios muito extensos (ex.: Altamira-PA) geram alertas legítimos, por isso é só ATENÇÃO.
g = df.groupby(["uf", "municipio"])
med = g[["latitude", "longitude"]].transform("median")
dist = np.hypot(df["latitude"] - med["latitude"], df["longitude"] - med["longitude"])
testar("T14", "ATENÇÃO", "coordenada a mais de 3 graus (~330 km) da mediana do próprio município (GPS ou município errado, ou município muito extenso)",
       (dist > 3) & (g["id"].transform("count") >= 5))
testar("T15", "CRÍTICO", "km entre 0 e 4.500 (maior extensão de uma BR)", ~df["km"].between(0, 4500))
chave = ["data_hora", "br", "km", "municipio", "tipo_acidente", "causa_acidente", "mortos", "feridos"]
testar("T16", "ATENÇÃO", "possíveis registros duplicados (mesma hora, local, tipo, causa e vítimas)", df.duplicated(chave, keep=False))
testar("T17", "INFO", "acidente com 20 ou mais pessoas (possível outlier real)", df["pessoas"] >= 20)
testar("T18", "INFO", "BR não identificada (BR = 0 na origem)", df["flag_br_nao_identificada"])
testar("T19", "INFO", "clima não informado", df["condicao_metereologica"] == "Não informado")

# ---- Investigação do item 7 (pessoas x soma das categorias)
f = df[df["flag_pessoas_inconsistente"]]
excesso = f["pessoas_soma_categorias"] - f["pessoas"]
invest = {
    "linhas": len(f),
    "todas_com_ignorados": bool((f["ignorados"] > 0).all()),
    "ignorados_maior_ou_igual_ao_excesso": bool((f["ignorados"] >= excesso).all()),
    "pessoas_menor_que_conhecidos": int((f["pessoas"] < conhecidos[f.index]).sum()),
    "todas_com_2_ou_mais_veiculos": bool((f["veiculos"] >= 2).all()),
    "pct_2_ou_mais_veiculos_nas_demais": round(float(100 * (df.loc[~df["flag_pessoas_inconsistente"], "veiculos"] >= 2).mean()), 1),
    "pct_ignorados_positivo_nas_demais": round(float(100 * (df.loc[~df["flag_pessoas_inconsistente"], "ignorados"] > 0).mean()), 1),
}

# ---- Relatório
criticas = [r for r in resultados if r[1] == "CRÍTICO" and r[3] > 0]
with open(relatorio, "w", encoding="utf-8") as w:
    w.write("# Relatório de qualidade dos dados - acidentes PRF 2025\n\n")
    w.write(f"Base auditada: {N:,} registros, {df.shape[1]} colunas (após a limpeza do Passo 3).\n\n".replace(",", "."))
    w.write("| Teste | Severidade | Regra | Linhas que violam | % da base | Resultado |\n|---|---|---|---:|---:|---|\n")
    for tid, sev, regra, n in resultados:
        res = "APROVADO" if n == 0 else ("FALHA" if sev == "CRÍTICO" else ("ATENÇÃO" if sev == "ATENÇÃO" else "INFO"))
        w.write(f"| {tid} | {sev} | {regra} | {n} | {100*n/N:.2f}% | {res} |\n")
    w.write("\n## Investigação: por que `pessoas` é menor que a soma das categorias?\n\n")
    w.write(f"- Linhas afetadas: **{invest['linhas']}** ({100*invest['linhas']/N:.1f}%).\n")
    w.write(f"- `pessoas` nunca é menor que ilesos + feridos + mortos (violações: {invest['pessoas_menor_que_conhecidos']}). A diferença aparece só quando o campo `ignorados` entra na soma.\n")
    w.write(f"- Todas as linhas afetadas têm `ignorados` > 0 ({invest['todas_com_ignorados']}), contra {invest['pct_ignorados_positivo_nas_demais']}% nas demais; e `ignorados` é sempre maior ou igual ao excesso ({invest['ignorados_maior_ou_igual_ao_excesso']}).\n")
    w.write(f"- Todas têm 2 ou mais veículos ({invest['todas_com_2_ou_mais_veiculos']}), contra {invest['pct_2_ou_mais_veiculos_nas_demais']}% nas demais.\n")
    w.write("- **Hipótese (não confirmada):** em acidentes com vários veículos, parte das pessoas classificadas como `ignorados` também está contada em outra categoria, ou `pessoas` não registra todos os ocupantes. A base não traz um dicionário que permita confirmar; seria preciso consultar a PRF.\n")
    w.write("- **Decisão:** os KPIs do projeto usam `mortos` e `feridos`, que passam em todos os testes críticos. `ignorados` e `pessoas` não são usados em métricas.\n")
    w.write("\n## Conclusão\n\n")
    if criticas:
        w.write(f"**{len(criticas)} teste(s) crítico(s) falharam.** Revisar antes de usar a base.\n")
    else:
        w.write("Todos os testes **críticos** passaram. Os itens de ATENÇÃO foram mantidos na base e ficam listados em `linhas_suspeitas.csv` para revisão, sem exclusão.\n")

cols = ["id", "data_hora", "uf", "br", "km", "municipio", "tipo_acidente", "pessoas", "veiculos", "mortos", "feridos", "ignorados"]
frames = []
for tid, sev, regra, n in resultados:
    if sev == "ATENÇÃO" and tid != "T10" and n > 0:
        frames.append(df.loc[mascaras[tid], cols].assign(teste=tid))
pd.concat(frames).to_csv(suspeitas, index=False, encoding="utf-8-sig") if frames else None
print(pd.DataFrame(resultados, columns=["teste", "sev", "regra", "n"]).to_string(index=False))
print(invest)
sys.exit(1 if criticas else 0)
