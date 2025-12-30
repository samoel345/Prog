import pandas as pd
import os

pasta = r"C:\Users\685727\Documents\downloads"

for arquivo in os.listdir(pasta):
    if arquivo.lower().endswith(".xls"):
        caminho_xls = os.path.join(pasta, arquivo)
        caminho_xlsx = os.path.join(pasta, os.path.splitext(arquivo)[0] + ".xlsx")

        try:
            # tenta primeiro como Excel antigo
            try:
                df = pd.read_excel(caminho_xls, engine="xlrd")
            except Exception:
                # se falhar, lê como HTML (relatórios disfarçados de .xls)
                tabelas = pd.read_html(caminho_xls)
                df = tabelas[0]

            df.to_excel(caminho_xlsx, index=False)
            print(f"✅ Convertido: {arquivo} → {os.path.basename(caminho_xlsx)}")

        except Exception as e:
            print(f"❌ Erro ao converter {arquivo}: {e}")
