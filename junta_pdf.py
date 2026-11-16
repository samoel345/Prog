import os
from PyPDF2 import PdfMerger

def juntar_pdfs(pasta_origem, arquivo_saida):
    # Cria o objeto de mesclagem
    merger = PdfMerger()
    
    # Lista e ordena os arquivos da pasta
    arquivos = [f for f in os.listdir(pasta_origem) if f.endswith('.pdf')]
    arquivos.sort() # Garante a ordem correta
    
    # Verifica se há arquivos para mesclar
    if not arquivos:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    # Adiciona cada arquivo ao objeto de mesclagem
    for arquivo in arquivos:
        caminho_completo = os.path.join(pasta_origem, arquivo)
        print(f"Adicionando: {arquivo}")
        merger.append(caminho_completo)
    
    # Escreve o arquivo final
    with open(arquivo_saida, "wb") as f_out:
        merger.write(f_out)
        
    merger.close()
    print(f"\nFinalizado! Arquivo gerado: {arquivo_saida}")

# --- CONFIGURAÇÃO ---
# Coloque "." para a pasta atual ou o caminho completo, ex: "C:/Documentos/PDFs"
pasta_dos_pdfs = "." 
nome_do_resultado = "pdf_final_mesclado.pdf"

juntar_pdfs(pasta_dos_pdfs, nome_do_resultado)
