import pandas as pd
from supabase import create_client

# 1. Conexão com Supabase
URL = "https://fpjbmypkvzgkyeiwgbqq.supabase.co" # Substitua pela sua URL
KEY = "sb_publishable_KI8qO9pVdWEl60fFQC_B_g__jZLHTUx"   # Substitua pela sua Key
supabase = create_client(URL, KEY)

# 2. Carrega as Unidades do Banco para mapear os IDs
unidades_response = supabase.table("unidades").select("id, nome_unidade").execute()
unidades_map = {u["nome_unidade"].strip(): u["id"] for u in unidades_response.data}

# 3. Leitura do Excel
df = pd.read_excel("veiculos.xlsx")

# 4. Tratamento e Estruturação dos Dados
registros = []
for _, row in df.iterrows():
    nome_unidade = str(row["UO"]).strip()
    unidade_id = unidades_map.get(nome_unidade)
    
    # Trata data de previsão se existir
    prev = str(row["PREVISÃO RETORNO"]).strip()
    previsao_retorno = None if prev in ["-", "", "nan", "None", "NaT"] else prev

    # Trata marca/modelo/ano
    marca = None if pd.isna(row["MARCA"]) or str(row["MARCA"]).strip() == "-" else str(row["MARCA"]).strip()
    modelo = None if pd.isna(row["MODELO"]) or str(row["MODELO"]).strip() == "-" else str(row["MODELO"]).strip()
    
    try:
        ano = int(row["ANO"])
    except (ValueError, TypeError):
        ano = None

    registros.append({
        "unidade_id": unidade_id,
        "placa": str(row["PLACA"]).strip(),
        "prefixo": str(row["PREFIXO"]).strip(),
        "grupo": str(row["GRUPO"]).strip(),
        "tipo": str(row["TIPO"]).strip(),
        "situacao": str(row["SITUAÇÃO"]).strip(),
        "previsao_retorno": previsao_retorno,
        "marca": marca,
        "modelo": modelo,
        "ano": ano
    })

# 5. Inserção em Lotes (Batch Insert)
BATCH_SIZE = 200
for i in range(0, len(registros), BATCH_SIZE):
    batch = registros[i:i + BATCH_SIZE]
    supabase.table("veiculos").insert(batch).execute()
    print(f"Inseridos {i + len(batch)} de {len(registros)} veículos...")

print("✅ Carga finalizada com sucesso!")
