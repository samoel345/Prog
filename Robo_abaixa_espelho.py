import os
import shutil
import glob
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import sys
import win32com.client as win32

# === DETECTAR BASE_DIR ===
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # Pasta do EXE
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Pasta do script

# === PASTA DE DESTINO NA REDE ===
PASTA_DESTINO = r"\\prddfsr01\OPERACOES\CONTROLE_E_GESTAO\41. Ponto Web Ahgora\base_bd_espelhos_ponto"

# === FUNÇÕES DE PASTA SEGURA ===
def criar_pasta(pasta):
    try:
        os.makedirs(pasta, exist_ok=True)
        print(f"✅ Pasta '{pasta}' criada ou já existia.")
    except PermissionError as e:
        print(f"❌ Sem permissão para criar pasta '{pasta}': {e}")

def limpar_pasta(pasta):
    if os.path.exists(pasta):
        for arquivo in os.listdir(pasta):
            caminho_arquivo = os.path.join(pasta, arquivo)
            try:
                if os.path.isfile(caminho_arquivo) or os.path.islink(caminho_arquivo):
                    os.remove(caminho_arquivo)
                elif os.path.isdir(caminho_arquivo):
                    shutil.rmtree(caminho_arquivo, ignore_errors=True)
            except PermissionError as e:
                print(f"⚠️ Sem permissão para excluir '{caminho_arquivo}': {e}")
        print(f"✅ Pasta '{pasta}' limpa (arquivos bloqueados podem ter permanecido).")
    else:
        criar_pasta(pasta)

# === LIMPAR PASTA DE DESTINO ===
limpar_pasta(PASTA_DESTINO)

# === CONFIGURAÇÃO DO SELENIUM COM DOWNLOAD NA PASTA TEMP DO EXE ===
PASTA_TEMP = os.path.join(BASE_DIR, "Downloads")  # pasta já existente no exe

CAMINHO_CHROMEDRIVER = os.path.join(BASE_DIR, "Drive_crhome", "chromedriver.exe")
ARQUIVO_Meses_espelhos = os.path.join(BASE_DIR, "Meses_espelhos.xlsx")

options = Options()
prefs = {
    "download.default_directory": PASTA_TEMP,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(CAMINHO_CHROMEDRIVER), options=options)
wait = WebDriverWait(driver, 30)

# === LEITURA DADOS ===
df_meses = pd.read_excel(ARQUIVO_Meses_espelhos, sheet_name="Meses")
df_usuario = pd.read_excel(ARQUIVO_Meses_espelhos, sheet_name="usuario")
df_buscar = pd.read_excel(ARQUIVO_Meses_espelhos, sheet_name="buscado meses")


usuario = df_usuario.loc[0, "usuario"]
senha = df_usuario.loc[0, "senha"]

df_buscar["mes inicial"] = df_buscar["mes inicial"].str.strip().str.lower()
df_buscar["mes final"] = df_buscar["mes final"].astype(str).str.strip().str.lower()
df_buscar["ano"] = df_buscar["ano"].astype(str)

print("Colunas encontradas:", df_buscar.columns.tolist())

# === FUNÇÕES DE FLUXO ===
def seleciona_ano(driver, ano):
    try:
        wait = WebDriverWait(driver, 10)

        elemento_ano = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="yearsSess"]'))
        )

        select_ano = Select(elemento_ano)
        select_ano.select_by_visible_text(str(ano))

    except Exception as e:
        print(f"Erro ao selecionar o ano: {e}")

def login():
    driver.get("https://app.ahgora.com.br/gerenciador_espelhos")
    driver.maximize_window()
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(usuario + '\n')
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))).send_keys(senha + '\n')
    print("✅ Login realizado com sucesso!")

def selecionar_empresa():
    empresa_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[contains(text(), 'a555958 - DMA DISTRIBUIDORA S/A (PRODUÇÃO)')]/ancestor::div[@role='button']")))
    empresa_btn.click()
    print("✅ Empresa selecionada!")
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//select[@class='form-control input-sm pw-not-niceselect']")))
def buscar_mes(mes):
    try:
        select_mes_el = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//select[@class='form-control input-sm pw-not-niceselect']")))
        select_mes = Select(select_mes_el)
        mes_capitalizado = mes.strip().capitalize()
        select_mes.select_by_visible_text(mes_capitalizado)
        print(f"✅ Mês '{mes_capitalizado}' selecionado!")
        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
    except Exception as e:
        print(f"⚠️ Erro ao selecionar o mês '{mes}': {e}")
        time.sleep(20)

