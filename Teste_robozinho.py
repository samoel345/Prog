from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

Mes_final=input("Digite o mês final:")

CAMINHO_CHROMEDRIVER = r"C:\Users\685727\OneDrive - DMA Distribuidora S A\Documents\Robozinho\Drive_crhome\chromedriver.exe"
USUARIO = "samoel.silva@grupodma.com.br"
SENHA = "Dma@145353/"

options = Options()
driver = webdriver.Chrome(service=Service(CAMINHO_CHROMEDRIVER), options=options)

try:
    driver.set_window_size(1024, 768)
    driver.set_window_position(100, 100)

    driver.get("https://app.ahgora.com.br/relatorios")

    wait = WebDriverWait(driver, 20)

    # Preenche o e-mail
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    email_input.clear()
    email_input.send_keys(USUARIO)
    email_input.send_keys('\n')  # Pressiona Enter após digitar o email

    # Espera o campo senha aparecer (usando apenas XPATH)
    try:
        senha_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
        senha_input.clear()
        senha_input.send_keys(SENHA)
        senha_input.send_keys('\n')  # Pressiona Enter após digitar a senha
    except Exception as e:
        print("Erro ao localizar o campo de senha:", e)
        driver.quit()
        exit(1)

    print("Login realizado com sucesso!")


    # Aguarda o seletor de empresa aparecer (ajuste o XPATH conforme necessário)
    try:
        # Clica no botão da empresa pelo texto exato
        empresa_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'a555958 - DMA DISTRIBUIDORA S/A (PRODUÇÃO)')]/ancestor::div[@role='button']")))
        empresa_btn.click()
        print("Empresa selecionada com sucesso!")
        # Aguarda 15 segundos para garantir o carregamento completo da página
        time.sleep(15)
        # Clica no botão "Gerar novos relatórios" (aguarda até 30s, faz scroll até o botão)
        try:
            gerar_btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gerar novos relatórios')]/parent::button"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gerar_btn)
            time.sleep(1)
            gerar_btn.click()
            print("Botão 'Gerar novos relatórios' clicado!")

            # Seleciona múltiplos relatórios no campo de autocomplete
            relatorios = [
                "Afastamentos",
                "Batidas Ímpares",
                "Diário de totai",
                "Totais"
            ]
            campo_relatorio = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'id-autocomplete-multiple-Selecione')]"))
            )
            for relatorio in relatorios:
                # Limpa o campo antes de digitar o próximo relatório
                campo_relatorio.click()
                campo_relatorio.clear()
                time.sleep(0.5)
                campo_relatorio.send_keys(relatorio)
                time.sleep(1.5)  # Aguarda a lista suspensa aparecer
                opcao = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{relatorio}')]"))
                )
                opcao.click()
                print(f"Relatório '{relatorio}' selecionado!")
                time.sleep(0.5)
            # Após selecionar o último relatório, fecha a lista de autocomplete (pressiona ESC)
            from selenium.webdriver.common.keys import Keys
            campo_relatorio.send_keys(Keys.ESCAPE)
            # Aguarda a lista de autocomplete sumir completamente
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiAutocomplete-option"))
            )
            # Seleciona a data final após selecionar os relatórios
            try:
                # Seleciona todos os campos de data e pega o último (data final)
                campos_data = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//input[contains(@class, '_2t8pekO7_rn5BQDaNUsF79') and @type='text' and contains(@value, '/') ]"))
                )
                campo_data_final = campos_data[-1]  # Pega o último campo encontrado
                # Aguarda a lista de autocomplete sumir antes de clicar no campo de data final
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "MuiAutocomplete-option"))
                )
                # Aguarda o campo estar visível e clicável
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(campo_data_final))
                campo_data_final.click()
                time.sleep(1)

                # Aguarda o calendário aparecer
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "react-datepicker"))
                )

                # Seleciona o ano no calendário, se necessário
                ano_alvo = "2025"
                for _ in range(12):  # Limita tentativas para evitar loop infinito
                    try:
                        ano_atual = driver.find_element(By.CLASS_NAME, "react-datepicker-year-header").text.strip()
                        if ano_atual == ano_alvo:
                            break
                        elif int(ano_atual) < int(ano_alvo):
                            driver.find_element(By.CLASS_NAME, "react-datepicker__navigation--next").click()
                        else:
                            driver.find_element(By.CLASS_NAME, "react-datepicker__navigation--previous").click()
                        time.sleep(0.5)
                    except Exception as e:
                        print("Erro ao selecionar o ano no calendário:", e)
                        break
                
                # Seleciona o mês desejado (exemplo: outubro)
                mes_alvo = Mes_final
                try:
                    meses = driver.find_elements(By.CLASS_NAME, "react-datepicker__month-text")
                    for mes in meses:
                        if mes.text.strip().lower() == mes_alvo:
                            mes.click()
                            break
                except Exception as e:
                    print("Erro ao selecionar o mês no calendário:", e)

                print("Data final selecionada no calendário!")
                time.sleep(1)
                # Clica no campo "Velocidade de Geração" após selecionar a data final
                campo_velocidade = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "id-autocomplete-Velocidade de Geração"))
                )
                campo_velocidade.click()
                print("Campo 'Velocidade de Geração' clicado!")
                time.sleep(1)
                campo_velocidade.clear()
                campo_velocidade.send_keys("Informações atualizadas (velocidade normal)")
                time.sleep(1)
                # Seleciona a opção correta na lista suspensa, se aparecer
                opcao_velocidade = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Informações atualizadas (velocidade normal)')]"))
                )
                opcao_velocidade.click()
                print("Opção de velocidade selecionada!")
                time.sleep(0.5)

                # Clica no botão "Gerar relatórios" após selecionar a velocidade
                gerar_relatorios_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gerar relatórios')]/parent::button"))
                )
                gerar_relatorios_btn.click()
                print("Botão 'Gerar relatórios' clicado!")
                # Aguarda o link "Afastamentos" ficar disponível e clica nele, depois seleciona o filtro
                # Aguarda o link "Afastamentos" ficar disponível e clica nele, depois seleciona o filtro
                link_afastamentos = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/dynamicReport/afastamentos_v2') and contains(text(), 'Afastamentos')]"))
                )
                link_afastamentos.click()
                print("Link 'Afastamentos' clicado!")

                # Seleciona a opção desejada no select após abrir a página de Afastamentos
                select_afastamento = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.NAME, "filterOptions"))
                )
                from selenium.webdriver.support.ui import Select
                select = Select(select_afastamento)
                select.select_by_value("agrupado")  # Altere para "agrupadoMatricula" ou "detalhado" se desejar
                print("Opção 'Agrupado por Período' selecionada no filtro de afastamentos!")

                # Clica no botão "Gerar Relatório" após selecionar o filtro
                btn_gerar_relatorio = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Gerar Relatório'] and @type='submit']"))
                )
                btn_gerar_relatorio.click()
                print("Botão 'Gerar Relatório' clicado!")

                print("Aguardando 6 minutos para o relatório ser processado...")
                time.sleep(360)

                # Aguarda o botão de download (ícone de nuvem) ficar disponível e clica nele
                btn_download = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//svg[@data-testid='CloudDownloadIcon']]"))
                )
                btn_download.click()
                print("Botão de download clicado!")

                # Aguarda a opção "Baixar em .xlsx" aparecer e clica nela
                opcao_xlsx = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Baixar em .xlsx')]"))
                )
                opcao_xlsx.click()
                print("Opção 'Baixar em .xlsx' selecionada!")
                time.sleep(2)  # Aguarda o download iniciar
                # === NOVO BLOCO: Move e renomeia o arquivo baixado ===
                import os
                import shutil

                try:
                    # Caminho da pasta de download padrão do usuário
                    pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')
                    # Pasta de destino na rede
                    pasta_destino = r"\\prddfsr01\OPERACOES\CONTROLE_E_GESTAO\41. Ponto Web Ahgora\base_bd_afastamentos"
                    nome_destino = "bd_afastamentos.xlsx"

                    # Garante que a pasta de destino existe
                    os.makedirs(pasta_destino, exist_ok=True)

                    # Remove arquivo existente na pasta de destino, se houver
                    destino_final = os.path.join(pasta_destino, nome_destino)
                    if os.path.exists(destino_final):
                        os.remove(destino_final)

                    # Procura o arquivo mais recente baixado na pasta Downloads
                    arquivos_download = [f for f in os.listdir(pasta_download) if f.lower().endswith('.xlsx')]
                    if not arquivos_download:
                        print("Nenhum arquivo .xlsx encontrado na pasta de downloads!")
                    else:
                        arquivo_baixado = max([os.path.join(pasta_download, f) for f in arquivos_download], key=os.path.getctime)
                        # Move e renomeia
                        shutil.move(arquivo_baixado, destino_final)
                        print(f"Arquivo movido e renomeado para: {destino_final}")
                except Exception as e:
                    print(f"Erro ao mover/renomear o arquivo baixado: {e}")
            except Exception as e:
                print("Erro ao selecionar a data final:", e)
                driver.quit()
                exit(1)
        except Exception as e:
            print("Erro ao clicar no botão 'Gerar novos relatórios':", e)
            driver.quit()
            exit(1)
    except Exception as e:
        print("Erro ao selecionar a empresa:", e)
        driver.quit()
        exit(1)



    # Aguarda 7 minutos antes de selecionar os 4 botões/links
    print("Aguardando 7 minutos antes de selecionar os botões de relatórios...")
    time.sleep(420)  # 7 minutos = 420 segundos

    try:
        botoes = [
            ("Afastamentos", "/dynamicReport/afastamentos_v2"),
            ("Batidas Ímpares", "/dynamicReport/batidas_impares_novo"),
            ("Diário de totais", "/dynamicReport/diario_totais_funcionarios"),
            ("Totais", "/dynamicReport/totais_funcionarios")
        ]
        for texto, href in botoes:
            xpath = f"//a[contains(@href, '{href}') and contains(text(), '{texto}') and contains(@class, 'jss19')]"
            link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            link.click()
            print(f"Botão '{texto}' clicado!")
            time.sleep(2)  # Aguarda 2 segundos entre os cliques

            # Ações específicas para cada relatório
            if texto == "Batidas Ímpares":
                try:
                    # Apenas clica no botão Gerar Relatório
                    btn_gerar_relatorio = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Gerar Relatório'] and @type='submit']"))
                    )
                    btn_gerar_relatorio.click()
                    print("Botão 'Gerar Relatório' clicado em Batidas Ímpares!")
                    time.sleep(2)
                except Exception as e:
                    print(f"Erro ao clicar em Gerar Relatório em Batidas Ímpares: {e}")
            elif texto == "Diário de totais":
                try:
                    # Seleciona o input correto pelo placeholder "Nenhum arquivo selecionado"
                    input_csv = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @placeholder='Nenhum arquivo selecionado']"))
                    )
                    print("Input de arquivo diário localizado!")
                    time.sleep(1)

                    # Preenche o campo com o caminho do arquivo CSV desejado
                    caminho_csv = r"\\prddfsr01\OPERACOES\CONTROLE_E_GESTAO\41. Ponto Web Ahgora\tipos_horas_diario.csv"
                    input_csv.clear()
                    input_csv.send_keys(caminho_csv)
                    print(f"Arquivo CSV selecionado: {caminho_csv}")

                    # Prossegue normalmente (mantém as caixas de seleção, se necessário)
                    try:
                        checkbox_negative_sinal = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @name='isNegativeSinal']"))
                        )
                        if not checkbox_negative_sinal.is_selected():
                            checkbox_negative_sinal.click()
                            print("Checkbox 'isNegativeSinal' marcada!")
                        else:
                            print("Checkbox 'isNegativeSinal' já estava marcada.")
                    except Exception as e:
                        print(f"Não foi possível marcar a checkbox 'isNegativeSinal': {e}")

                    try:
                        checkbox_not_show_overtime = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @name='notShowOvertime']"))
                        )
                        if not checkbox_not_show_overtime.is_selected():
                            checkbox_not_show_overtime.click()
                            print("Checkbox 'notShowOvertime' marcada!")
                        else:
                            print("Checkbox 'notShowOvertime' já estava marcada.")
                    except Exception as e:
                        print(f"Não foi possível marcar a checkbox 'notShowOvertime': {e}")

                    # Agora clica no botão Gerar Relatório
                    btn_gerar_relatorio = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Gerar Relatório'] and @type='submit']"))
                    )
                    btn_gerar_relatorio.click()
                    print("Botão 'Gerar Relatório' clicado em Diário de totais!")
                    time.sleep(2)

                    # === NOVO BLOCO: Move e renomeia o arquivo baixado ===
                    import os
                    import shutil
                    try:
                        # Caminho da pasta de download padrão do usuário
                        pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')
                        # Pasta de destino na rede
                        pasta_destino = r"\\prddfsr01\OPERACOES\CONTROLE_E_GESTAO\41. Ponto Web Ahgora\base_bd_ausencias_batidas"
                        nome_destino = "bd_ausencias_batidas.xlsx"

                        # Garante que a pasta de destino existe
                        os.makedirs(pasta_destino, exist_ok=True)

                        # Remove arquivo existente na pasta de destino, se houver
                        destino_final = os.path.join(pasta_destino, nome_destino)
                        if os.path.exists(destino_final):
                            os.remove(destino_final)

                        # Procura o arquivo mais recente baixado na pasta Downloads
                        arquivos_download = [f for f in os.listdir(pasta_download) if f.lower().endswith('.xlsx')]
                        if not arquivos_download:
                            print("Nenhum arquivo .xlsx encontrado na pasta de downloads!")
                        else:
                            arquivo_baixado = max([os.path.join(pasta_download, f) for f in arquivos_download], key=os.path.getctime)
                            # Move e renomeia
                            shutil.move(arquivo_baixado, destino_final)
                            print(f"Arquivo movido e renomeado para: {destino_final}")
                    except Exception as e:
                        print(f"Erro ao mover/renomear o arquivo baixado de Diário de totais: {e}")
                except Exception as e:
                    print(f"Erro ao processar Diário de totais: {e}")
            elif texto == "Totais":
                try:
                    # Seleciona o input do arquivo tipos_horas_totais.csv
                    input_csv = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@value, 'tipos_horas_totais.csv')]"))
                    )
                    print("Input 'tipos_horas_totais.csv' localizado em Totais!")
                    time.sleep(1)

                    # Marca as caixas de seleção solicitadas
                    try:
                        checkbox_negative_sinal = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @name='isNegativeSinal']"))
                        )
                        if not checkbox_negative_sinal.is_selected():
                            checkbox_negative_sinal.click()
                            print("Checkbox 'isNegativeSinal' marcada em Totais!")
                        else:
                            print("Checkbox 'isNegativeSinal' já estava marcada em Totais.")
                    except Exception as e:
                        print(f"Não foi possível marcar a checkbox 'isNegativeSinal' em Totais: {e}")

                    try:
                        checkbox_centesimal_hours = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @name='centesimalHours']"))
                        )
                        if not checkbox_centesimal_hours.is_selected():
                            checkbox_centesimal_hours.click()
                            print("Checkbox 'centesimalHours' marcada em Totais!")
                        else:
                            print("Checkbox 'centesimalHours' já estava marcada em Totais.")
                    except Exception as e:
                        print(f"Não foi possível marcar a checkbox 'centesimalHours' em Totais: {e}")

                    # Agora clica no botão Gerar Relatório
                    btn_gerar_relatorio = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Gerar Relatório'] and @type='submit']"))
                    )
                    btn_gerar_relatorio.click()
                    print("Botão 'Gerar Relatório' clicado em Totais!")
                    time.sleep(2)
                except Exception as e:
                    print(f"Erro ao processar Totais: {e}")
    except Exception as e:
        print(f"Erro ao clicar nos botões de relatórios: {e}")

    input("Pressione ENTER para fechar o navegador...")

finally:
    driver.quit()
