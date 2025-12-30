import pandas as pd
import win32com.client as win32
import os
import sys

# Caminho do arquivo Excel

if getattr(sys,"frozen",False):
    BASE_DIR= os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_EXCEL = os.path.join(BASE_DIR, "Pendencias", "Pedencias_Batida_impares.xlsx")

def safe_str(valor):
    """Retorna string limpa ou vazia caso o valor seja NaN."""
    return "" if pd.isna(valor) else str(valor).strip()

# Verifica se o arquivo existe
if not os.path.exists(ARQUIVO_EXCEL):
    print(f"❌ Arquivo '{ARQUIVO_EXCEL}' não encontrado.")
    input("Pressione Enter para sair...")
    exit()

# Caminho do arquivo de corpo de e-mail (mesma pasta do Excel)
ARQUIVO_CORPO = os.path.join(os.path.dirname(ARQUIVO_EXCEL), "corpo_email - Batida Impar.txt")
if not os.path.exists(ARQUIVO_CORPO):
    print(f"❌ Arquivo '{ARQUIVO_CORPO}' não encontrado.")
    input("Pressione Enter para sair...")
    exit()

# Lê o modelo do corpo do e-mail uma vez
with open(ARQUIVO_CORPO, "r", encoding="utf-8") as f:
    modelo_corpo = f.read()

# Lê o Excel
df = pd.read_excel(ARQUIVO_EXCEL)

# Remove linhas sem e-mail principal
df = df.dropna(subset=["Email_loja.Email"])
df = df[df["Email_loja.Email"].str.strip() != ""]

# Preenche valores NaN de colunas importantes para evitar erros
df['Local'] = df['Local'].fillna('')
df['Departamento'] = df['Departamento'].fillna('')
df['Nome'] = df['Nome'].fillna('')

# Abre o Outlook
try:
    outlook = win32.Dispatch("Outlook.Application")
except Exception as e:
    print("❌ Erro ao abrir Outlook:", e)
    input("Pressione Enter para sair...")
    exit()

# Agrupa só pelo e-mail principal
grupos = list(df.groupby('Email_loja.Email'))
print(f"Total de grupos a processar: {len(grupos)}\n")

for i, (email_principal, grupo) in enumerate(grupos, start=1):
    destinatarios = safe_str(email_principal)

    if not destinatarios:
        print(f"⚠️ Grupo {i}: Nenhum e-mail principal encontrado, pulando...")
        continue

    # Lista de todos sub_emails válidos no grupo
    sub_emails = []
    if 'Sub_email' in grupo.columns:
        sub_emails = [safe_str(e) for e in grupo['Sub_email'].dropna().unique() if safe_str(e)]
    
    # Lista de locais e departamentos
    locais_str = ", ".join(map(str, grupo['Local'].dropna().unique()))
    departamentos_list = list(map(str, grupo['Departamento'].dropna().unique()))
    departamentos_str = ", ".join(departamentos_list[:3])
    if len(departamentos_list) > 3:
        departamentos_str += ", ..."

    # Monta tabela HTML
    tabela_html = """
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th>Local</th>
                <th>Matricula</th>
                <th>Nome</th>
                <th>Departamento</th>
                <th>Dia</th>
                <th>Batidas</th>
                <th>Qtde</th>
            </tr>
        </thead>
        <tbody>
    """
    for _, row in grupo.iterrows():
        tabela_html += f"""
            <tr>
                <td>{safe_str(row['Local'])}</td>
                <td>{int(float(row['Matrícula'])) if not pd.isna(row['Matrícula']) else ""}</td>
                <td>{safe_str(row['Nome'])}</td>
                <td>{safe_str(row['Departamento'])}</td>
                <td>{row["Dia"].strftime('%d/%m/%Y') if not pd.isna(row["Dia"]) else ""}</td>
                <td>{safe_str(row["Batidas"])}</td>
                <td>{int(float(row['Qtde'])) if not pd.isna(row['Qtde']) else ""}</td>
            </tr>
        """
    tabela_html += "</tbody></table>"

    # Substitui {{tabela}} no modelo pelo HTML gerado
    corpo_html = modelo_corpo.replace("{{tabela}}", tabela_html)

    # Monta lista final de CC
    cc_emails = ["ld.pontoeletronico@grupodma.com.br"] + sub_emails
    cc_str = "; ".join(cc_emails)

    # Debug antes do envio
    print(f"Grupo {i}:")
    print("  To:", destinatarios)
    print("  CC:", cc_str)
    print("  Locais:", locais_str)
    print("  Departamentos:", departamentos_str)

    # Cria e envia o e-mail
    mail = outlook.CreateItem(0)
    mail.To = destinatarios
    mail.CC = cc_str
    mail.Subject = f"Pendência de ponto - {locais_str}"
    mail.HTMLBody = corpo_html
    mail.Send()

    print(f"✅ E-mail enviado para: {destinatarios} com CC: {cc_str}\n")
    print("Todos os e-mails foram enviados com sucesso!")

input("Pressione Enter para sair...")