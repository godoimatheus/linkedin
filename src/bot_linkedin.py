import threading
from time import sleep
from urllib import parse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PySimpleGUI import PySimpleGUI as sg

driver = None
conection_level = None


def bot_linkedin():
    global driver, conection_level
    email = values["email"]
    password = values["senha"]
    search = values["profissao"]
    formated_search = parse.quote(search)
    msg = values["mensagem"]
    conection_limit = int(values["quantidade"])
    if values["todosGrau"]:
        conection_level = '%5B"S"%2C"O"%5D'
    elif values["segundoGrau"]:
        conection_level = '%5B"S"%5D'
    elif values["terceiroGrau"]:
        conection_level = '%5B"O"%5D'
    city = values["cep"]
    current_time = int(datetime.now().strftime("%H"))
    if current_time >= 18:
        salute = "Boa noite"
    elif 12 <= current_time < 18:
        salute = "Boa tarde"
    else:
        salute = "Bom dia"
    print("Abrindo navegador...")
    print("Verificando atualizações")
    # abrir navegador
    if values["chrome"]:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )
    elif values["edge"]:
        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install())
        )
    elif values["firefox"]:
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install())
        )
    # navegador.maximize_window()
    wait = WebDriverWait(driver, 10)
    print("Acessando linkedin.com")
    driver.get("https://www.linkedin.com/")
    print("Realizando login...")
    email_box = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="session_key"]'))
    )
    email_box.send_keys(email)
    driver.find_element(By.XPATH, '//*[@id="session_password"]').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="session_password"]').send_keys(Keys.ENTER)
    sleep(1)
    print("Checando se existe captcha")

    # checar url
    current_url = driver.current_url
    if "checkpoint" in current_url:
        while True:
            current_url = driver.current_url
            print("Resolva o captcha para prosseguir")
            if "checkpoint" not in current_url:
                break

    # remover solicitacoes
    if values["tirarConexao"]:
        print("Removendo conexões")
        driver.get("https://www.linkedin.com/mynetwork/invitation-manager/sent/")
        sleep(5)
        remove_button = driver.find_elements(By.CLASS_NAME, "artdeco-button__text")
        remove_count = 0
        for b in remove_button:
            if b.text == "Retirar":
                b.click()
                sleep(0.7)
                confirm = driver.find_element(
                    By.XPATH, "/html/body/div[3]/div/div/div[3]/button[2]/span"
                )
                confirm.click()
                print(f"Quantidade de pessoas removidas: {remove_count}")
                sleep(0.7)
            else:
                continue
    if values["naoRemoverConexao"]:
        pass

    sleep(1)
    print("Página de resultados da pesquisa de pessoas")
    search_page = f"https://www.linkedin.com/search/results/people/?keywords={formated_search}&network={conection_level}&origin=SWITCH_SEARCH_VERTICAL"
    driver.get(search_page)

    # filtrar por local
    sleep(5)
    filter_button = driver.find_elements(By.TAG_NAME, "button")
    print("Selecionando cidade/estado/país")
    for button in filter_button:
        if button.text == "Localidades":
            button.click()
            # sleep(1)
            city_search = driver.find_element(
                By.XPATH,
                '//*[@id="artdeco-hoverable-artdeco-gen-43"]/div['
                "1]/div/form/fieldset/div[1]/div/div/input",
            )
            city_search.send_keys(city)
            sleep(1)
            city_search.send_keys(Keys.ARROW_DOWN)
            city_search.send_keys(Keys.ENTER)
            search_results = driver.find_element(
                By.XPATH,
                "/html/body/div[4]/div[3]/div[2]/section/div/nav/div/ul/li[4]/div/div/div/div[1]/div/form/fieldset/div[2]/button[2]/span",
            )
            wait.until(
                EC.element_to_be_clickable(search_results)
            )  # alteração para esperar
            sleep(0.5)
            search_results.click()
            sleep(1)
            print(f"{city} selecionado para pesquisa")
            break
        else:
            continue
    print("Buscando conectar")
    count = 0
    page = 0
    print("Resultado da pesquisas conforme filtros")
    while conection_limit > count:
        page += 1
        sleep(1)
        print(f"Página {page}")
        current_url = driver.current_url
        driver.get(f"{current_url}&page={page}")

        # conectar
        sleep(5)
        conection_button = driver.find_elements(By.CLASS_NAME, "artdeco-button__text")
        for button in conection_button:
            if button.text == "Conectar":
                button.click()
                try:
                    # pegar nome
                    sleep(1)
                    name = driver.find_element(By.TAG_NAME, "strong")
                    full_name = name.text
                    separate_name = full_name.split(" ")
                    first_name = separate_name[0].capitalize()

                    # add msg
                    note_add = driver.find_element(
                        By.XPATH, "/html/body/div[3]/div/div/div[3]/button[1]"
                    )
                    note_add.click()
                    sleep(1)
                    text_area = driver.find_element(By.ID, "custom-message")
                    note = f"{salute}, {first_name}, tudo bem? {msg}"
                    text_area.send_keys(note)
                    sleep(1)
                    send_button = driver.find_element(
                        By.XPATH, "/html/body/div[3]/div/div/div[3]/button[2]/span"
                    )
                    send_button.click()
                    print(f"Conectar com {first_name}...")
                    count += 1
                except:
                    pass
                print(f"Número de conexão atual: {count}")
                if count == conection_limit:
                    print("Chegou a limite definido")
                    break
            elif button.text == "Pendente" or "Seguindo" or "Enviar mensagem":
                continue
        if page == 100:
            print("Chegamos a última página, inicie a pesquisa novamente")
            break
    sleep(1)
    print("Fechando o navegador")
    driver.quit()
    print("FIM")
    print()
    print("https://github.com/godoimatheus")


