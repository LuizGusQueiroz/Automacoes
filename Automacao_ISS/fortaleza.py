from functions import *

path = r'C:\Users\Singular.RESERVA004\PycharmProjects\ISS Selenium\notas-Fortaleza'
# Configurações do Chrome
options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-infobars')
options.add_argument('--safebrowsing-disable-download-protection')
options.add_argument('--safebrowsing-disable-extension-blacklist')
options.add_argument('--safebrowsing-manual-download-blacklist')
options.add_argument('--start-maximized')
options.add_experimental_option('prefs', {
    'download.default_directory': path,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
})
service = Service(ChromeDriverManager().install())

nav = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(nav, 60)


def clica(xpath: str, n: int = 50) -> None:
    '''
    Tenta até n vezes clicar no botão com xpath passado no campo 'xpath'
    tendo uma pausa de 0.5s entre cada tentativa
    '''
    wait.until(EC.element_to_be_clickable(('xpath', xpath)))
    sleep(0.5)
    for _ in range(n):
        try:
            nav.find_element('xpath', xpath).click()
            return
        except Exception as e:
            sleep(0.5)
    print(f'Erro ao clicar em {xpath}')


# Vai para o site do ISS Fortaleza
nav.get('https://iss.fortaleza.ce.gov.br/grpfor/login.seam?cid=928590')

# Lê os dados de acesso
dados = pd.read_excel('ACESSO ISS - ( SINGULAR ).xlsx')
# Filtra os dados apenas de Fortaleza
dados = dados[dados['MUNICIPIO'] == 'FORTALEZA'].reset_index(drop=True)

acessos = dados['LOGIN ISS'].unique()