def baixar_relatorios():
    # Espera overlay sumir e tabela aparecer
    try:
        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//div[contains(@class, 'overlay') or contains(@class, 'loading')]")))
    except:
        pass
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
    except:
        print("⚠️ Tabela não carregou corretamente.")
        return None

    print("⏳ Aguardando 60 segundos para garantir carregamento...")
    time.sleep(80)

    try:
        baixar_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="managerTable_wrapper"]/div[1]/button[1]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", baixar_btn)
        time.sleep(1)
        baixar_btn.click()
    except:
        print("⚠️ Botão Excel não encontrado ou não clicável.")
        return None

    # Aguarda o download terminar
    arquivo_baixado = None
    while True:
        time.sleep(2)
        lista_xlsx = glob.glob(os.path.join(PASTA_TEMP, "*.xlsx"))
        lista_temp = glob.glob(os.path.join(PASTA_TEMP, "*.crdownload"))
        if lista_xlsx and not lista_temp:
            arquivo_baixado = max(lista_xlsx, key=os.path.getctime)
            break

    print(f"✅ Download concluído: {arquivo_baixado}")
    return arquivo_baixado

def mover_arquivo(origem, destino):
    try:
        shutil.move(origem, destino)
        print(f"✅ Arquivo movido de {origem} para {destino}")
    except PermissionError as e:
        print(f"❌ Sem permissão para mover '{origem}' para '{destino}': {e}")
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado '{origem}': {e}")

PASTA_ARQUIVO = r"\\prddfsr01\OPERACOES\CONTROLE_E_GESTAO\41. Ponto Web Ahgora\bd_espelhos.xlsm"

def atualizar_excel(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return

    try:
        excel = win32.DispatchEx("Excel.Application")  # abre uma instância separada do Excel
        excel.Visible = False  # não mostrar janela
        excel.DisplayAlerts = False  # evita alertas

        wb = excel.Workbooks.Open(caminho_arquivo, UpdateLinks=True)  # abre e atualiza links
        wb.RefreshAll()  # atualiza todas as consultas externas
        excel.CalculateUntilAsyncQueriesDone()  # espera queries terminarem
        wb.Save()  # salva alterações
        wb.Close()
        excel.Quit()
        print(f"✅ Excel atualizado e salvo: {caminho_arquivo}")

    except Exception as e:
        print(f"⚠️ Erro ao atualizar Excel '{caminho_arquivo}': {e}")

def meses_por_periodo(mes_inicial, mes_final, lista_meses):
    if mes_final == "" or mes_final == "nan":
        return [mes_inicial]

    selecionados = []
    inicio = False

    for mes in lista_meses:
        if mes == mes_inicial:
            inicio = True
        if inicio:
            selecionados.append(mes)
        if mes == mes_final:
            break

    return selecionados


# === FLUXO PRINCIPAL ===
if __name__ == "__main__":
    login()
    selecionar_empresa()

    for _, linha in df_buscar.iterrows():
        ano = linha["ano"]
        mes_inicial = linha["mes inicial"]
        mes_final = linha["mes final"]

        seleciona_ano(driver, ano)
        print(f"\n📅 Ano selecionado no site: {ano}")

        meses_para_baixar = meses_por_periodo(
            mes_inicial,
            mes_final,
            df_meses["mes"].str.lower().tolist()
        )

        for mes in meses_para_baixar:
            buscar_mes(mes)

            # ✅ PRINT NO TERMINAL (ANO + MÊS)
            print(f"▶️ Selecionado → Ano: {ano} | Mês: {mes}")

            arquivo = baixar_relatorios()
            if arquivo is None:
                print(f"⚠️ Falha ao baixar {mes}/{ano}")
                continue

            novo_nome = f"espelho_{mes}_{ano}.xlsx"
            destino = os.path.join(PASTA_DESTINO, novo_nome)

            mover_arquivo(arquivo, destino)
            atualizar_excel(destino)

    atualizar_excel(PASTA_ARQUIVO)
    print("🎉 Processo finalizado com sucesso!")
    driver.quit()