sg.theme("Dark Blue 3")

layout = [
    [
        sg.Column(
            [
                [sg.Text("E-mail", size=(10, 0))],
                [sg.Input(key="email")],
                [sg.Text("Senha", size=(10, 0))],
                [sg.Input(key="senha", password_char="*")],
                [sg.Text("Profissão", size=(10, 0))],
                [sg.Input(key="profissao")],
                [sg.Text("Filtros")],
                [
                    sg.Radio(
                        "2º grau e 3º grau ou +", "grau", default=True, key="todosGrau"
                    ),
                    sg.Radio("2º grau", "grau", key="segundoGrau"),
                    sg.Radio("3º grau", "grau", key="terceiroGrau"),
                ],
                [sg.Text("Cidade/Estado/País")],
                [sg.Input(default_text="Brasil", key="cep")],
                [sg.Text("Mensagem", size=(10, 0))],
                [
                    sg.Multiline(
                        key="mensagem",
                        size=(45, 6),
                        default_text="O Linkedin limita em 300 caracteres, "
                        "mas como teremos uma saudação e o nome da pessoa no começo, "
                        "use somente o tamanho desta caixa",
                    )
                ],
                [
                    sg.Text("Quantidade", size=(10, 0)),
                    sg.Slider(
                        range=(1, 100),
                        default_value=1,
                        orientation="h",
                        key="quantidade",
                        size=(25, 16),
                    ),
                ],
                [sg.Text("Remover pedidos de conexão")],
                [
                    sg.Radio("Sim", "remover", key="tirarConexao"),
                    sg.Radio("Não", "remover", default=True, key="naoRemoverConexao"),
                ],
                [sg.Text("Selecione o navegador")],
                [
                    sg.Radio("Chrome", "browser", default=True, key="chrome"),
                    sg.Radio("Edge", "browser", key="edge"),
                    sg.Radio("Firefox", "browser", key="firefox"),
                ],
                [sg.Button("INICIAR", size=(10, 2)), sg.Button("PARAR", size=(10, 2))],
            ],
            element_justification="left",
        ),
        sg.VSeperator(),
        sg.Column(
            [[sg.Text("log")], [sg.Output(size=(45, 35))]],
            element_justification="center",
        ),
    ]
]

# janela
window = sg.Window("BOT CONEXÃO LINKEDIN", layout)

while True:
    events, values = window.read()
    if events == sg.WINDOW_CLOSED:
        break
    if events == "PARAR":
        try:
            print("Fechando o navegador")
            driver.quit()
        except:
            pass

    if events == "INICIAR":
        thread = threading.Thread(target=bot_linkedin)
        thread.start()
window.close()
