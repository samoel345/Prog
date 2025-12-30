import os
import time
import shutil
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# === CONFIGURAÇÕES ===
CAMINHO_CHROMEDRIVER = r"C:\Users\685727\OneDrive - DMA Distribuidora S A\Desktop\Baixar_espelhos\Drive_crhome\chromedriver.exe"
ARQUIVO_USUARIO = r"C:\Users\685727\OneDrive - DMA Distribuidora S A\Desktop\Baixar_espelhos\Meses_espelhos.xlsx"

usuario=input("Insira o e-mail")
senha=input("Insira a Senha:")

credecias=[usuario,senha]


df = pd.read_excel(ARQUIVO_USUARIO)
MES_ALVO = str(df.loc[0, 'mes'])
ANO_ALVO = str(df.loc[0, "ano"])

options = Options()
driver = webdriver.Chrome(service=Service(CAMINHO_CHROMEDRIVER), options=options)
wait = WebDriverWait(driver, 30)

# === FUNÇÕES ===

def login():
    driver.get("https://app.ahgora.com.br/relatorios")
    driver.set_window_size(1024, 768)
    driver.set_window_position(100, 100)
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(credecias[0] + '\n')
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))).send_keys(credecias[1] + '\n')
    print("✅ Login realizado com sucesso!")

def selecionar_empresa():
    empresa_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'a555958 - DMA DISTRIBUIDORA S/A (PRODUÇÃO)')]/ancestor::div[@role='button']")))
    empresa_btn.click()
    print("✅ Empresa selecionada!")
    time.sleep(5)

def gerar_relatorios():
    gerar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gerar novos relatórios')]/parent::button")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gerar_btn)
    gerar_btn.click()
    print("✅ Botão 'Gerar novos relatórios' clicado!")

    relatorios = ["Afastamentos", "Batidas Ímpares", "Diário de totais", "Totais"]
    campo = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'id-autocomplete-multiple-Selecione')]")))
    for relatorio in relatorios:
        campo.click()
        campo.clear()
        campo.send_keys(relatorio)
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{relatorio}')]"))).click()
        print(f"✅ Relatório '{relatorio}' selecionado!")

    campo.send_keys(Keys.ESCAPE)
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "MuiAutocomplete-option")))
    print("✅ Todos os relatórios foram selecionados!")

def selecionar_data():
    input_data = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[contains(@class, '_2t8pekO7_rn5BQDaNUsF79')])[2]")))
    input_data.click()
    print("✅ Calendário aberto!")

    for _ in range(12):
        ano_atual = driver.find_element(By.CLASS_NAME, "react-datepicker-year-header").text.strip()
        if ano_atual == ANO_ALVO:
            break
        elif int(ano_atual) < int(ANO_ALVO):
            driver.find_element(By.CLASS_NAME, "react-datepicker__navigation--next").click()
        else:
            driver.find_element(By.CLASS_NAME, "react-datepicker__navigation--previous").click()
        time.sleep(0.5)

    for mes in driver.find_elements(By.CLASS_NAME, "react-datepicker__month-text"):
        if mes.text.strip().lower() == MES_ALVO.lower():
            mes.click()
            break

    print("✅ Data final selecionada!")

def selecionar_velocidade():
    campo = wait.until(EC.element_to_be_clickable((By.ID, "id-autocomplete-Velocidade de Geração")))
    campo.click()
    campo.clear()
    campo.send_keys("Informações atualizadas (velocidade normal)")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Informações atualizadas (velocidade normal)')]"))).click()
    print("✅ Velocidade de geração configurada!")

    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gerar relatórios')]/parent::button"))).click()
    print("✅ Relatórios disparados!")
    time.sleep(480)
    print("⏳ Aguardando 8 minutos para o processamento dos relatórios...")

def configurar_afastamentos():
    relatorio_afastamento = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//a[contains(text(), 'Afastamentos')]"
    )))
    relatorio_afastamento.click()
    print("✅ Relatório 'Afastamentos' aberto!")

    # Aguarda o carregamento do select
    time.sleep(1)

    # Seleciona o select pelo atributo name (mais robusto)
    select_element = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//select[@size="1" and @name="filterOptions"]'
    )))
    select_obj = Select(select_element)
    select_obj.select_by_value("agrupado")
    print("✅ Opção 'Agrupado por Período' selecionada!")

    # Clica no botão para gerar o relatório
    botao_gerar = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[contains(@class, '_2jHx3p6_MqWsTtB_jglcst') and .//div[text()='Gerar Relatório']]"
    )))
    botao_gerar.click()
    print("✅ Botão de geração do relatório 'Afastamentos'")

def acessar_batidas_impares():
    batidas_impares_link = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//a[contains(text(), 'Batidas Ímpares')]"
    )))
    batidas_impares_link.click()
    print("✅ Relatório 'Batidas Ímpares' aberto!")

    driver.switch_to.window(driver.window_handles[-1])
    print("✅ Foco trocado para a aba 'Batidas Ímpares'!")

def renomear_e_mover_arquivo(nome_destino, pasta_destino):
    try:
        pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')
        os.makedirs(pasta_destino, exist_ok=True)
        destino_final = os.path.join(pasta_destino, nome_destino)
        if os.path.exists(destino_final):
            os.remove(destino_final)
        arquivos_download = [f for f in os.listdir(pasta_download) if f.lower().endswith('.xlsx')]
        if not arquivos_download:
            print("❌ Nenhum arquivo .xlsx encontrado na pasta de downloads!")
            return False
        arquivo_baixado = max([os.path.join(pasta_download, f) for f in arquivos_download], key=os.path.getctime)
        shutil.move(arquivo_baixado, destino_final)
        print(f"✅ Arquivo movido e renomeado para: {destino_final}")
        return True
    except Exception as e:
        print(f"❌ Erro ao mover/renomear o arquivo baixado: {e}")
        return False

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    login()
    selecionar_empresa()
    configurar_afastamentos()
    acessar_batidas_impares()
    print("✅ Processo concluído!")