for acesso in range(len(acessos)):
    dados_temp = dados[dados['LOGIN ISS'] == acessos[acesso]]

    login = dados_temp['LOGIN ISS'].iloc[0]
    senha = dados_temp['SENHA ISS'].iloc[0]

    # Verifica se o botão de login está na tela, enquanto ele estiver, tenta fazer o login
    while nav.find_elements('xpath', '//*[@id="login:botaoEntrar"]'):
        # Preenche os dados de acesso
        nav.find_element('xpath', '//*[@id="login:username"]').send_keys(login)
        nav.find_element('xpath', '//*[@id="login:password"]').send_keys(senha)
        nav.find_element('xpath', '//*[@id="login:captchaDecor:captchaLogin"]').send_keys()
        sleep(10)  # Tempo para o usuário preencher o capcha
        # Clica no botão 'Entrar'
        nav.find_element('xpath', '//*[@id="login:botaoEntrar"]').click()
        sleep(1)  # Espera a página carregar

    # Extrai os cnpjs a partir de uma tabela
    cnpjs = nav.find_element('xpath', '//*[@id="alteraInscricaoForm"]').text.split('\n')
    cnpjs = cnpjs[5::3]

    n_encontr = 0

    for row in range(dados_temp.shape[0]):

        cnpj = dados_temp['CNPJ'].iloc[row]
        emp = ''.join(i for i in cnpj if i.isnumeric())

        # Quando só há um cnpj no login, a tabela não aparece, então só é necessário
        # verificar em qual linha clicar quando houver mais que 1 cnpj.
        if len(cnpjs) > 1:
            achou = False
            for i, cnpj_i in enumerate(cnpjs):
                if cnpj_i == cnpj:  # Clica na linha correta e espera a página carregar
                    achou = True
                    nav.find_element('xpath',
                                     f'//*[@id="alteraInscricaoForm:empresaDataTable:{i}:linkDocumento"]').click()
                    if row > n_encontr:
                        sleep(0.5)
                        nav.find_element('xpath', '//*[@id="alteraInscricaoForm:botaoOk"]').click()
                    sleep(0.5)
                    break
            if not achou:
                print(f'{cnpj} não encontrado')
                n_encontr += 1
                continue

        # Clica em 'Consultar NFS-e'
        clica('//*[@id="homeForm:divHotLinks"]/div[4]')

        ## Consulta as notas de Serviço Prestados

        # Clica em 'Competência/Tomador'
        clica('//*[@id="consultarnfseForm:competencia_prestador_tab_lbl"]')
        # Clica em 'Consultar'
        sleep(1)
        clica('//*[@id="consultarnfseForm:j_id231"]')
        sleep(2)
        # Verifica se houve alguma mensagem de erro
        if nav.find_elements('xpath', '//*[@id="mensagens"]/dt/span'):
            pass
        else:  # Se não houveram erros, realiza a extração das NFS

            # Espera o carregamento
            wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="consultarnfseForm:j_id318"]')))
            # Acessa os índices das páginas
            pags = nav.find_element('xpath',
                                    '//*[@id="consultarnfseForm:dataTable:j_id368_table"]').text.split()[2:-2]
            pags = [int(pag) for pag in pags]
            # Percorre as páginas
            for pag in pags:
                clica(f'//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[{pag + 3}]')
                # Espera a página carregar
                for _ in range(20):
                    try:
                        wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="consultarnfseForm:dataTable:0:j_id360"]')))
                    except Exception as e:
                        sleep(0.5)
                sleep(1)
                # Acessa a tabela de resultados
                linhas = nav.find_element('xpath', '//*[@id="consultarnfseForm:dataTable"]').text.split('\n')[9:]

                for i, linha in enumerate(linhas):
                    if linha.split()[2] == 'NORMAL':
                        # Verifica se o arquivo já foi baixado
                        nome_emp = ((' '.join(linha.split()[4:-2]))
                                    .replace('/', '').replace('\\', ''))
                        num_nf = linha.split()[1]
                        nome_arq = fr'{path}\{nome_emp}-{num_nf}.pdf'
                        if f'{nome_emp}-{num_nf}.pdf' not in os.listdir(path):
                            sleep(0.5)
                            clica(f'//*[@id="consultarnfseForm:dataTable:{i}:j_id360"]')
                            # Clica em 'Exportar PDF'
                            clica('//*[@id="j_id157:panelAcoes"]/tbody/tr/td[1]/input')
                            # Espera o download acabar
                            sleep(1)
                            # Renomeia
                            nome_ant = fr'{path}\relatorio.pdf'
                            for _ in range(20):
                                try:
                                    os.rename(nome_ant, nome_arq)
                                    break
                                except Exception as e:
                                    sleep(0.5)
                            # Clica em 'Voltar'
                            clica('//*[@id="j_id157:panelAcoes"]/tbody/tr/td[2]/input')
                            # Clica em 'Competência/Tomador'
                            clica('//*[@id="consultarnfseForm:competencia_prestador_tab_lbl"]')
                            # Clica em 'Consultar'
                            sleep(1)
                            clica('//*[@id="consultarnfseForm:j_id231"]')
                            # Clica no índice da página
                            clica(f'//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[{pag + 3}]')

        ## Consulta as notas de Serviços tomados

        # Clica em 'Serviços Tomados'
        clica('//*[@id="consultarnfseForm:opTipoRelatorio:1"]')
        # Clica em 'Competência/Tomador'
        clica('//*[@id="consultarnfseForm:abaPorCompetenciaTomador_tab_lbl"]')
        # Clica em 'Consultar'
        sleep(1)
        clica('//*[@id="consultarnfseForm:j_id311"]')
        sleep(2)
        # Verifica se houve alguma mensagem de erro
        if nav.find_elements('xpath', '//*[@id="mensagens"]/dt/span'):
            pass
        else:  # Se não houveram erros, realiza a extração das NFS

            # Espera o carregamento
            wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="consultarnfseForm:j_id318"]')))
            # Acessa os índices das páginas
            pags = nav.find_element('xpath',
                                    '//*[@id="consultarnfseForm:dataTable:j_id368_table"]').text.split()[2:-2]
            pags = [int(pag) for pag in pags]
            # Percorre as páginas
            for pag in pags:
                clica(f'//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[{pag + 3}]')
                # Espera a página carregar
                wait.until(EC.element_to_be_clickable(
                    ('xpath', '//*[@id="consultarnfseForm:dataTable:0:j_id360"]')))
                sleep(1)
                # Acessa a tabela de resultados
                linhas = nav.find_element('xpath',
                                          '//*[@id="consultarnfseForm:dataTable"]').text.split('\n')[9:]

                for i, linha in enumerate(linhas):
                    if linha.split()[2] == 'NORMAL':
                        # Verifica se o arquivo já foi baixado
                        nome_emp = ((' '.join(linha.split()[4:-2]))
                                    .replace('/', '').replace('\\', ''))
                        num_nf = linha.split()[1]
                        nome_arq = fr'{path}\{nome_emp}-{num_nf}.pdf'
                        if f'{nome_emp}-{num_nf}.pdf' not in os.listdir(path):
                            sleep(0.5)
                            # Clica no símbolo de lupa
                            clica(f'//*[@id="consultarnfseForm:dataTable:{i}:j_id360"]')
                            # Clica em 'Exportar PDF'
                            clica('//*[@id="j_id157:panelAcoes"]/tbody/tr/td[1]/input')
                            # Espera o download acabar
                            sleep(1)
                            # Renomeia
                            nome_ant = fr'{path}\relatorio.pdf'
                            for _ in range(20):
                                try:
                                    os.rename(nome_ant, nome_arq)
                                    break
                                except Exception as e:
                                    sleep(0.5)
                            # Clica em 'Voltar'
                            clica('//*[@id="j_id157:panelAcoes"]/tbody/tr/td[2]/input')
                            # Clica em 'Serviços Tomados'
                            clica('//*[@id="consultarnfseForm:opTipoRelatorio:1"]')
                            # Clica em 'Competência/Tomador'
                            clica('//*[@id="consultarnfseForm:abaPorCompetenciaTomador_tab_lbl"]')
                            # Clica em 'Consultar'
                            sleep(1)
                            clica('//*[@id="consultarnfseForm:j_id311"]')
                            # Clica no índice da página
                            clica(
                                f'//*[@id="consultarnfseForm:dataTable:j_id368_table"]/tbody/tr/td[{pag + 3}]')
                            sleep(1)

        # Clica no íncone para trocar de empresa
        clica('//*[@id="j_id151:j_id153"]')
        sleep(1)

    # Fecha a tabela de CNPJs
    clica('//*[@id="ocultarAlteraPrestador"]')
    # Clica em 'Sair'
    clica('//*[@id="j_id14"]')

sleep(5)
