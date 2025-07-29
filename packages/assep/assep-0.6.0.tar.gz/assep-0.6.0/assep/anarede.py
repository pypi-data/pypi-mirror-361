"""Módulo ANAREDE"""
import os
import subprocess
import time
import sys
import pandas as pd
import numpy as np
import easygui
import plotly.express as px
import matplotlib.pyplot as plt
import assep.decks as decks

# pylint: disable=unsubscriptable-object
# pylint "01_ASSEP\assep\anarede.py" > "01_ASSEP\testes\pyl_anarede.txt"
class ANAREDE():
    r"""
    Classe destinada a automatizar a extração de dados diretamente dos arquivos SAV.

    Esta classe contém métodos para extrair dados diretamente de arquivos no formato SAV.
    Ela gera decks para alimentar o ANAREDE, que por sua vez gera relatórios de saída.
    Após o tratamento desses relatórios, os dados desejados são fornecidos.

    Parameters
    ----------
    path : str
        O caminho para o executável do ANAREDE.
    roda_anarede : bool, optional
        Se True, o ANAREDE será executado novamente. O padrão é True.
    clear_temp_folder : bool, optional
        Se True, a pasta temporária será inicializada novamente. O padrão é False.

    Examples
    --------
    Para inicializar a classe, basta chamar ela para o objeto de interesse.

    >>> import anarede as anr
    >>> Path_Anarede = str(r"C:\Cepel\Anarede\V110702\ANAREDE.exe")
    >>> oAnarede = anarede.ANAREDE(Path_Anarede, roda_anarede = True, clear_temp_folder = False)
    """
    ###================================================================================================================
    ###
    ### CÓDIGOS DE INICIALIZAÇÃO
    ###
    ###================================================================================================================
    def __init__(self, path, roda_anarede = True, clear_temp_folder = False):
        """
        Inicializa a instância da classe.

        Esta função define a engine, cria constantes do programa e inicializa algumas variáveis.

        Parameters
        ----------
        path : str
            Caminho para a engine.
        roda_anarede : bool, optional
            Indica se o Anarede será rodado. O padrão é True.
        clear_temp_folder : bool, optional
            Indica se a pasta TEMP será limpa. O padrão é False.

        Returns
        -------
        None
        """
        # Definindo engine
        self.engine = path

        # Cria constantes do programa
        self.clear_temp_folder = clear_temp_folder
        self.roda_anarede = roda_anarede
        self.path_decks = ""
        self.lista_casos = []

    def __initialize_temp_folder(self):
        """
        Inicializa a pasta temporária.

        Esta função verifica se a pasta temporária existe e, se não existir, a cria.
        Em seguida, dependendo da configuração, limpa a pasta TEMP. Se a opção
        'clear_temp_folder' estiver ativada, todos os arquivos na pasta TEMP serão removidos.
        Caso contrário, apenas os arquivos com a extensão 'END' serão removidos.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        SystemExit
            Se não for possível remover um arquivo porque ele está aberto.
        """
        # Checa se a pasta temporária existe
        temp_exist = os.path.exists(self.path_decks)
        if not temp_exist:
            os.makedirs(self.path_decks)

        # Limpa pasta TEMP
        if self.clear_temp_folder:
            for file_name in os.listdir(self.path_decks):
                file = self.path_decks + file_name
                if os.path.isfile(file):
                    try:
                        os.remove(file)
                    except: # pylint: disable=bare-except
                        print(f"Execução abortada! Não foi possível remover o arquivo {file}....ele está aberto?")
                        sys.exit()
        else:
            for file_name in os.listdir(self.path_decks):
                file = self.path_decks + file_name
                if os.path.isfile(file) and file.endswith("END"):
                    try:
                        os.remove(file)
                    except: # pylint: disable=bare-except
                        print(f"Execução abortada! Não foi possível remover o arquivo {file}....ele está aberto?")
                        sys.exit()

    ###================================================================================================================
    ###
    ### CÓDIGOS COMANDO CMD ANAREDE
    ###
    ###================================================================================================================
    def _exe_command_anarede(self, comando, file_end):
        """
        Executa um comando no Anarede.

        Esta função executa um comando no Anarede. Ela verifica se os dados de área existem.
        Em seguida, inicia um subprocesso com o comando fornecido e aguarda até que o arquivo
        de saída seja criado. Por fim, termina o subprocesso.

        Parameters
        ----------
        comando : str
            Comando a ser executado no Anarede.
        file_end : list
            Lista de arquivos de saída esperados.

        Returns
        -------
        None
        """
        # Checar se existe os dados de área
        counter = len(file_end)
        file_dadb = 0
        if os.path.exists(file_end[counter-1]):
            file_dadb = -1

        p = subprocess.Popen(comando)
        report_exist = False
        while report_exist is False:
            report_exist = os.path.exists(file_end[counter-1 + file_dadb])
        p.terminate()

    ###================================================================================================================
    ###
    ### CÓDIGOS IMPORTAR NOME CASOS
    ###
    ###================================================================================================================
    def __deck_list_cases(self, file_out, file_end):
        """
        Cria a lista de casos do Deck.

        Esta função cria uma lista de casos para o Deck. Para cada caso na lista de casos,
        gera arquivos de saída e adiciona comandos ao corpo do Deck. Por fim, retorna o corpo
        do Deck e as listas de arquivos de saída.

        Parameters
        ----------
        file_out : list
            Lista de arquivos de saída.
        file_end : list
            Lista de arquivos de finalização.

        Returns
        -------
        body_list_cases : str
            Corpo do Deck com a lista de casos.
        file_out : list
            Lista atualizada de arquivos de saída.
        file_end : list
            Lista atualizada de arquivos de finalização.
        """
        body_list_cases = []
        counter = 0
        for i, _ in enumerate(self.lista_casos):
            # Contadores e arquivos a serem gerados
            counter = counter + 1
            file_out.append(self.path_decks + "rel_sav_" + str(counter) + ".out")
            file_end.append(self.path_decks + "rel_sav_" + str(counter) + ".end")
            # Corpo do Deck
            body_list_cases.append("(RELATÓRIO - ARQUIVO: " + self.lista_casos[i])
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "rel_sav_" + str(counter) + ".out")
            body_list_cases.append("DOPC")
            body_list_cases.append("FILE L")
            body_list_cases.append("99999")
            body_list_cases.append("ULOG")
            body_list_cases.append("2")
            body_list_cases.append(self.lista_casos[i])
            body_list_cases.append("ARQV LIST")
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "rel_sav_" + str(counter) + ".end")
            body_list_cases.append("(")
        body_list_cases.append("FIM")

        body_list_cases = "\n".join(body_list_cases)

        return body_list_cases, file_out, file_end

    def __get_dic_casos(self, file_out):
        """
        Obtém um dicionário de casos.

        Esta função lê cada arquivo de saída, extrai informações relevantes e cria um
        dicionário para cada caso. Cada dicionário é então adicionado a uma lista.

        Parameters
        ----------
        file_out : list
            Lista de arquivos de saída.

        Returns
        -------
        list_dics : list
            Lista de dicionários, cada um representando um caso.
        """
        list_dics = []
        for i in range(0, len(self.lista_casos)):
            with open(file_out[i], 'r') as file:
                data = file.read()
            data_list = data.splitlines()

            # Definições dos nomes dos arquivos
            diretorio_arquivo = data_list[6].replace("Arquivo Historico: ","").strip()
            nome_arquivo = diretorio_arquivo[diretorio_arquivo.rfind("\\")+1:]
            counter = 11

            while data_list[counter][:6].strip() != "":
                numero_caso = data_list[counter][:6].strip()
                nome_caso = data_list[counter][12:].strip()
                # Salvando resultados
                dic_dados_sav =  {"Diretorio_Arquivo": diretorio_arquivo,
                                "Nome_Arquivo": nome_arquivo,
                                "Numero_Caso": numero_caso,
                                "Nome_Caso":  nome_caso,
                                }
                list_dics.append(dic_dados_sav)
                counter = counter + 1
        return list_dics

    def __get_data_sav(self, suffix_id=""):
        """
        Obtém os dados SAV.

        Esta função verifica se o Anarede será rodado. Se sim, cria a estrutura do deck,
        escreve o deck, executa o Anarede, coleta os dicionários com a lista de casos e
        gera um DataFrame. Se o Anarede não for rodado, tenta ler o CSV com os casos SAV.

        Parameters
        ----------
        suffix_id : str, optional
            Identificador usado para identificar com sufixo os CSVs gerados. O padrão é uma string vazia.

        Returns
        -------
        df_dados_sav : DataFrame
            DataFrame com os dados SAV.

        Raises
        ------
        SystemExit
            Se o tamanho do deck violar os 80 caracteres ou se ocorrer um erro na leitura do CSV.
        """
        start_time = time.time()
        if self.roda_anarede:
            # Criando a estrutura do deck para obter a lista de casos
            file_end = []
            file_out = []
            body_list_cases, file_out, file_end = self.__deck_list_cases(file_out, file_end)

            # Escrevendo deck
            deck_list_cases = self.path_decks + "deck_list_cases.pwf"

            # Checando se o tamanho do deck viola os 80 caracteres
            if len(deck_list_cases)>80:
                print(f"O diretório do arquivo atual possui {len(deck_list_cases)} caracteres!!! Reduza para no máximo 80")
                sys.exit()

            with open(deck_list_cases, "w", encoding='utf-8') as text_file:
                text_file.write(body_list_cases)

            # Elaborando comando
            # comando = self.engine + " " +  deck_list_cases +  " " +  file_end[0]
            comando = self.engine + " " + '"' + deck_list_cases + '"' + " " + '"' + file_end[0] + '"'
            comando = comando.replace("/","\\")

            # Executa ANAREDE
            self._exe_command_anarede(comando, file_end)

            # Coletar dicionários com a lista de casos
            list_dics = self.__get_dic_casos(file_out)

            # Gerando DataFrame
            df_dados_sav = pd.DataFrame(list_dics)
            df_dados_sav.to_csv(self.path_decks + "df_dados_sav" + suffix_id + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")
        else:
            try:
                df_dados_sav = pd.read_csv(self.path_decks + "df_dados_sav" + suffix_id + ".csv", sep=";", encoding="utf-8-sig", decimal=",")
                df_dados_sav = df_dados_sav[df_dados_sav["Diretorio_Arquivo"].isin(self.lista_casos)]
            except: # pylint: disable=bare-except
                print("Erro na leitura do CSV contendo os casos SAV. Favor executar o ANAREDE novamente!")
                sys.exit()


        print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO ANAREDE: COLETA INFORMAÇÕES DOS .SAVs")
        # print("--- %s seconds --- TEMPO ANAREDE: COLETA INFORMAÇÕES DOS .SAVs" % (time.time() - start_time))
        # Resultado da função
        return df_dados_sav

    ###================================================================================================================
    ###
    ### CÓDIGOS RELATÓRIO ANAREDE - RBAR
    ###
    ###================================================================================================================
    def __deck_rbar(self, file_out, file_end, df_casos_sav, list_barra, list_areas):
        """
        Cria o corpo do deck para a análise RBAR.

        Esta função constrói o corpo do deck para a análise RBAR, utilizando os dados fornecidos
        pelo DataFrame df_casos_sav. Dependendo dos parâmetros list_barra e list_areas, diferentes
        seções do deck são criadas para coletar informações sobre barras e áreas específicas.

        Parameters
        ----------
        file_out : list
            Lista de caminhos para os arquivos de saída.
        file_end : list
            Lista de caminhos para os arquivos de finalização.
        df_casos_sav : DataFrame
            DataFrame contendo os dados dos casos SAV.
        list_barra : list or None
            Lista de barras para análise ou None para coletar todas as barras.
        list_areas : list or None
            Lista de áreas para análise ou None para coletar todas as áreas.

        Returns
        -------
        body_list_cases : str
            Corpo do deck para análise RBAR.
        file_out : list
            Lista atualizada de caminhos para os arquivos de saída.
        file_end : list
            Lista atualizada de caminhos para os arquivos de finalização.
        """
        list_paths = df_casos_sav['Diretorio_Arquivo'].tolist()
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()
        body_list_cases = []
        counter = 0
        for i, _ in enumerate(list_paths):
            # Contadores e arquivos a serem gerados
            counter = counter + 1
            file_out.append(self.path_decks + "rel_rbar_" + str(counter) + ".out")
            file_end.append(self.path_decks + "rel_rbar_" + str(counter) + ".end")
            # Corpo do Deck
            body_list_cases.append("(RELATÓRIO - ARQUIVO: " + list_savs[i] + " - " + list_num_cases[i] + "-" + list_name_cases[i])
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "rel_rbar_" + str(counter) + ".out")
            body_list_cases.append("DOPC")
            body_list_cases.append("FILE L")
            body_list_cases.append("99999")
            body_list_cases.append("ULOG")
            body_list_cases.append("2")
            body_list_cases.append(list_paths[i])
            body_list_cases.append("ARQV REST")
            body_list_cases.append(list_num_cases[i])
            body_list_cases.append("DOPC")
            body_list_cases.append("FILE L")
            body_list_cases.append("99999")

            # Diferenciação de acordo com o que se deseja estudar
            ## Caso 1 - Coletando todas barras
            if list_barra is None and list_areas is None:
                body_list_cases.append("RELA RBAR")
            ## Caso 2 - Coletando lista de barras
            elif list_barra is not None and list_areas is None:
                for j, _ in enumerate(list_barra):
                    body_list_cases.append("RELA RBAR CONV")
                    body_list_cases.append(str(list_barra[j]))
                    body_list_cases.append("99999")
            ## Caso 3 - Coletando lista de areas
            elif list_barra is None and list_areas is not None:
                for j, _ in enumerate(list_areas):
                    body_list_cases.append("RELA RBAR AREA")
                    body_list_cases.append(str(list_areas[j]))
            ## Caso 4 - Coletando lista de barras e areas
            elif list_barra is not None and list_areas is not None:
                for j, _ in enumerate(list_barra):
                    body_list_cases.append("RELA RBAR CONV")
                    body_list_cases.append(str(list_barra[j]))
                    body_list_cases.append("99999")
                for j, _ in enumerate(list_areas):
                    body_list_cases.append("RELA RBAR AREA")
                    body_list_cases.append(str(list_areas[j]))
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "rel_rbar_" + str(counter) + ".end")
            body_list_cases.append("(")
        # Adiciona seção para extrair dados de Área e Barra
        file_out.append(self.path_decks + "rel_dadb.out")
        file_end.append(self.path_decks + "rel_dadb.end")
        body_list_cases.append("(RELATÓRIO - EXTRAIR DADOS DE ÁREA")
        body_list_cases.append("ULOG")
        body_list_cases.append("4")
        body_list_cases.append(self.path_decks + "rel_dadb.out")
        body_list_cases.append("DOPC")
        body_list_cases.append("FILE L")
        body_list_cases.append("99999")
        body_list_cases.append("ULOG")
        body_list_cases.append("2")
        body_list_cases.append(list_paths[-1])
        body_list_cases.append("ARQV REST")
        body_list_cases.append(list_num_cases[-1])
        body_list_cases.append("DOPC")
        body_list_cases.append("FILE L")
        body_list_cases.append("99999")
        body_list_cases.append("RELA DADB")
        body_list_cases.append("ULOG")
        body_list_cases.append("4")
        body_list_cases.append(self.path_decks + "rel_dadb.end")
        body_list_cases.append("(")
        body_list_cases.append("FIM")
        body_list_cases = "\n".join(body_list_cases)

        return body_list_cases, file_out, file_end

    def __get_dfs_rbar_area(self, file_out):
        """
        Extrai e processa os resultados da análise RBAR por área.

        Esta função analisa os arquivos de saída da análise RBAR para cada área e cria dataframes
        contendo os dados de barras correspondentes a essas áreas.

        Parameters
        ----------
        file_out : list
            Lista de caminhos para os arquivos de saída da análise RBAR.

        Returns
        -------
        dic_dfs : dict
            Dicionário onde as chaves são os índices dos arquivos de saída e os valores são os dataframes
            contendo os dados da análise RBAR por área.
        """
        # list_dfs = []
        dic_dfs = {}
        for i in range(0, len(file_out)-1):
            # Buscando resultados novos
            if self.roda_anarede:
                # Coletando dados do OUT - AREA
                with open(file_out[i], 'r') as file:
                    data = file.read()
                    # Filtrando o tamanho do deck
                    index = data.find("RELATORIO DE BARRAS CA DO SISTEMA * AREA")
                    data = data[index:]

                # Plota em um arquivo temporário, o código RBAR
                with open(self.path_decks + 'temp.txt', 'w', encoding="utf-8") as f:
                    f.write(data)

                # Define a disposição dos dados
                list_columns=['Numero', 'Nome_Barra', 'Tipo_Barra', 'Estado', 'Tensao_MOD', 'Tensao_ANG', 'Geracao_MW', 'Geracao_Mvar', 'Carga_MW', 'Carga_Mvar', 'Shunt_Mvar']
                colspecs =   [ (2,7),    (8,20),       (22,23),      (132,135),(24,29),      (30,35),      (36,43),      (44,51),        (68,75),    (76,83),      (100,107)  ]

                # Leitura para um dataframe
                df = pd.read_fwf(self.path_decks + "temp.txt", skiprows=0, skipfooter=0, names=list_columns, colspecs=colspecs,  dtype=str)

                # Limpeza nos dados - Elimina dados não numéricos de numero e tipo de barra
                cols = ["Numero", "Tipo_Barra"]
                df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
                df = df[df['Numero'].notna()]
                df[cols] = df[cols].astype(int)

                # Limpar colunas com barras desligadas
                df = df[df["Estado"] != "DES"]

                if len(df) > 0:
                    # Adequa colunas para float
                    list_columns = ["Tensao_MOD", "Tensao_ANG", "Geracao_MW", "Geracao_Mvar", "Carga_MW", "Carga_Mvar", "Shunt_Mvar"]
                    df[list_columns] = df[list_columns].astype(float)

                    # Pegando Área
                    start_block = ["DA BARRA", "NOME ", "---", "...", "NS -", "     ", "NUM. ", "PEL - "]
                    start_block = tuple(start_block)  # Convert list to tuple for faster access
                    list_data_red = []
                    for element in data.splitlines():
                        sliced_element = element[2:46]
                        if sliced_element.strip() and not sliced_element.startswith(start_block):
                            list_data_red.append(sliced_element)
                    num_barras_set = set(df['Numero'].tolist())
                    # print(f"{time.time() - time_x} cria lista reduzida")

                    # time_x = time.time()
                    list_dados_barra = []
                    area = None  # Initialize area
                    for index, value in enumerate(list_data_red):
                        if value.startswith("ELATORIO DE BARRAS"):
                            area = value[39:-1].strip()
                        elif value.startswith("LATORIO DE BARRAS"):
                            area = value[40:-1].strip()
                        elif value.upper().startswith("ASO"):
                            pass
                        elif value[:6].strip().isnumeric():
                            if int(value[:6].strip()) in num_barras_set:
                                dic_dados_barra= {}
                                dic_dados_barra["Numero"] = value[:6].strip()
                                dic_dados_barra["Area"] = area
                                list_dados_barra.append(dic_dados_barra)
                    df_dados_barra = pd.DataFrame(list_dados_barra)
                    df_dados_barra = df_dados_barra.astype(int)
                    # print(f"{time.time() - time_x} cria df")

                    # time_x = time.time()
                    # Complementa Área
                    df = df.merge(df_dados_barra, on='Numero', how='left')

                    # Acerta colunas
                    cols = list(df.columns)
                    # items to be removed
                    unwanted_cols = ['Area', 'Estado', 'Tipo_Barra', 'Numero', 'Nome_Barra',]
                    cols = [ele for ele in cols if ele not in unwanted_cols]
                    cols = unwanted_cols + cols
                    df = df[cols]

                    df.to_csv(self.path_decks + "df_OUT_RBAR_AREA_" + str(i+1) + ".csv", index=False, sep=";", encoding="utf-8", decimal=",")

            # Buscando resultados existentes
            else:
                try:
                    df = pd.read_csv(self.path_decks + "df_OUT_RBAR_AREA_" + str(i+1) + ".csv", sep=";", encoding="utf-8-sig", decimal=",")
                except: # pylint: disable=bare-except
                    print("ERRO FATAL! Não foi possível localizar o df do RBAR em CSV...rodar ANAREDE novamente!")
                    sys.exit()


            # Salva DF na pilha
            dic_dfs[(i)] = df

        return dic_dfs

    # def __get_dfs_rbar_barra(self, file_out):
    #     """None"""
        # list_dfs = []
        # for i in range(0, len(file_out)-1):
        #     # pegando casos novos
        #     if self.roda_anarede:
        #         # Coletando dados do OUT - AREA
        #         with open(file_out[i], 'r') as file:
        #             data = file.read()
        #             # Filtrando o tamanho do deck
        #             index_final = data.find("RELATORIO DE BARRAS CA DO SISTEMA * AREA")
        #             index_start = data.find("RELATORIO DE BARRAS CA DO SISTEMA")
        #             data = data[index_start:index_final]

        #         # Plota em um arquivo temporário, o código RBAR
        #         with open(self.path_decks + 'temp.txt', 'w', encoding="utf-8") as f:
        #             f.write(data)

        #         # Define o dataframe RBAR
        #         list_columns=['Numero', 'Nome_Barra', 'Tipo_Barra', 'Estado']
        #         colspecs =   [  (2,7),     (8,20),       (21,23),  (152,156)]

        #         # Verifica seleção - Módulo da Tensão
        #         if dic_Importacao["Tensao_MOD"]:
        #             list_columns.append('Tensao_MOD')
        #             colspecs.append((28,33))

        #         # Verifica seleção - Ângulo da Tensão
        #         if dic_Importacao["Tensao_ANG"]:
        #             list_columns.append('Tensao_ANG')
        #             colspecs.append((34,39))

        #         # Verifica seleção - Geração Ativa
        #         if dic_Importacao["Geracao_MW"]:
        #             list_columns.append('Geracao_MW')
        #             colspecs.append((40,47))

        #         # Verifica seleção - Geração Reativa
        #         if dic_Importacao["Geracao_Mvar"]:
        #             list_columns.append('Geracao_Mvar')
        #             colspecs.append((64,71))

        #         # Verifica seleção - Carga Ativa
        #         if dic_Importacao["Carga_MW"]:
        #             list_columns.append('Carga_MW')
        #             colspecs.append((88,95))

        #         # Verifica seleção - Carga Reativa
        #         if dic_Importacao["Carga_Mvar"]:
        #             list_columns.append('Carga_Mvar')
        #             colspecs.append((96,103))

        #         # Verifica seleção - Shunt_Mvar
        #         if dic_Importacao["Shunt_Mvar"]:
        #             list_columns.append('Shunt_Mvar')
        #             colspecs.append((120,127))
        #         # list_columns=['Numero', 'Nome_Barra', 'Tipo_Barra', 'Estado', 'Tensao_MOD', 'Tensao_ANG', 'Geracao_MW', 'Geracao_Mvar', 'Carga_MW', 'Carga_Mvar', 'Shunt_Mvar']
        #         # colspecs = [  (2,7),     (8,20),       (22,23),     (132,135), (24,29),      (30,35),      (36,43),      (44,51),        (68,75),     (76,83),     (100,107)  ]
        #         df = pd.read_fwf(self.path_decks + "temp.txt", skiprows=0, skipfooter=0, names=list_columns, colspecs=colspecs,  dtype=str)

        #         # Limpeza nos dados - Elimina dados não numéricos de numero e tipo de barra
        #         cols = ["Numero", "Tipo_Barra"]
        #         df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        #         df = df[df['Numero'].notna()]



        #         # Adequa colunas para inteiro
        #         df[cols] = df[cols].astype(int)

        #         # Adequa colunas para float
        #         list_columns = []
        #         if dic_Importacao["Tensao_MOD"]: list_columns.append("Tensao_MOD")
        #         if dic_Importacao["Tensao_ANG"]: list_columns.append("Tensao_ANG")
        #         if dic_Importacao["Geracao_MW"]: list_columns.append("Geracao_MW")
        #         if dic_Importacao["Geracao_Mvar"]: list_columns.append("Geracao_Mvar")
        #         if dic_Importacao["Carga_MW"]: list_columns.append("Carga_MW")
        #         if dic_Importacao["Carga_Mvar"]: list_columns.append("Carga_Mvar")
        #         if dic_Importacao["Shunt_Mvar"]: list_columns.append("Shunt_Mvar")
        #         df[list_columns] = df[list_columns].astype(float)

        #         # Imprimindo DataFrame-CSV
        #         df.to_csv(self.path_decks + "df_OUT_RBAR_BARRA_" + str(i+1) + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")

        #     # Buscando resultados existentes
        #     else:
        #         try:
        #             df = pd.read_csv(self.path_decks + "df_OUT_RBAR_BARRA_" + str(i+1) + ".csv", sep=";", encoding="utf-8-sig", decimal=",")
        #         except:
        #             print("ERRO FATAL! Não foi possível localizar o df do RBAR em CSV...rodar ANAREDE novamente!")
        #             sys.exit()

        #     # Salva DF na pilha
        #     # if not df.empty:
        #     list_dfs.append(df)

        # return list_dfs
        # pass

    def __get_dfs_rbar(self, file_out, list_barra, list_areas):
        """
        Extrai e processa os resultados da análise RBAR.

        Esta função coordena a extração e processamento dos resultados da análise RBAR, permitindo
        a seleção de barras específicas ou áreas de interesse.

        Parameters
        ----------
        file_out : list
            Lista de caminhos para os arquivos de saída da análise RBAR.
        list_barra : list or None
            Lista de barras para análise ou None para coletar todas as barras.
        list_areas : list or None
            Lista de áreas para análise ou None para coletar todas as áreas.

        Returns
        -------
        dic_dfs : dict
            Dicionário onde as chaves são os índices dos arquivos de saída e os valores são os dataframes
            contendo os dados da análise RBAR.
        """
        if list_barra is not None and list_areas is not None:
            dic_dfs_area = self.__get_dfs_rbar_area(file_out)
            # dic_dfs_BARRA = self.__get_dfs_rbar_barra(file_out)
            # dic_dfs = dic_dfs_area + dic_dfs_BARRA
        elif list_barra is not None:
            # dic_dfs_BARRA = self.__get_dfs_rbar_barra(file_out)
            # dic_dfs =
            pass
        elif list_areas is not None:
            dic_dfs_area = self.__get_dfs_rbar_area(file_out)
            dic_dfs = dic_dfs_area
        elif list_barra is None and list_areas is None:
            dic_dfs_area = self.__get_dfs_rbar_area(file_out)
            dic_dfs = dic_dfs_area

        return  dic_dfs

    def __get_rbar(self, df_casos_sav,  list_barra = None, list_areas = None, make_multilevel_df = False, suffix_id=""):
        """
        Obtém os resultados da análise RBAR.

            Esta função coordena a obtenção dos resultados da análise RBAR, permitindo a seleção
            de barras específicas ou áreas de interesse. Pode opcionalmente criar um DataFrame
            com múltiplos níveis de índice.

        Parameters
        ----------
            df_casos_sav : DataFrame
                DataFrame contendo os dados dos casos SAV.
            list_barra : list or None, optional
                Lista de barras para análise ou None para coletar todas as barras. O padrão é None.
            list_areas : list or None, optional
                Lista de áreas para análise ou None para coletar todas as áreas. O padrão é None.
            make_multilevel_df : bool, optional
                Se True, cria um DataFrame com múltiplos níveis de índice. O padrão é False.
            suffix_id : str, optional
                Identificador usado para diferenciar os arquivos de saída. O padrão é uma string vazia.

        Returns
        -------
            dic_dfs_grouped : dict
                Dicionário contendo os resultados da análise RBAR agrupados por grandeza monitorada.
        """
        # Checando se dicionário com exceções chegou
        start_time = time.time()

        # Verifica necessidade de rodar ANAREDE novamente
        if self.roda_anarede:
            # Criando a estrutura do deck para obter a lista de casos
            file_end = []
            file_out = []
            body_list_cases, file_out, file_end = self.__deck_rbar(file_out, file_end, df_casos_sav, list_barra, list_areas)

            # Escrevendo deck
            deck_rbar = self.path_decks + "deck_rbar.pwf"
            with open(deck_rbar, "w", encoding='utf-8') as text_file:
                text_file.write(body_list_cases)

            # Elaborando comando
            # comando = self.engine + " " + deck_rbar + " " + file_end[0]
            comando = self.engine + " " + '"' + deck_rbar + '"' + " " + '"' + file_end[0] + '"'

            # print("--- %s seconds --- TEMPO PYTHON: CRIAÇÃO DOS DECKS ANAREDE" % (time.time() - start_time))
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CRIAÇÃO DOS DECKS ANAREDE")
            start_time = time.time()

            # Executa ANAREDE
            self._exe_command_anarede(comando, file_end)
            # print("--- %s seconds --- TEMPO ANAREDE: CRIAÇÃO DOS RELATÓRIOS .OUT E .END" % (time.time() - start_time))
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO ANAREDE: CRIAÇÃO DOS RELATÓRIOS .OUT E .END")

            start_time = time.time()
            # Coletar dicionários com a lista de casos
            dic_dfs = self.__get_dfs_rbar(file_out, list_barra, list_areas)
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CONVERSÃO RELATÓRIO .OUT PARA DATAFRAME")

            dic_dfs_grouped = self.__group_rbar_by_variable(df_casos_sav, dic_dfs, make_multilevel_df, suffix_id)

        else:
            list_grandezas = ['Tensao_MOD', 'Tensao_ANG', 'Geracao_MW', 'Geracao_Mvar', 'Carga_MW', 'Shunt_Mvar']
            dic_dfs_grouped = {}
            columns_base = ['Area', 'Tipo_Barra', 'Numero', 'Nome_Barra',]
            columns_filter = []
            # Iterando sobre as linhas do DataFrame
            for _, row in df_casos_sav.iterrows():
                element = str(row["Nome_Arquivo"]) + "\n[" + str(row["Numero_Caso"]) + "] " + str(row["Nome_Caso"])
                columns_filter.append(element)
            cols = columns_base + columns_filter

            for _, grandeza in enumerate(list_grandezas):
                df_grand_monit = pd.read_csv(self.path_decks + "df_"+ grandeza + suffix_id + ".csv", sep=";", encoding="utf-8-sig", decimal=",")
                df_grand_monit = df_grand_monit[cols]
                dic_dfs_grouped[grandeza] = df_grand_monit
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: OBTER DATAFRAME DE CADA GRANDEZA RBAR")

        return dic_dfs_grouped

    def __group_rbar_by_variable(self, df_casos_sav, dic_df_rbar, make_multilevel_df = False, suffix_id=""):
        """
        Agrupa os resultados da análise RBAR por variável monitorada.

        Esta função itera sobre os DataFrames resultantes da análise RBAR e os agrupa
        por variável monitorada (por exemplo, Tensao_MOD, Geracao_MW). Os resultados
        são armazenados em um dicionário com as variáveis monitoradas como chaves.

        Parameters
        ----------
        df_casos_sav : DataFrame
            DataFrame contendo os dados dos casos SAV.
        dic_df_rbar : dict
            Dicionário contendo os resultados da análise RBAR.
        make_multilevel_df : bool, optional
            Se True, cria um DataFrame com múltiplos níveis de índice. O padrão é False.
        suffix_id : str, optional
            Identificador usado para diferenciar os arquivos de saída. O padrão é uma string vazia.

        Returns
        -------
        dic_dfs_group : dict
            Dicionário contendo os DataFrames agrupados por variável monitorada.
        """
        start_time = time.time()

        # Buscando nome das DFs
        dic_dfs_group = {}
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()

        list_cols = ["Area", "Estado", "Tipo_Barra", "Numero", "Nome_Barra"]
        var_cols = ['Tensao_MOD', 'Tensao_ANG', 'Geracao_MW', 'Geracao_Mvar', 'Carga_MW', 'Shunt_Mvar']

        # for j in range(0, len(var_cols)):
        for _, grandeza in enumerate(var_cols):
            # Grandeza Monitorada
            # grandeza = var_cols[j]
            counter = 0

            # Fazendo o loop
            for i, df_temp in enumerate(dic_df_rbar.values()):
                # Refaço minhas colunas desejadas
                list_cols_var = list_cols.copy()
                list_cols_var.append(grandeza)

                # Pegando o próximo df
                df_temp = df_temp[list_cols_var].copy()

                # Escrevendo o dataframe
                if not df_temp.empty:
                    # Pegando o próximo df

                    # Garantindo que barras desligadas sejam zeradas
                    if len(df_temp[df_temp["Estado"] != "LIG"]) > 0:
                        df_temp.loc[:,grandeza] = np.vectorize(self.__check_estado_barra)(df_temp["Estado"], df_temp[grandeza])

                    # Removendo a coluna Estado - não preciso mais dela
                    df_temp = df_temp.drop('Estado', axis=1)
                    list_cols_var.remove("Estado")

                    # Acertando o nome da grandeza
                    df_temp.rename(columns={ df_temp.columns[len(list_cols_var)-1]: list_savs[i] + "\n[" + list_num_cases[i]+ "] " + list_name_cases[i]}, inplace = True)

                    # Cria df avançado no PANDAS
                    if make_multilevel_df:
                        df_temp.columns = pd.MultiIndex.from_tuples([tuple(c.split('\n')) for c in df_temp.columns])

                    # Passando as grandezas para float
                    df_temp[df_temp.columns[len(list_cols_var)-1]] = df_temp[df_temp.columns[len(list_cols_var)-1]].astype(float)

                    # Eliminando linhas vazias
                    df_temp = df_temp.dropna(subset=[df_temp.columns[-1]])

                    # Juntando dataframes
                    if counter == 0:
                        df_grand_monit = df_temp
                        counter = 1
                    else:
                        # Colunas repetidas
                        df_grand_monit = pd.merge(df_grand_monit, df_temp[['Numero', df_temp.columns[-1]]], how='outer', left_on="Numero", right_on="Numero").drop_duplicates(subset="Numero")
                        ## Atualiza elementos em branco
                        cols_update = ['Area', 'Tipo_Barra', 'Nome_Barra']
                        index_update = 'Numero'
                        #
                        df_grand_monit.set_index(index_update, inplace=True)
                        df_temp.set_index(index_update, inplace=True)
                        df_grand_monit[cols_update] = df_grand_monit[cols_update].combine_first(df_temp[cols_update])
                        # df_grand_monit[cols_update].update(df_temp[cols_update])
                        df_grand_monit.reset_index(inplace=True)
                        df_temp.reset_index(inplace=True)

            # Preencheendo valores vazios
            # df_grand_monit = df_grand_monit.fillna(0)
            df_grand_monit.to_csv(self.path_decks + "df_" + grandeza + suffix_id + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")

            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: OBTENDO DATAFRAME PARA GRANDEZA: {grandeza}")
            start_time = time.time()

            # Armazendo DFs
            match grandeza:
                case "Tensao_MOD":
                    dic_dfs_group['Tensao_MOD'] = df_grand_monit
                case "Tensao_ANG":
                    dic_dfs_group['Tensao_ANG'] = df_grand_monit
                case "Geracao_MW":
                    dic_dfs_group['Geracao_MW'] = df_grand_monit
                case "Geracao_Mvar":
                    dic_dfs_group['Geracao_Mvar'] = df_grand_monit
                case "Carga_MW":
                    dic_dfs_group['Carga_MW'] = df_grand_monit
                case "Shunt_Mvar":
                    dic_dfs_group['Shunt_Mvar'] = df_grand_monit

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO DF/CSV GRANDEZAS")
        return dic_dfs_group

    def __check_estado_barra(self, estado, grandeza):
        """
        Verifica o estado da barra e retorna a grandeza correspondente.

        Esta função verifica se a barra está ligada ou desligada e retorna a grandeza
        correspondente. Se o estado for 'LIG', retorna a grandeza. Se for 'DES', retorna 0.

        Parameters
        ----------
        estado : str or None
            estado da barra ('LIG' para ligada, 'DES' para desligada).
        grandeza : float or None
            Valor da grandeza monitorada na barra.

        Returns
        -------
        val : float or None
            Valor da grandeza monitorada, ajustado de acordo com o estado da barra.
        """
        if pd.isnull(estado):
            val = grandeza
        elif estado[:3] == "LIG":
            val = grandeza
        elif estado[:3] == "DES":
            val = 0
        else:
            val = None
        return val

    ###================================================================================================================
    ###
    ### CÓDIGOS RELATÓRIO ANAREDE - RLIN
    ###
    ###================================================================================================================
    def __deck_rlin(self, file_out, file_end, df_casos_sav, list_barra, list_areas):
        """
        Cria o deck para a análise RLIN.

        Esta função gera o corpo do deck para a análise RLIN com base nos casos SAV fornecidos.
        O deck inclui instruções para a geração de relatórios RLIN para todas as barras,
        uma lista específica de barras, todas as áreas ou uma lista específica de áreas.

        Parameters
        ----------
        file_out : list
            Lista de arquivos de saída a serem gerados.
        file_end : list
            Lista de arquivos de fim a serem gerados.
        df_casos_sav : DataFrame
            DataFrame contendo os dados dos casos SAV.
        list_barra : list or None
            Lista de barras para análise RLIN. Se None, todas as barras serão consideradas.
        list_areas : list or None
            Lista de áreas para análise RLIN. Se None, todas as áreas serão consideradas.

        Returns
        -------
        body_list_cases : str
            Corpo formatado do deck RLIN.
        file_out : list
            Lista atualizada de arquivos de saída.
        file_end : list
            Lista atualizada de arquivos de fim.
        """
        list_paths = df_casos_sav['Diretorio_Arquivo'].tolist()
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()
        body_list_cases = []
        counter = 0
        for i, _ in enumerate(list_paths):
            # Contadores e arquivos a serem gerados
            counter = counter + 1
            file_out.append(self.path_decks + "rel_rlin_" + str(counter) + ".out")
            file_end.append(self.path_decks + "rel_rlin_" + str(counter) + ".end")
            # Corpo do Deck
            body_list_cases.append("(RELATÓRIO - ARQUIVO: " + list_savs[i] + " - " + list_num_cases[i] + "-" + list_name_cases[i])
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "rel_rlin_" + str(counter) + ".out")
            body_list_cases.append("DOPC")
            body_list_cases.append("FILE L")
            body_list_cases.append("99999")
            body_list_cases.append("ULOG")
            body_list_cases.append("2")
            body_list_cases.append(list_paths[i])
            body_list_cases.append("ARQV REST")
            body_list_cases.append(list_num_cases[i])
            body_list_cases.append("DOPC")
            body_list_cases.append("FILE L")
            body_list_cases.append("99999")

            # Diferenciação de acordo com o que se deseja estudar
            ## Caso 1 - Coletando todas barras
            if list_barra is None and list_areas is None:
                body_list_cases.append("RELA RLIN")
            ## Caso 2 - Coletando lista de barras
            elif list_barra is not None and list_areas is None:
                for j, _ in enumerate(list_barra):
                    body_list_cases.append("RELA RLIN CONV")
                    body_list_cases.append(str(list_barra[j]))
                    body_list_cases.append("99999")
            ## Caso 3 - Coletando lista de areas
            elif list_barra is None and list_areas is not None:
                for j, _ in enumerate(list_areas):
                    body_list_cases.append("RELA RLIN AREA")
                    body_list_cases.append(str(list_areas[j]))
            ## Caso 4 - Coletando lista de barras e areas
            elif list_barra is not None and list_areas is not None:
                for j, _ in enumerate(list_barra):
                    body_list_cases.append("RELA RLIN CONV")
                    body_list_cases.append(str(list_barra[j]))
                    body_list_cases.append("99999")
                for j, _ in enumerate(list_areas):
                    body_list_cases.append("RELA RLIN AREA")
                    body_list_cases.append(str(list_areas[j]))
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "rel_rlin_" + str(counter) + ".end")
            body_list_cases.append("(")
        # Adiciona seção para extrair dados de Área e Barra
        file_out.append(self.path_decks + "rel_dadb.out")
        file_end.append(self.path_decks + "rel_dadb.end")
        body_list_cases.append("(RELATÓRIO - EXTRAIR DADOS DE ÁREA")
        body_list_cases.append("ULOG")
        body_list_cases.append("4")
        body_list_cases.append(self.path_decks + "rel_dadb.out")
        body_list_cases.append("DOPC")
        body_list_cases.append("FILE L")
        body_list_cases.append("99999")
        body_list_cases.append("ULOG")
        body_list_cases.append("2")
        body_list_cases.append(list_paths[-1])
        body_list_cases.append("ARQV REST")
        body_list_cases.append(list_num_cases[-1])
        body_list_cases.append("DOPC")
        body_list_cases.append("FILE L")
        body_list_cases.append("99999")
        body_list_cases.append("RELA DADB")
        body_list_cases.append("ULOG")
        body_list_cases.append("4")
        body_list_cases.append(self.path_decks + "rel_dadb.end")
        body_list_cases.append("(")
        body_list_cases.append("FIM")
        body_list_cases = "\n".join(body_list_cases)

        return body_list_cases, file_out, file_end

    def __create_id_line(self, barra_de, barra_para, num_circ):
        """
        Cria um identificador para uma linha com base nas barras e no número do circuito.

        Parameters
        ----------
        BarraDe : str
            Identificador da barra de origem da linha.
        BarraPara : str
            Identificador da barra de destino da linha.
        NumCirc : str
            Número do circuito.

        Returns
        -------
        val : str
            Identificador da linha.
        """
        val = "_" + barra_de + "_" + barra_para + "_" + num_circ
        return val

    def __get_dfs_rlin_area(self, file_out):
        """
        Extrai os dados de linhas do arquivo de saída do ANAREDE para as linhas de área.

        Parameters
        ----------
        file_out : list of str
            Lista dos caminhos dos arquivos de saída (.OUT) do ANAREDE.

        Returns
        -------
        dic_dfs : dict
            Dicionário contendo os DataFrames de linhas de área.
        """
        dic_dfs = {}
        for i in range(0, len(file_out)-1):
            # Buscando resultados novos
            if self.roda_anarede:
                # Coletando dados do OUT - AREA
                with open(file_out[i], 'r') as file:
                    data = file.read()
                    # Filtrando o tamanho do deck
                    index = data.find(" RELATORIO COMPLETO DO SISTEMA")
                    data = data[index:]

                # Plota em um arquivo temporário, o código RBAR
                with open(self.path_decks + 'temp.txt', 'w', encoding="utf-8") as f:
                    f.write(data)

                # Define a disposição dos dados
                list_columns=['Nome_BarraDe', 'Nome_BarraPara', 'NumCirc', 'BarraPara', 'Estado', "CapacNom", "Fluxo_MW", "Fluxo_Mvar", "Fluxo_MVA_Vd", "TAP", "Defasagem", "Carregamento"]
                colspecs =   [  (2,14),        (82,94),          (95,97),   (76,81),   (14,23),    (24,31),    (98,105),    (106,113),    (114,121),  (122,126), (129,134),    (53, 59) ]

                # Leitura para um dataframe
                df = pd.read_fwf(self.path_decks + "temp.txt", skiprows=0, skipfooter=0, names=list_columns, colspecs=colspecs,  dtype=str)

                # Limpeza nos dados - Elimina dados não numéricos de numero e tipo de barra
                cols = ["CapacNom"]
                df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
                df = df[df['CapacNom'].notna()]
                # df['Nome_BarraDe'].fillna(method="ffill", inplace=True)
                # df['Nome_BarraDe'] = df['Nome_BarraDe'].fillna(method="ffill")
                df['Nome_BarraDe'] = df['Nome_BarraDe'].ffill()
                df = df[df['Nome_BarraPara'].notna()]

                # Limpar colunas com barras desligadas
                df = df[df["Estado"] != "DES"]

                # Ajeita a coluna com carregamento percentual, retirando o simbolo %
                df['Carregamento'] = df['Carregamento'].str[:-1]

                # Adequa colunas para float
                list_columns = ["CapacNom", "Fluxo_MW", "Fluxo_Mvar", "Fluxo_MVA_Vd", "TAP", "Defasagem", "Carregamento"]
                df[list_columns] = df[list_columns].astype(float)

                # Adiciona informação de Barra De faltante
                # time_x = time.time()
                start_block = ["DA BARRA", "NOME ", "---", "...", "NS -", "     ", "NUM. ", "PEL - "]
                start_block = tuple(start_block)  # Convert list to tuple for faster access
                list_data_red = []
                for element in data.splitlines():
                    sliced_element = element[2:44]
                    if sliced_element.strip() and not sliced_element.startswith(start_block):
                        list_data_red.append(sliced_element)
                nomes_barras = pd.concat([df['Nome_BarraDe'], df['Nome_BarraPara']]).unique().tolist()
                # print(f"{time.time() - time_x} cria lista reduzida")

                # time_x = time.time()
                nomes_barras_set = set(nomes_barras)  # Convert list to set for faster access
                list_dados_barra = []
                area = None  # Initialize area
                for index, value in enumerate(list_data_red):
                    if value.startswith("ELATORIO COMPLETO DO SISTEMA *"):
                        area = value[35:40].strip()
                    elif value[:12].strip() in nomes_barras_set:
                        dic_dados_barra= {}
                        dic_dados_barra["NomeBarra"] = value[:12].strip()
                        data_temp = list_data_red[index-1].split()
                        dic_dados_barra["Barra"] = data_temp[0]
                        dic_dados_barra["Tensao"] = data_temp[1]
                        dic_dados_barra["Area"] = area
                        list_dados_barra.append(dic_dados_barra)
                df_dados_barra = pd.DataFrame(list_dados_barra)
                # print(f"{time.time() - time_x} cria df")

                # time_x = time.time()
                # Complementa Barra Para
                df_dados_para = df_dados_barra.rename({'Barra': 'BarraPara','Area': 'Area_BarraPara', 'Tensao': 'Tensao_BarraPara'}, axis=1)
                df_para = df.merge(df_dados_para[['BarraPara', 'Area_BarraPara', 'Tensao_BarraPara']], on='BarraPara', how='left')

                # Complementa Barra De
                df_dados_de = df_dados_barra.rename({'Barra': 'BarraDe','Area': 'Area_BarraDe', 'Tensao': 'Tensao_BarraDe', 'NomeBarra':'Nome_BarraDe'}, axis=1)
                df_de_para = df_para.merge(df_dados_de[['BarraDe', 'Area_BarraDe', 'Tensao_BarraDe', 'Nome_BarraDe']], on='Nome_BarraDe', how='left')

                # Acerta colunas
                df_de_para.loc[:,'ID'] = np.vectorize(self.__create_id_line)(df_de_para["BarraDe"], df_de_para["BarraPara"],df_de_para["NumCirc"])
                cols = list(df_de_para.columns)
                # items to be removed
                unwanted_cols = ['ID', 'Area_BarraDe', 'Area_BarraPara', 'Tensao_BarraDe', 'Tensao_BarraPara', 'BarraDe', 'BarraPara', 'Nome_BarraDe', 'Nome_BarraPara', 'NumCirc']
                cols = [ele for ele in cols if ele not in unwanted_cols]
                cols = unwanted_cols + cols
                df_de_para = df_de_para[cols]

                # print(f"{time.time() - time_x} acerta df")

                # Imprimindo DataFrame-CSV
                df_de_para.to_csv(self.path_decks + "df_OUT_RLIN_AREA_" + str(i+1) + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")

            # Buscando resultados existentes
            else:
                try:
                    df_de_para = pd.read_csv(self.path_decks + "df_OUT_RLIN_AREA_" + str(i+1) + ".csv", sep=";", encoding="utf-8-sig", decimal=",")
                except: # pylint: disable=bare-except
                    print("ERRO FATAL! Não foi possível localizar o df do RLIN em CSV...rodar ANAREDE novamente!")
                    sys.exit()

            # Salva DF na pilha
            dic_dfs[(i)] = df_de_para

        return dic_dfs

    def __get_dfs_rlin(self, file_out, list_barra, list_areas):
        """
        Extrai os DataFrames das linhas de RLIN de acordo com as barras ou áreas especificadas.

        Parameters
        ----------
        file_out : list of str
            Lista dos caminhos dos arquivos de saída (.OUT) do ANAREDE.
        list_barra : list or None
            Lista das barras para as quais deseja-se extrair os dados. Se None, todas as barras são consideradas.
        list_areas : list or None
            Lista das áreas para as quais deseja-se extrair os dados. Se None, todas as áreas são consideradas.

        Returns
        -------
        dic_dfs : dict
            Dicionário contendo os DataFrames das linhas de RLIN.
        """
        if list_barra is not None and list_areas is not None:
            dic_dfs_area = self.__get_dfs_rlin_area(file_out)
            # dic_dfs_BARRA = self.__get_dfs_rlin_BARRA(file_out)
            # dic_dfs = dic_dfs_area + dic_dfs_BARRA
        elif list_barra is not None:
            # dic_dfs_BARRA = self.__get_dfs_rlin_BARRA(file_out)
            # dic_dfs =
            pass
        elif list_areas is not None:
            dic_dfs_area = self.__get_dfs_rlin_area(file_out)
            dic_dfs = dic_dfs_area
        elif list_barra is None and list_areas is None:
            dic_dfs_area = self.__get_dfs_rlin_area(file_out)
            dic_dfs = dic_dfs_area

        return dic_dfs

    def __get_rlin(self, df_casos_sav, list_barra = None, list_areas = None, make_multilevel_df = False, suffix_id=""):
        """
        Obtém os DataFrames das linhas de RLIN de acordo com as barras ou áreas especificadas.

        Parameters
        ----------
        df_casos_sav : DataFrame
            DataFrame contendo os casos SAV.
        list_barra : list or None, optional
            Lista das barras para as quais deseja-se extrair os dados. Se None, todas as barras são consideradas. Default é None.
        list_areas : list or None, optional
            Lista das áreas para as quais deseja-se extrair os dados. Se None, todas as áreas são consideradas. Default é None.
        make_multilevel_df : bool, optional
            Indica se os DataFrames resultantes devem ser multilevel. Default é False.
        suffix_id : str, optional
            Identificação adicional para os DataFrames. Default é uma string vazia.

        Returns
        -------
        dic_dfs_grouped : dict
            Dicionário contendo os DataFrames das linhas de RLIN agrupados por grandeza monitorada.
        """
        # Checando se dicionário com exceções chegou
        start_time = time.time()

        # Verifica necessidade de rodar ANAREDE novamente
        if self.roda_anarede:
            file_end = []
            file_out = []
            body_list_cases, file_out, file_end = self.__deck_rlin(file_out, file_end, df_casos_sav, list_barra, list_areas)

            # Escrevendo deck
            deck_rlin = self.path_decks + "deck_rlin.pwf"
            with open(deck_rlin, "w", encoding='utf-8') as text_file:
                text_file.write(body_list_cases)
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CRIAÇÃO DOS DECKS ANAREDE")
            start_time = time.time()

            # Elaborando comando
            comando = self.engine + " " + '"' + deck_rlin + '"' + " " + '"' + file_end[0] + '"'

            # Executa ANAREDE
            self._exe_command_anarede(comando, file_end)
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO ANAREDE: CRIAÇÃO DOS RELATÓRIOS .OUT E .END")
            start_time = time.time()

            # Coletar dicionários com a lista de casos
            dic_dfs = self.__get_dfs_rlin(file_out, list_barra, list_areas)
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CONVERSÃO RELATÓRIO .OUT PARA DATAFRAME")

            dic_dfs_grouped = self.__group_rlin_by_variable(df_casos_sav, dic_dfs, make_multilevel_df, suffix_id)

        else:
            list_grandezas = ['CapacNom', 'Fluxo_MW', 'Fluxo_Mvar', 'Fluxo_MVA_Vd', 'TAP', 'Defasagem', 'Carregamento']
            dic_dfs_grouped = {}
            columns_base = ['ID', 'Area_BarraDe', 'Area_BarraPara', 'Tensao_BarraDe','Tensao_BarraPara', 'BarraDe', 'BarraPara', 'Nome_BarraDe',
                            'Nome_BarraPara', 'NumCirc',]
            columns_filter = []
            # Iterando sobre as linhas do DataFrame
            for _, row in df_casos_sav.iterrows():
                element = str(row["Nome_Arquivo"]) + "\n[" + str(row["Numero_Caso"]) + "] " + str(row["Nome_Caso"])
                columns_filter.append(element)
            cols = columns_base + columns_filter

            for _, grandeza in enumerate(list_grandezas):
                df_grand_monit = pd.read_csv(self.path_decks + "df_"+ grandeza + suffix_id + ".csv", sep=";", encoding="utf-8-sig", decimal=",")
                df_grand_monit = df_grand_monit[cols]
                dic_dfs_grouped[grandeza] = df_grand_monit
            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: OBTER DATAFRAME DE CADA GRANDEZA RLIN")

        return dic_dfs_grouped

    def __group_rlin_by_variable(self, df_casos_sav, dic_df_rlin, make_multilevel_df = False, suffix_id=""):
        """
        Agrupa os DataFrames das linhas de RLIN de acordo com as variáveis monitoradas.

        Parameters
        ----------
        df_casos_sav : DataFrame
            DataFrame contendo os casos SAV.
        dic_df_rlin : dict
            Dicionário contendo os DataFrames das linhas de RLIN.
        make_multilevel_df : bool, optional
            Indica se os DataFrames resultantes devem ser multilevel. O padrão é False.
        suffix_id : str, optional
            Identificação adicional para os DataFrames. O padrão é uma string vazia.

        Returns
        -------
        dic_dfs_group : dict
            Dicionário contendo os DataFrames das linhas de RLIN agrupados por grandeza monitorada.
        """
        start_time = time.time()

        # Buscando nome das DFs
        dic_dfs_group = {}
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()

        list_cols = ['ID', 'Area_BarraDe','Area_BarraPara','Tensao_BarraDe','Tensao_BarraPara','BarraDe','BarraPara','Nome_BarraDe','Nome_BarraPara','NumCirc', 'Estado']
        var_cols = ['CapacNom', 'Fluxo_MW', 'Fluxo_Mvar', 'Fluxo_MVA_Vd', 'TAP', 'Defasagem', 'Carregamento']

        for j, _ in enumerate(var_cols):
            # Grandeza Monitorada
            grandeza = var_cols[j]
            counter = 0

            # Fazendo o loop
            for i, df_temp in enumerate(dic_df_rlin.values()):
                # Refaço minhas colunas desejadas
                list_cols_var = list_cols.copy()
                list_cols_var.append(grandeza)

                # Pegando o próximo df
                df_temp = df_temp[list_cols_var].copy()

                # Escrevendo o dataframe
                if not df_temp.empty:
                    # Eliminando elementos desligados
                    df_temp = df_temp[df_temp["Estado"] != "DESLIGADO"]

                    # Removendo a coluna Estado - não preciso mais dela
                    df_temp = df_temp.drop('Estado', axis=1)
                    list_cols_var.remove("Estado")

                    # Acertando o nome da grandeza
                    df_temp.rename(columns={ df_temp.columns[len(list_cols_var)-1]: list_savs[i] + "\n[" + list_num_cases[i]+ "] " + list_name_cases[i]}, inplace = True)

                    # Cria df avançado no PANDAS
                    if make_multilevel_df:
                        df_temp.columns = pd.MultiIndex.from_tuples([tuple(c.split('\n')) for c in df_temp.columns])

                    # Passando as grandezas para float
                    df_temp[df_temp.columns[len(list_cols_var)-1]] = df_temp[df_temp.columns[len(list_cols_var)-1]].astype(float)

                    # Eliminando linhas vazias
                    df_temp = df_temp.dropna(subset=[df_temp.columns[-1]])

                    # Juntando dataframes
                    if counter == 0:
                        df_grand_monit = df_temp
                        counter = 1
                    else:
                        # Colunas repetidas
                        df_grand_monit = pd.merge(df_grand_monit, df_temp[['ID', df_temp.columns[-1]]], how='outer', left_on="ID", right_on="ID").drop_duplicates(subset="ID")
                        ## Atualiza elementos em branco
                        cols_update = ['Area_BarraDe', 'Area_BarraPara', 'Tensao_BarraDe', 'Tensao_BarraPara', 'BarraDe', 'BarraPara', 'NumCirc','Nome_BarraDe','Nome_BarraPara']
                        index_update = 'ID'
                        #
                        df_grand_monit.set_index(index_update, inplace=True)
                        df_temp.set_index(index_update, inplace=True)
                        df_temp = df_temp.loc[~df_temp.index.duplicated(keep='first')]
                        df_grand_monit[cols_update] = df_grand_monit[cols_update].combine_first(df_temp[cols_update])
                        # df_grand_monit[cols_update].update(df_temp[cols_update])
                        df_grand_monit.reset_index(inplace=True)
                        df_temp.reset_index(inplace=True)

                        if len(df_grand_monit[df_grand_monit["Nome_BarraDe"].str.len() < 2]) > 0:
                            pass

                        # keys = ['ID', 'Area_BarraDe', 'Area_BarraPara', 'Tensao_BarraDe', 'Tensao_BarraPara', 'BarraDe', 'BarraPara', 'NumCirc']
                        # cols_join = list(df_temp.columns)
                        # cols_join = [x for x in cols_join if x not in ["Nome_BarraDe", "Nome_BarraPara"]]
                        # df_grand_monit = pd.merge(df_grand_monit, df_temp[cols_join], how='outer', left_on=keys, right_on=keys)

            # Preencheendo valores vazios
            # df_grand_monit = df_grand_monit.fillna(0)

            # Inserindo dados de Área
            df_grand_monit.to_csv(self.path_decks + "df_" + grandeza + suffix_id + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")

            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: OBTENDO DATAFRAME PARA GRANDEZA: {grandeza}")
            start_time = time.time()

            # Armazendo DFs
            match grandeza:
                case "CapacNom":
                    dic_dfs_group['CapacNom'] = df_grand_monit
                case "Fluxo_MW":
                    dic_dfs_group['Fluxo_MW'] = df_grand_monit
                case "Fluxo_Mvar":
                    dic_dfs_group['Fluxo_Mvar'] = df_grand_monit
                case "Fluxo_MVA_Vd":
                    dic_dfs_group['Fluxo_MVA_Vd'] = df_grand_monit
                case "TAP":
                    dic_dfs_group['TAP'] = df_grand_monit
                case "Defasagem":
                    dic_dfs_group['Defasagem'] = df_grand_monit
                case "Carregamento":
                    dic_dfs_group['Carregamento'] = df_grand_monit

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO DF/CSV GRANDEZAS")
        return dic_dfs_group

    ###================================================================================================================
    ###
    ### CÓDIGOS RELATÓRIO ANAREDE - RLIN + RBAR
    ###
    ###================================================================================================================
    def __deck_fragmenta(self, file_out, file_end, df_casos_sav):
        """
        """
        list_paths = df_casos_sav['Diretorio_Arquivo'].tolist()
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()
        body_list_cases = []
        counter = 0
        for i, _ in enumerate(list_paths):
            # Contadores e arquivos a serem gerados
            counter = counter + 1
            file_out.append(self.path_decks + "pwf_" + str(counter) + "-" + list_name_cases[i] + ".pwf")
            file_end.append(self.path_decks + "pwf_" + str(counter) + "-" + list_name_cases[i] + ".end")
            # Corpo do Deck
            body_list_cases.append("(ARQUIVO FRAGMENTAÇÃO .SAV EM .PWF: " + list_savs[i] + " - " + list_num_cases[i] + "-" + list_name_cases[i])
            body_list_cases.append("ULOG")
            body_list_cases.append("2")
            body_list_cases.append(list_paths[i])
            body_list_cases.append("ARQV REST")
            body_list_cases.append(list_num_cases[i])
            body_list_cases.append("ULOG")
            body_list_cases.append("7")
            body_list_cases.append(self.path_decks + "pwf_" + str(counter) + "-" + list_name_cases[i] + ".pwf")
            body_list_cases.append("CART")
            body_list_cases.append("ULOG")
            body_list_cases.append("4")
            body_list_cases.append(self.path_decks + "pwf_" + str(counter) + "-" + list_name_cases[i] + ".end")
            body_list_cases.append("(")
        # Adiciona seção para extrair dados de Área e Barra
        body_list_cases.append("FIM")
        body_list_cases = "\n".join(body_list_cases)

        return body_list_cases, file_out, file_end
    ###================================================================================================================
    ###
    ### CÓDIGOS MANIPULAÇÃO DATAFRAME PARA RECOMPOSIÇÃO
    ###
    ###================================================================================================================
    def __auxdf_adjustcoordinates(self, tensao,coordinate,name):
        """
        Ajusta as coordenadas com base na tensão.

        Parameters
        ----------
        tensao : str
            O valor da tensão.
        coordinate : str
            O valor da coordenada.
        name : str
            O nome da coordenada.

        Returns
        -------
        adjusted_coordinate : str or None
            A coordenada ajustada ou None se a tensão for '-' ou se o nome for 'Limite_inferior' ou 'Limite_superior'.
        """
        if str(tensao) == "-":
            return None
        elif name == "Limite_inferior" or name == "Limite_superior":
            return None
        else:
            return coordinate

    def __melt_df(self, df):
        """
        Funde as colunas da DataFrame em uma única coluna de valores com base nos IDs das barras.

        Parameters
        ----------
        df : pandas.DataFrame
            O DataFrame a ser derretido.

        Returns
        -------
        df_melted : pandas.DataFrame
            O DataFrame derretido.
        """
        # Limpando barras ficticias
        bool_comp = df.Nome_Barra.str.endswith("000")
        df = df[~bool_comp]
        #
        list_columns = list(df.columns[:3])
        numeric_names = [*range(1,1+len(list(df.columns[3:])))]
        list_columns = list_columns + numeric_names
        df.columns = list_columns
        #
        # Adicionando limite inferior
        new_data = pd.DataFrame(df[-1:].values, columns=df.columns)
        for col in (new_data.columns)[3:]:
            new_data[col].values[:] = 0.90
        new_data["Nome_Barra"][0] = "Limite_inferior"
        # new_data["Area"][0] = "-"
        # new_data["Numero"][0] = "001"
        df = pd.concat([df,new_data])
        # Adicionando limite superior
        new_data = pd.DataFrame(df[-1:].values, columns=df.columns)
        for col in (new_data.columns)[3:]:
            new_data[col].values[:] = 1.050
        new_data["Nome_Barra"][0] = "Limite_superior"
        # new_data["Area"][0] = "-"
        # new_data["Numero"][0] = "002"
        df = pd.concat([df,new_data])
        #
        df_melted = df.melt(id_vars=["Area", "Numero", "Nome_Barra"])
        df_melted = df_melted.rename(columns={"variable": "passo", "value": "tensao"})

        return df_melted

    def __get_coordinates(self, df_melted):
        """
        Obtém as coordenadas de latitude e longitude para as barras no DataFrame derretido e ajusta essas coordenadas com base na tensão.

        Parameters
        ----------
        df_melted : pandas.DataFrame
            O DataFrame derretido contendo as informações de tensão.

        Returns
        -------
        df_melted_coordinates : pandas.DataFrame
            O DataFrame contendo as coordenadas ajustadas com base na tensão.
        """
        path_csv_coordinates = self.path_decks[:(self.path_decks)[:-1].rindex("\\")+1]
        path_csv_coordinates = str(easygui.fileopenbox(default=path_csv_coordinates + "*.csv", title="Selecionar as informações de coordenadas", multiple=False))
        #
        df_coordinates = pd.read_csv(path_csv_coordinates, sep=";", decimal=",", encoding='utf-8-sig')
        list_columns = ["Numero", "longitude", "latitude"]  #list(df_coordinates.columns)[1:]
        df_coordinates = df_coordinates[list_columns]
        #
        df_melted_coordinates = pd.merge(df_melted, df_coordinates)
        #
        df_melted_coordinates["latitude_mod"] = np.vectorize(self.__auxdf_adjustcoordinates)(df_melted_coordinates["tensao"], df_melted_coordinates["latitude"], df_melted_coordinates["Nome_Barra"])
        df_melted_coordinates["longitude_mod"] = np.vectorize(self.__auxdf_adjustcoordinates)(df_melted_coordinates["tensao"], df_melted_coordinates["longitude"], df_melted_coordinates["Nome_Barra"])

        all_data_diffq = (1.05 - 0.9) / 20
        df_melted_coordinates = df_melted_coordinates.replace("-", np.nan)
        df_melted_coordinates["marker_siz"] = (df_melted_coordinates["tensao"] - df_melted_coordinates["tensao"].min()) / all_data_diffq + 1

        return df_melted_coordinates

    def _ask_coordinates(self, df):
        """
        Pede as coordenadas de latitude e longitude para cada barra no DataFrame e as salva em um arquivo CSV.

        Parameters
        ----------
        df : pandas.DataFrame
            O DataFrame contendo as informações das barras.

        Returns
        -------
        None
        """
        # Passando informações de latitude e longitude
        df_coordinates = df[["Numero", "Nome_Barra"]]
        df_coordinates["latitude"] = np.nan
        df_coordinates["longitude"] = np.nan
        #
        path_csv_coordinates = self.path_decks[:(self.path_decks)[:-1].rindex("\\")+1] + "bus_coordinates.csv"
        # Verifica se o arquivo existe - para evitar sobrescrever um existente
        if os.path.isfile(path_csv_coordinates):
            message = "Foi identificado um arquivo .CSV de coordenadas existente na pasta! Você deseja sobrescrever o arquivo, apagando seu conteúdo?"
            title = "Salvar arquivo .CSV para preenchimento das coordenadas"
            output = easygui.ynbox(message, title)
            if output:
                df_coordinates.to_csv(path_csv_coordinates, sep=";", decimal=",", encoding='utf-8-sig')
        else:
            df_coordinates.to_csv(path_csv_coordinates, sep=";", decimal=",", encoding='utf-8-sig')

    def _associate_coordinates(self, df):
        """
        Associa coordenadas de latitude e longitude às barras no DataFrame e exporta para um arquivo CSV.

        Parameters
        ----------
        df : pandas.DataFrame
            O DataFrame contendo as informações das barras.

        Returns
        -------
        pandas.DataFrame
            O DataFrame com as coordenadas associadas às barras.
        """
        # Derretendo o dataframe informado
        df_melted = self.__melt_df(df)

        # Inserindo informações de coordenadas no df
        df_melted_coordinates = self.__get_coordinates(df_melted)

        # Exportando para pasta padrão
        path_csv_coordinates = self.path_decks + "df_coordinates.csv"
        df_melted_coordinates.to_csv(path_csv_coordinates, sep=";", decimal=",", encoding='utf-8-sig')


        return df_melted_coordinates

    def _plot_df_tensao_melted_coordinates(self, df):
        """
        Plota um gráfico de dispersão de latitudes e longitudes com cores representando a tensão das barras.

        Parameters
        ----------
        df : pandas.DataFrame
            O DataFrame contendo as informações das barras com coordenadas associadas.

        Returns
        -------
        plotly.graph_objs._figure.Figure
            O objeto figura contendo o gráfico plotado.
        """
        fig = px.scatter_mapbox(df, lat='latitude_mod', lon='longitude_mod', color='tensao', hover_name  = 'Nome_Barra',
                            hover_data=["Nome_Barra", "tensao"], animation_frame = 'passo', mapbox_style="open-street-map",
                            zoom=5, color_continuous_scale = px.colors.sequential.Bluered, opacity = 0.66, width= 1366, height=600)
        #size="marker_siz"
        fig.update_traces(marker={'size': 25})
        fig.update_traces(cluster=dict(enabled=True))
        # fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 150
        # fig.update_traces(mode = "markers+lines")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, mapbox=dict(pitch=0,bearing=0))

        return fig

    def __adjust_df_tensao_to_plot(self, df):
        """
        Ajusta o DataFrame de tensões para plotagem.

        Parameters
        ----------
        df : pandas.DataFrame
            O DataFrame contendo as informações das tensões das barras.

        Returns
        -------
        pandas.DataFrame
            O DataFrame ajustado para plotagem.
        int
            O número de linhas para a plotagem.
        int
            O número de colunas para a plotagem.
        """
        # Limpando barras ficticias
        bool_comp = df.Nome_Barra.str.endswith("000")
        df = df[~bool_comp]
        df = df.drop('Tipo_Barra', axis=1)
        # Realizando a transposição do dataframe original
        df_tensao_t = df.iloc[:, 2:].T
        df_tensao_t.columns = df_tensao_t.iloc[0]
        df_tensao_t = df_tensao_t[1:]
        # df_tensao_t = df_tensao_t.iloc[:,:-2]
        df_tensao_t = df_tensao_t.reset_index(drop=True)
        df_tensao_t = df_tensao_t.rename_axis(None, axis=1)
        df_tensao_t['passo'] = range(1,len(df_tensao_t)+1)
        df_tensao_t['passo'] = df_tensao_t['passo'].astype(int)
        list_columns = ["passo"] + list(df_tensao_t.columns[:-1])
        df_tensao_t = df_tensao_t[list_columns]
        df_tensao_t = df_tensao_t.replace("-", np.nan)

        # Dimensões da plotagem
        # if df_tensao_t.shape[1] <= 3:
        #     number_cols = 1
        #     number_rows = df_tensao_t.shape[1]
        # else:
        #     number_cols = (df_tensao_t.shape[1] // 3) + 1
        #     number_rows = (df_tensao_t.shape[1] // number_cols) + 1

        return df_tensao_t

    def __adjust_df_potencia_to_plot(self, df):
        """
        Ajusta o DataFrame de potências para plotagem.

        Parameters
        ----------
        df : pandas.DataFrame
            O DataFrame contendo as informações das potências das barras.

        Returns
        -------
        pandas.DataFrame
            O DataFrame ajustado para plotagem.
        int
            O número de linhas para a plotagem.
        int
            O número de colunas para a plotagem.
        """
        # Limpando barras ficticias
        # bool_comp = (df.Nome_BarraDe.str.endswith("000")) | (df.Nome_BarraPara.str.endswith("000"))
        # df = df[~bool_comp]
        df["EQP"] = df['Nome_BarraDe'] + '-' + df['Nome_BarraPara'] + ' C' + df['NumCirc'].astype(str)
        df = df.drop(['ID', 'Area_BarraDe', 'Area_BarraPara', 'Tensao_BarraDe','Tensao_BarraPara', 'BarraDe', 'BarraPara', 'Nome_BarraDe','Nome_BarraPara', 'NumCirc'], axis=1)
        specific_column = df.pop('EQP')  # Remove the column
        df.insert(0, 'EQP', specific_column)
        # Realizando a transposição do dataframe original
        df_tensao_t = df.iloc[:, :].T
        df_tensao_t.columns = df_tensao_t.iloc[0]
        df_tensao_t = df_tensao_t[1:]
        # df_tensao_t = df_tensao_t.iloc[:,:-2]
        df_tensao_t = df_tensao_t.reset_index(drop=True)
        df_tensao_t = df_tensao_t.rename_axis(None, axis=1)
        df_tensao_t['passo'] = range(1,len(df_tensao_t)+1)
        df_tensao_t['passo'] = df_tensao_t['passo'].astype(int)
        list_columns = ["passo"] + list(df_tensao_t.columns[:-1])
        df_tensao_t = df_tensao_t[list_columns]
        df_tensao_t = df_tensao_t.replace("-", np.nan)

        # # Dimensões da plotagem
        # if df_tensao_t.shape[1] <= 3:
        #     number_cols = 1
        #     number_rows = df_tensao_t.shape[1]
        # else:
        #     number_cols = (df_tensao_t.shape[1] // 3) + 1
        #     number_rows = (df_tensao_t.shape[1] // number_cols) + 1

        return df_tensao_t

    ###================================================================================================================
    ###
    ### CÓDIGOS MANIPULAÇÃO TABELADOR E COMPARADOR DE GRANDEZAS - BARRA
    ###
    ###================================================================================================================

    def __auxdf_pu_evol(self, value_old,value_new, type_var = "pu"):
        """
        Calcula a evolução em valores por unidade entre dois valores.

        Parameters
        ----------
        value_old : float
            O valor antigo.
        value_new : float
            O novo valor.

        Returns
        -------
        float
            A evolução em valores por unidade entre os dois valores.
        """
        if type_var == "pu":
            if str(value_old) != "-" and str(value_new) != "-":
                return value_new-value_old
            else:
                return np.nan
        else:
            if str(value_old) != "-" and str(value_new) != "-" and value_old != 0:
                return round(100*((value_new-value_old)/value_old),3)
            else:
                return np.nan

    def __getdfevol(self, df, reference_case):
        """
        Calcula a evolução de cada variável em relação a um caso de referência.

        Parameters
        ----------
        df : DataFrame
            O DataFrame contendo os valores das variáveis.
        reference_case : int
            O índice do caso de referência.

        Returns
        -------
        DataFrame
            O DataFrame contendo a evolução de cada variável em relação ao caso de referência.
        """
        fixed_columns=['Area', 'Numero', 'Nome_Barra']
        df_evol = df[fixed_columns]

        for i in range(3,len(df.columns)):
            col_referencia = df.columns[reference_case]
            col_novovalor = df.columns[i]
            col_evol = "evol_" + df.columns[i]

            df_temp = df[[col_referencia, col_novovalor]].copy()
            df_temp[col_evol] = np.vectorize(self.__auxdf_pu_evol)(df[col_referencia], df[col_novovalor])
            df_temp.columns = ["A","B", col_evol]
            df_temp = df_temp.rename(columns={"A": "ref_" + col_referencia, "B": "comp_" + col_novovalor})

            if i > 3:
                df_temp = df_temp.iloc[:,1:]
            df_evol = pd.merge(df_evol, df_temp, left_index=True, right_index=True)

        return df_evol

    def __complementdfevol(self, df_comp, grandeza):
        """
        Completa o DataFrame de evolução com análises adicionais.

        Parameters
        ----------
        df_comp : DataFrame
            O DataFrame contendo os dados de evolução.
        grandeza : str
            O nome da grandeza analisada.

        Returns
        -------
        DataFrame
            O DataFrame complementado com análises adicionais.
        """
        list_columns = list(df_comp.columns)
        list_cols_evol = []
        list_cols_values = []

        # Arruma dataframe
        df_comp = df_comp.replace("-", np.nan)
        df_comp[list_columns[3:]] = df_comp[list_columns[3:]].astype(float)

        for i in range(5,len(list_columns)+1,2):
            list_cols_evol.append(list_columns[i])

        for i in range(4,len(list_columns),2):
            list_cols_values.append(list_columns[i])

        df_evolutions = df_comp[list_cols_evol]
        df_values = df_comp[list_cols_values]

        series_max_evol = pd.Series(df_evolutions.max(axis='columns', skipna = True, numeric_only = True), name= "Maior_evol")
        series_min_evol = pd.Series(df_evolutions.min(axis='columns', skipna = True, numeric_only = True), name= "Menor_evol")
        series_max_evol_abs = pd.Series(df_evolutions.abs().max(axis='columns', skipna = True, numeric_only = True), name= "Maior_evol_abs")
        series_max_val = pd.Series(df_values.max(axis='columns'), name= "Maior_valor")
        series_min_val = pd.Series(df_values.min(axis='columns'), name= "Menor_valor")

        df_analysis = pd.concat([series_max_evol,series_min_evol,series_max_evol_abs, series_max_val, series_min_val],axis=1)
        df_result = pd.merge(df_comp, df_analysis, left_index=True, right_index=True)
        df_result.to_csv(self.path_decks + grandeza + "_comparador.csv", sep=";", decimal=",", encoding='utf-8-sig')

        return df_result

    def __ask_reference_case(self, df_casos_sav):
        """
        Pergunta ao usuário qual caso deseja selecionar como referência.

        Parameters
        ----------
        df_casos_sav : DataFrame
            O DataFrame contendo os casos disponíveis.

        Returns
        -------
        int
            O número do caso selecionado como referência.
        """
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()

        list_cases = []
        print("\nLista de casos disponíveis para escolha de referência:")
        for i, _ in enumerate(list_savs):
            option = f"[{i}]. {list_savs[i]} - {list_num_cases[i]}-{list_name_cases[i]}"
            list_cases.append(option)
            print(option)

        print("Informar o número [x] do caso que deseja selecionar como referência:")
        user_casos = int(input()) + 3

        return user_casos

    def _compare_single_reference_case_bus(self, df_casos_sav, list_df, grand_monit):
        """
        Compara um único caso de referência com outros casos para análise de grandezas em barras.

        Parameters
        ----------
        df_casos_sav : DataFrame
            O DataFrame contendo os casos disponíveis.
        list_df : list
            Uma lista de DataFrames contendo os dados a serem comparados.
        grand_monit : list
            Uma lista de strings contendo as grandezas monitoradas.

        Returns
        -------
        list
            Uma lista de DataFrames com os resultados da comparação.
        """
        # Coleta o caso referência
        reference_case = self.__ask_reference_case(df_casos_sav)
        start_time = time.time()

        # Inicia o loop
        list_df_compara = []
        for i, _ in enumerate(list_df):
            #  Obtém o dataframe no formato comparador
            df_comp = self.__getdfevol(list_df[i], reference_case)
            #
            # Adiciona grandezas estatísticas para comparação
            df_result = self.__complementdfevol(df_comp, grand_monit[i])

            # Salva resultado
            list_df_compara.append(df_result)

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - TABELANDO COMPARADOR GRANDEZAS BARRA")
        # Retorna a lista de dataframes
        return list_df_compara

    ###================================================================================================================
    ###
    ### CÓDIGOS MANIPULAÇÃO COMPARAÇÃO ANTES E DEPOIS DO RBAR E RLIN
    ###
    ###================================================================================================================
    def __adjust_df_python(self, dic_df, index_df, cols_inic):
        """
        Ajusta os DataFrames de um dicionário, definindo um novo índice e removendo colunas iniciais.

        Parameters
        ----------
        dic_df : dict
            Um dicionário contendo DataFrames a serem ajustados.
        index_df : str or list
            O novo índice ou lista de colunas a serem definidas como índice nos DataFrames ajustados.
        cols_inic : list
            Uma lista de colunas iniciais a serem removidas dos DataFrames.

        Returns
        -------
        dict
            Um novo dicionário contendo os DataFrames ajustados.
        """
        dic_df_adj = {}
        for _, (key, df) in enumerate(dic_df.items()):
            df = df.set_index(index_df)
            df = df.drop(columns=cols_inic)
            df = df.astype(float)

            dic_df_adj[key] = df

        return dic_df_adj

    def __get_df_delta(self, df_antes, df_depois, delta_minimo=0.005):
        """
        Calcula a diferença entre dois DataFrames e estatísticas para cada linha.

        Parameters
        ----------
        df_antes : pandas.DataFrame
            O DataFrame "antes" para comparação.
        df_depois : pandas.DataFrame
            O DataFrame "depois" para comparação.
        delta_minimo : float, optional
            O valor mínimo considerado para diferença, por padrão 0.005.

        Returns
        -------
        pandas.DataFrame, pandas.DataFrame
            O DataFrame contendo as diferenças filtradas e o DataFrame com as estatísticas para cada linha.
        """
        df_antes = df_antes.sort_index()
        df_depois = df_depois.sort_index()
        # Acerta df_antes para operação
        df_antes.columns = df_depois.columns
        df_antes = df_antes.reindex(df_depois.index, fill_value=0)
        df_antes = df_antes.fillna(0)
        #
        df_diferenca = df_depois - df_antes
        df_diferenca_filtrado = df_diferenca[(df_diferenca.abs() > delta_minimo).any(axis=1)]

        # Calcular as estatísticas para cada linha
        df_sts = df_diferenca_filtrado.apply(lambda x: pd.Series({
            'max': x.max(),
            'min': x.min(),
            'abs_max': x.abs().max(),
            'media': x.mean(),
            'desvio_padrao': x.std(),
            'mediana': x.median(),
            'Q1': x.quantile(0.25),
            'Q3': x.quantile(0.75),
            'contagem_acima_limiar': (x > delta_minimo).sum(),
            'contagem_abaixo_limiar': (x < -delta_minimo).sum()
        }), axis=1)

        return df_diferenca_filtrado, df_sts

    def __complement_df_sts(self, df_original, df, df_index, cols_inic):
        """
        Complementa o DataFrame de estatísticas com as colunas do DataFrame original.

        Parameters
        ----------
        df_original : pandas.DataFrame
            O DataFrame original contendo as colunas a serem complementadas.
        df : pandas.DataFrame
            O DataFrame de estatísticas para complementar.
        df_index : list
            A lista de colunas a serem usadas como índice para a junção.
        cols_inic : list
            A lista de colunas iniciais que devem ser mantidas.

        Returns
        -------
        pandas.DataFrame
            O DataFrame de estatísticas complementado com as colunas do DataFrame original.
        """
        # Acerta colunas detalhadas
        df_original = df_original.set_index(df_index)
        df_original = df_original[cols_inic]

        df = df.merge(df_original, on=df_index, how='left')

        # Acerta colunas df delta
        cols = df.columns
        cols = [ele for ele in cols if ele not in cols_inic]
        cols = cols_inic + cols
        df = df[cols]

        return df

    ###================================================================================================================
    ###
    ### FUNÇÕES EXTERNALIZADAS PARA USO DA API
    ###
    ###================================================================================================================
    def get_casos_sav(self, list_cases_user, suffix_id=""):
        """
        Obtém os casos SAV.

        Esta função recebe uma lista de casos do usuário, converte todos os casos para maiúsculas,
        verifica se há espaços em branco no diretório e, se necessário, inicializa a pasta TEMP.
        Por fim, inicializa o dataframe com os dados SAV.

        Parameters
        ----------
        list_cases_user : list
            Lista de casos SAV fornecidos pelo usuário.
        suffix_id : str, optional
            Identificador usado para identificar com sufixo os CSVs gerados. O padrão é uma string vazia.

        Returns
        -------
        df_dados_sav : DataFrame
            DataFrame com os dados SAV.

        Raises
        ------
        SystemExit
            Se houver espaços em branco no diretório.
        """
        self.lista_casos = [casoSAV.upper() for casoSAV in list_cases_user]
        caso_path = list_cases_user[0].replace("/","\\")
        index = caso_path.rfind("\\")
        self.path_decks = list_cases_user[0][:index] + "\\TEMP_ANR\\"

        for index, path in enumerate(list_cases_user):
            if " " in  path:
                print("ERRO FATAL! Encontrado espaços em branco no diretório. Favor corrigir!")
                sys.exit()

        # Limpa ou cria a pasta TEMP
        if self.roda_anarede:
            self.__initialize_temp_folder()

        # Inicializa o dataframe
        df_dados_sav = self.__get_data_sav(suffix_id)

        return df_dados_sav

    def filtrar_casos_sav(self, df_casos_sav):
        """
        Filtra os casos SAV.

        Esta função recebe um DataFrame de casos SAV, exibe uma lista de casos disponíveis para o usuário,
        e retorna um DataFrame filtrado com base na entrada do usuário.

        Parameters
        ----------
        df_casos_sav : DataFrame
            DataFrame contendo os casos SAV.

        Returns
        -------
        df_casos_sav_filter : DataFrame
            DataFrame filtrado com os casos SAV selecionados pelo usuário.

        Notes
        -----
        O usuário pode selecionar casos específicos por meio de um índice único, uma lista de índices separados por vírgulas,
        ou um intervalo de índices separados por dois pontos. Se o usuário inserir ":", todos os casos serão selecionados.
        """
        # Buscando nome das DFs
        list_savs = df_casos_sav['Nome_Arquivo'].tolist()
        list_num_cases = df_casos_sav['Numero_Caso'].tolist()
        list_name_cases = df_casos_sav['Nome_Caso'].tolist()

        list_cases = []
        print("\nLista de casos disponíveis para carregamento:")
        for i, _ in enumerate(list_savs):
            option = f"[{i}]. {list_savs[i]} - {list_num_cases[i]}-{list_name_cases[i]}"
            list_cases.append(option)
            print(option)

        print("Informar o(s) caso(s) que deseja analisar:")
        user_casos = input()

        # Caso seja informado um caso com um intervalo (:)
        if user_casos == ":":
            df_casos_sav_filter = df_casos_sav
        elif ":" in user_casos:
            index_start, index_end = user_casos.split(":")
            df_casos_sav_filter = df_casos_sav[int(index_start):int(index_end)+1]

        if "," in user_casos:
            list_cases = user_casos.split(",")
            integer_map = map(int, list_cases)
            int_list_cases = list(integer_map)

            df_casos_sav_filter = df_casos_sav.loc[int_list_cases]

        if len(user_casos) < 3 and user_casos != ":":
            case = int(user_casos)
            df_casos_sav_filter = df_casos_sav.loc[[case]]
            # df = pd.DataFrame(df_casos_sav_filter)

        return df_casos_sav_filter

    def plot_tabela_excel(self, dic_dfs_grouped):
        """
        Plota tabelas em arquivos Excel.

        Esta função recebe um dicionário de DataFrames agrupados, cria um arquivo Excel para
        cada DataFrame, adiciona uma tabela ao arquivo com os dados do DataFrame e ajusta a
        largura das colunas para melhor visualização.
        Ela também imprime o tempo gasto para criar cada arquivo Excel.

        Parameters
        ----------
        dic_dfs_grouped : dict
            Dicionário de DataFrames agrupados.

        Notes
        -----
        A função utiliza a biblioteca xlsxwriter para criar os arquivos Excel.
        """
        start_time = time.time()

        for _, (grandeza, df) in enumerate(dic_dfs_grouped.items()):
            title = self.path_decks + grandeza + ".xlsx"

            writer = pd.ExcelWriter(title, engine='xlsxwriter')
            # Limpando linhas com dados sempre em 0
            df = df.loc[~(df==0).all(axis=1)]
            #
            df = df.reset_index()
            df.to_excel(writer, sheet_name='DataFrame', startrow=1, header=False, index=False)
            # workbook = writer.book
            worksheet = writer.sheets['DataFrame']
            (max_row, max_col) = df.shape
            # Create a list of column headers, to use in add_table().
            column_settings = [{'header': column} for column in df.columns]
            # Add the Excel table structure. Pandas will add the data.
            worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
            # Make the columns wider for clarity.
            worksheet.set_column(0, max_col - 1, 12)
            # Close the Pandas Excel writer and output the Excel file.
            writer.close()

            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CRIAÇÃO DOS ARQUIVO EXCEL: {grandeza}")
            start_time= time.time()

    def plot_table_csv(self, grand_monit, list_df_grand_monit):
        """
        Gera arquivos CSV para cada DataFrame em uma lista.

        Esta função percorre uma lista de DataFrames, e para cada DataFrame, gera um arquivo CSV com os dados do DataFrame.
        Ela também imprime o tempo gasto para gerar cada arquivo CSV.

        Parameters
        ----------
        grand_monit : list
            Lista contendo os títulos para os arquivos CSV.
        list_df_grand_monit : list
            Lista de DataFrames para os quais os arquivos CSV serão gerados.

        Notes
        -----
        Os arquivos CSV são salvos no diretório especificado em self.path_decks, com o título correspondente da lista grand_monit.
        """
        start_time = time.time()

        for j, _ in enumerate(grand_monit):
            df = list_df_grand_monit[j]
            title = grand_monit[j]

            df.to_csv(self.path_decks + "df_" + str(title) +".csv", index=True, sep=";", encoding="utf-8-sig", decimal=",")

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO CSV DF GRANDEZAS")

    def subplots_tensao_recomp(self, df):
        """
        Plota subplots de tensão e salva as figuras.

        Esta função recebe um DataFrame, ajusta o DataFrame para plotagem, converte as colunas necessárias para float,
        e plota subplots de tensão para cada conjunto de três colunas. Ela também salva cada subplot como uma imagem PNG.
        Além disso, plota um gráfico geral com todos os subplots e salva como uma imagem PNG. O tempo gasto para gerar
        os plots é impresso no console.

        Parameters
        ----------
        df : DataFrame
            DataFrame contendo os dados para plotagem.

        Notes
        -----
        A função utiliza a biblioteca matplotlib para criar os plots.
        """
        start_time = time.time()

        # Inserindo informações de coordenadas no df
        df_plot = self.__adjust_df_tensao_to_plot(df)

        # Garantindo dados no formato numérico
        columns_to_convert = df_plot.columns[1:]  # Assuming columns 2 to 4 need conversion
        df_plot[columns_to_convert] = df_plot[columns_to_convert].astype(float)

        # Plotando
        col_indexes = list(range(1, len(df_plot.columns)-1, 3))
        plt.style.use('ggplot')
        counter = 1
        for i, _ in enumerate(col_indexes):
            if i < len(col_indexes):
                selected_columns = ['passo'] + list(df_plot.iloc[:, col_indexes[i]:col_indexes[i] + 3].columns)
                df_plot_temp = df_plot[selected_columns]

                df_plot_temp.plot(   x="passo",
                                subplots=True,
                                layout=(1,3),
                                legend=False,
                                title=list(df_plot_temp.columns[1:]),
                                figsize=(20,5),
                                ylim=(0.90, 1.05)
                                )
                plt.tight_layout()
                plt.savefig(self.path_decks + f"PLOT_subplots_v_{counter}.png")
                counter += 1

        #Plot geral
        df_plot.plot(   x="passo",
                                subplots=True,
                                layout=(len(df_plot.columns)//6+1,6),
                                legend=False,
                                title=list(df_plot.columns[1:]),
                                figsize=(20, 5 * len(df_plot.columns)//10),
                                ylim=(0.90, 1.05)
                                )
        plt.tight_layout()
        plt.savefig(self.path_decks + "PLOT_subplots_v_total.png")

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO PLOT DF")
        plt.show(block=False)

    def subplots_potencia_recomp(self, df, filtro_eqp = None, type_var = "MW"):
        """
        Plota subplots de potência e salva as figuras.

        Esta função recebe um DataFrame, ajusta o DataFrame para plotagem, converte as colunas necessárias para float,
        e plota subplots de potência para cada conjunto de três colunas. Ela também salva cada subplot como uma imagem PNG.
        Além disso, se um filtro de equipamento for fornecido, a função filtrará o DataFrame de acordo com esse filtro antes
        de plotar e salvar as figuras. O tempo gasto para gerar os plots é impresso no console.

        Parameters
        ----------
        df : DataFrame
            DataFrame contendo os dados para plotagem.
        filtro_eqp : list, optional
            Lista de equipamentos para filtrar o DataFrame antes da plotagem. O padrão é None.
        ylimite : tuple, optional
            Limites do eixo y para a plotagem. O padrão é uma tupla vazia.
        type_var : str, optional
            Tipo de potência para a plotagem. Pode ser "MW" ou "Mvar". O padrão é "MW".

        Notes
        -----
        A função utiliza a biblioteca matplotlib para criar os plots.
        """
        start_time = time.time()

        # Inserindo informações de coordenadas no df
        df_plot = self.__adjust_df_potencia_to_plot(df)

        # Garantindo dados no formato numérico
        columns_to_convert = df_plot.columns[1:]  # Assuming columns 2 to 4 need conversion
        df_plot[columns_to_convert] = df_plot[columns_to_convert].astype(float)

        if filtro_eqp is not None:
            filtro_eqp = ["passo"] + filtro_eqp
            df_plot = df_plot[filtro_eqp]

        # Plotando
        col_indexes = list(range(1, len(df_plot.columns)-1, 3))
        if not col_indexes:
        # if col_indexes == []:
            col_indexes = [1]
        col_indexes_visao_geral = list(range(1, len(df_plot.columns)-1, 9))
        plt.style.use('ggplot')
        counter = 1

        if filtro_eqp is None:
            for i, _ in enumerate(col_indexes_visao_geral):
                if i < len(col_indexes_visao_geral):
                    selected_columns = ['passo'] + list(df_plot.iloc[:, col_indexes_visao_geral[i]:col_indexes_visao_geral[i] + 9].columns)
                    df_plot_temp = df_plot[selected_columns]

                    df_plot_temp.plot(   x="passo",
                                    subplots=True,
                                    layout=(3,3),
                                    legend=False,
                                    title=list(df_plot_temp.columns[1:]),
                                    figsize=(20,5),)
                                    # ylim=(0.90, 1.05)
                    plt.tight_layout()
                    if type_var == "MW":
                        plt.savefig(self.path_decks + f"PLOT_subplots_pot_ativ_{counter}.png")
                    elif type_var == "Mvar":
                        plt.savefig(self.path_decks + f"PLOT_subplots_pot_reativ_{counter}.png")
                    counter += 1
        else:
            for i, _ in enumerate(col_indexes):
                if i < len(col_indexes):
                    selected_columns = ['passo'] + list(df_plot.iloc[:, col_indexes[i]:col_indexes[i] + 3].columns)
                    df_plot_temp = df_plot[selected_columns]

                    df_plot_temp.plot(   x="passo",
                                    subplots=True,
                                    layout=(1,df_plot_temp.shape[1]-1),
                                    legend=False,
                                    title=list(df_plot_temp.columns[1:] + " [" + type + "]"),
                                    figsize=(20,5),
                                    # ylim=(0.90, 1.05)
                                    )
                    plt.tight_layout()
                    if type_var == "MW":
                        plt.savefig(self.path_decks + f"PLOT_subplots_pot_ativ_{counter}.png")
                    elif type_var == "Mvar":
                        plt.savefig(self.path_decks + f"PLOT_subplots_pot_reativ_{counter}.png")
                    counter += 1
        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO PLOT DF")
        plt.show(block=False)

    def analysis_dfs_delta(self, casos_antes, casos_depois, filtro_pu = 0.002, filtro_val = 10,
                           complement_cols = True, grandezas_rbar = None, grandezas_rlin = None, export_csv = True):
        """
        Realiza uma análise de variação nos DataFrames.

        Esta função recebe dois conjuntos de casos (antes e depois), um limiar mínimo de variação para
        grandezas em p.u. e normais, e listas de grandezas para RBAR e RLIN. Ela coleta os casos antes e
        depois, ajusta os DataFrames para eliminar colunas sem dados float, e realiza uma análise de delta
        nos DataFrames. Os resultados são salvos em um dicionário e, se solicitado, exportados como arquivos CSV.

        Parameters
        ----------
        casos_antes : list
            Lista de casos antes da alteração.
        casos_depois : list
            Lista de casos depois da alteração.
        filtro_pu : float, optional
            Filtro de potência útil para a análise de delta. O padrão é 0.002.
        filtro_val : int, optional
            Filtro de valor para a análise de delta. O padrão é 10.
        complement_cols : bool, optional
            Se True, complementa as colunas do DataFrame. O padrão é True.
        grandezas_rbar : list, optional
            Lista de grandezas para RBAR. O padrão é uma lista vazia.
        grandezas_rlin : list, optional
            Lista de grandezas para RLIN. O padrão é uma lista vazia.
        export_csv : bool, optional
            Se True, exporta os resultados como arquivos CSV. O padrão é True.

        Returns
        -------
        dic_dfs : dict
            Dicionário contendo os DataFrames resultantes da análise de delta.

        Notes
        -----
        A função imprime o tempo gasto para organizar e carregar os arquivos .SAVs antes e depois, e para gerar os plots.
        """
        # Coleta casos Antes e Depois
        start_time = time.time()
        df_casos_sav_antes = self.get_casos_sav(casos_antes, suffix_id="_antes")
        dic_dfs_rbar_antes, dic_dfs_rlin_antes = self.get_csv_sav(df_casos_sav_antes, get_rbar=True, get_rlin=True, suffix_id="_antes")

        self.clear_temp_folder = False
        df_casos_sav_depois = self.get_casos_sav(casos_depois, suffix_id="_depois")
        dic_dfs_rbar_depois, dic_dfs_rlin_depois = self.get_csv_sav(df_casos_sav_depois, get_rbar=True, get_rlin=True, suffix_id="_depois")

        # Acerta dfs para eliminar colunas sem dados float, montando o indice
        cols_inic_rbar = ["Area","Tipo_Barra","Nome_Barra"]
        cols_inic_rlin = ['Area_BarraDe', 'Area_BarraPara', 'Tensao_BarraDe','Tensao_BarraPara', 'BarraDe',
                        'BarraPara', 'Nome_BarraDe', 'Nome_BarraPara', 'NumCirc',]

        dic_dfs_rbar_antes_adj = self.__adjust_df_python(dic_dfs_rbar_antes, index_df = "Numero", cols_inic = cols_inic_rbar)
        dic_dfs_rbar_depois_adj = self.__adjust_df_python(dic_dfs_rbar_depois, index_df = "Numero", cols_inic = cols_inic_rbar)
        dic_dfs_rlin_antes_adj = self.__adjust_df_python(dic_dfs_rlin_antes, index_df = "ID", cols_inic = cols_inic_rlin)
        dic_dfs_rlin_depois_adj = self.__adjust_df_python(dic_dfs_rlin_depois, index_df = "ID", cols_inic = cols_inic_rlin)
        print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: ORGANIZA E CARREGA .SAVs ANTES E DEPOIS")

        # Análise para RBAR
        start_time = time.time()
        list_filtro_pu = ["Tensao_MOD"]
        dic_dfs = {}
        for _, (grandeza, __) in enumerate(dic_dfs_rbar_depois_adj.items()):
            if grandeza in grandezas_rbar:
                start_time = time.time()
                df_delta_grandeza = pd.DataFrame()
                df_sts_grandeza = pd.DataFrame()
                df_delta_grandeza_exp = pd.DataFrame()
                df_sts_grandeza_exp = pd.DataFrame()

                # Define o filtro de dados
                filtro_df = filtro_pu if grandeza in list_filtro_pu else filtro_val

                df_delta_grandeza, df_sts_grandeza = self.__get_df_delta(df_antes = dic_dfs_rbar_antes_adj[grandeza], df_depois = dic_dfs_rbar_depois_adj[grandeza], delta_minimo=filtro_df)
                if complement_cols:
                    df_delta_grandeza_exp = self.__complement_df_sts(dic_dfs_rbar_depois[grandeza], df_delta_grandeza, "Numero", cols_inic_rbar)
                    df_sts_grandeza_exp = self.__complement_df_sts(dic_dfs_rbar_depois[grandeza], df_sts_grandeza, "Numero", cols_inic_rbar)

                key_delta_grandeza = f'delta_{grandeza}'
                key_sts_grandeza = f'sts_{grandeza}'
                if complement_cols:
                    key_delta_grandeza_exp = f'delta_{grandeza}_exp'
                    key_sts_grandeza_exp = f'sts_{grandeza}_exp'

                dic_dfs[key_delta_grandeza] = df_delta_grandeza
                dic_dfs[key_sts_grandeza] = df_sts_grandeza
                if complement_cols:
                    dic_dfs[key_delta_grandeza_exp] = df_delta_grandeza_exp
                    dic_dfs[key_sts_grandeza_exp] =  df_sts_grandeza_exp

                # Exporta CSVs
                if export_csv:
                    dic_dfs_rbar_depois[grandeza].to_csv(self.path_decks +  grandeza + "_depois.csv", index=True, sep=";", encoding="utf-8-sig", decimal=",")
                    dic_dfs_rbar_antes[grandeza].to_csv(self.path_decks +  grandeza + "_antes.csv", index=True, sep=";", encoding="utf-8-sig", decimal=",")
                    df_delta_grandeza.to_csv(self.path_decks + "delta_" + grandeza + ".csv", index=True, sep=";", encoding="utf-8-sig", decimal=",", float_format='%.3f')
                    df_sts_grandeza.to_csv(self.path_decks + "sts_" + grandeza + ".csv", index=True, sep=";", encoding="utf-8-sig", decimal=",", float_format='%.3f')
                    if complement_cols:
                        df_delta_grandeza_exp.to_csv(self.path_decks + "delta_exp_" + grandeza + ".csv", index=True, sep=";", encoding="utf-8-sig", decimal=",", float_format='%.3f')
                        df_sts_grandeza_exp.to_csv(self.path_decks + "sts_exp_" + grandeza + ".csv", index=True, sep=";", encoding="utf-8-sig", decimal=",", float_format='%.3f')

                print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: PROCESSANDO ANÁLISE ESTATÍSTICA NA GRANDEZA: {grandeza} - {len(df_delta_grandeza)} elementos pós-filtro")

        # Análise para RLIN
        for _, (grandeza, __) in enumerate(dic_dfs_rlin_depois_adj.items()):
            if grandeza in grandezas_rlin:
                start_time = time.time()

                df_delta_grandeza = pd.DataFrame()
                df_sts_grandeza = pd.DataFrame()
                df_delta_grandeza_exp = pd.DataFrame()
                df_sts_grandeza_exp = pd.DataFrame()

                # Define o filtro de dados
                filtro_df = filtro_pu if grandeza in list_filtro_pu else filtro_val

                df_delta_grandeza, df_sts_grandeza = self.__get_df_delta(df_antes = dic_dfs_rlin_antes_adj[grandeza], df_depois = dic_dfs_rlin_depois_adj[grandeza], delta_minimo=filtro_df)
                if complement_cols:
                    df_delta_grandeza_exp = self.__complement_df_sts(dic_dfs_rlin_depois[grandeza], df_delta_grandeza, "ID", cols_inic_rlin)
                    df_sts_grandeza_exp = self.__complement_df_sts(dic_dfs_rlin_depois[grandeza], df_sts_grandeza, "ID", cols_inic_rlin)

                key_delta_grandeza = f'delta_{grandeza}'
                key_sts_grandeza = f'sts_{grandeza}'
                if complement_cols:
                    key_delta_grandeza_exp = f'delta_{grandeza}_exp'
                    key_sts_grandeza_exp = f'sts_{grandeza}_exp'

                dic_dfs[key_delta_grandeza] = df_delta_grandeza
                dic_dfs[key_sts_grandeza] = df_sts_grandeza
                if complement_cols:
                    dic_dfs[key_delta_grandeza_exp] = df_delta_grandeza_exp
                    dic_dfs[key_sts_grandeza_exp] =  df_sts_grandeza_exp

                # Exporta CSVs
                if export_csv:
                    dic_dfs_rlin_depois[grandeza].to_csv(self.path_decks +  grandeza + "_depois.csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")
                    dic_dfs_rlin_antes[grandeza].to_csv(self.path_decks +  grandeza + "_antes.csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")
                    df_delta_grandeza.to_csv(self.path_decks + "delta_" + grandeza + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",", float_format="%.3f")
                    df_sts_grandeza.to_csv(self.path_decks + "sts_" + grandeza + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",", float_format="%.3f")
                    if complement_cols:
                        df_delta_grandeza_exp.to_csv(self.path_decks + "delta_exp_" + grandeza + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",", float_format="%.3f")
                        df_sts_grandeza_exp.to_csv(self.path_decks + "sts_exp_" + grandeza + ".csv", index=False, sep=";", encoding="utf-8-sig", decimal=",", float_format="%.3f")

                print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: PROCESSANDO ANÁLISE ESTATÍSTICA NA GRANDEZA:{grandeza} - {len(df_delta_grandeza)} elementos pós-filtro")
        return dic_dfs

    def get_csv_sav(self, df_casos_sav, get_rbar= True, get_rlin = True, list_barra = None,
                    list_areas = None, make_multilevel_df = False, suffix_id=""):
        """
        Obtém os DataFrames dos arquivos RBAR e RLIN em formato CSV.

        Parameters
        ----------
        df_casos_sav : DataFrame
            DataFrame contendo os casos SAV.
        get_rbar : bool, optional
            Indica se os DataFrames dos arquivos RBAR devem ser obtidos. O padrão é True.
        get_rlin : bool, optional
            Indica se os DataFrames dos arquivos RLIN devem ser obtidos. O padrão é True.
        list_barra : list or None, optional
            Lista das barras para as quais deseja-se extrair os dados. Se None, todas as barras
            são consideradas. O padrão é None.
        list_areas : list or None, optional
            Lista das áreas para as quais deseja-se extrair os dados. Se None, todas as áreas
            são consideradas. O padrão é None.
        make_multilevel_df : bool, optional
            Indica se os DataFrames resultantes devem ser multilevel. O padrão é False.
        suffix_id : str, optional
            Identificação adicional para os DataFrames. O padrão é uma string vazia.

        Returns
        -------
        dic_dfs_rbar : dict
            Dicionário contendo os DataFrames dos arquivos RBAR.
        dic_dfs_rlin : dict
            Dicionário contendo os DataFrames dos arquivos RLIN.
        """
        dic_dfs_rbar = {}
        dic_dfs_rlin = {}

        if get_rbar:
            dic_dfs_rbar = self.__get_rbar(df_casos_sav, list_barra, list_areas, make_multilevel_df, suffix_id)

        if get_rlin:
            dic_dfs_rlin = self.__get_rlin(df_casos_sav, list_barra, list_areas, make_multilevel_df, suffix_id)

        return dic_dfs_rbar, dic_dfs_rlin

    def fragmenta_sav(self, df_casos_sav):
        # Checando se dicionário com exceções chegou
        start_time = time.time()

        file_end = []
        file_out = []
        body_list_cases, file_out, file_end = self.__deck_fragmenta(file_out, file_end, df_casos_sav)

        # Escrevendo deck
        deck_fragmenta = self.path_decks + "deck_fragmenta.pwf"
        with open(deck_fragmenta, "w", encoding='cp1252') as text_file:
            text_file.write(body_list_cases)
        print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CRIAÇÃO DOS DECKS ANAREDE")
        start_time = time.time()

        # Elaborando comando
        comando = self.engine + " " + '"' + deck_fragmenta + '"' + " " + '"' + file_end[0] + '"'

        # Executa ANAREDE
        self._exe_command_anarede(comando, file_end)
        print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO ANAREDE: CRIAÇÃO DOS RELATÓRIOS .OUT E .END")

        return

    def get_decks_from_sav(self, df_casos_sav):
        # Passo 1 - Fragmenta o arquivo .SAV
        self.fragmenta_sav(df_casos_sav)

        # Passo 2 - Realiza a leitura dos arquivos para memória
        arquivos = os.listdir(self.path_decks)
        arquivos_pwf = [arquivo for arquivo in arquivos if arquivo.upper().startswith("PWF") and arquivo.upper().endswith("PWF")]

        # Passo 3 - Coletando os dataframes dos equipamentos
        dic_PWF = {}
        oDeck = decks.DECKS()
        for index, row in df_casos_sav.iterrows():
            # dic_PWF_temp = oDeck.get_df_PWF(arquivos_pwf[index])
            # chave = row["Nome_Arquivo"] + "_" + row["Numero_Caso"]
            dic_PWF[arquivos_pwf[index]] = oDeck.get_df_PWF(self.path_decks + arquivos_pwf[index])

        return dic_PWF
