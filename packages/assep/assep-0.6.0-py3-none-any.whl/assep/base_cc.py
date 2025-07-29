import os, shutil
import subprocess
import zipfile
import glob
import pandas as pd
import numpy as np

class BaseCC:
    # Inicializa a representação dos dados de uma barra
    def __init__(self):
        self.path_orig_SUL = r"\baseCC\SUL\1_original"
        self.path_orfg_SUL = r"\baseCC\SUL\2_original_frag"
        self.path_nvfg_SUL = r"\baseCC\SUL\3_novo_frag"
        self.path_novo_SUL = r"\baseCC\SUL\4_novo"
        self.path_falt_SUL = r"\baseCC\SUL\5_decks_faltantes"

        self.path_orig_SEC = r"\baseCC\SECO\1_original"
        self.path_orfg_SEC = r"\baseCC\SECO\2_original_frag"
        self.path_nvfg_SEC = r"\baseCC\SECO\3_novo_frag"
        self.path_novo_SEC = r"\baseCC\SECO\4_novo"
        self.path_falt_SEC = r"\baseCC\SECO\5_decks_faltantes"

        self.path_orig_NNE = r"\baseCC\NNE\1_original"
        self.path_orfg_NNE = r"\baseCC\NNE\2_original_frag"
        self.path_nvfg_NNE = r"\baseCC\NNE\3_novo_frag"
        self.path_novo_NNE = r"\baseCC\NNE\4_novo"
        self.path_falt_NNE = r"\baseCC\NNE\5_decks_faltantes"

    ###================================================================================================================
    ###
    ### XXXX
    ###
    ###================================================================================================================
    def set_paths(self, path_PAR):
        path_baseCC = path_PAR + r"\baseCC"
        paths_to_create = [path_PAR + self.path_orig_SUL, path_PAR + self.path_orfg_SUL, path_PAR + self.path_nvfg_SUL, path_PAR + self.path_novo_SUL, path_PAR + self.path_falt_SUL,
                           path_PAR + self.path_orig_SEC, path_PAR + self.path_orfg_SEC, path_PAR + self.path_nvfg_SEC, path_PAR + self.path_novo_SEC, path_PAR + self.path_falt_SEC,
                           path_PAR + self.path_orig_NNE, path_PAR + self.path_orfg_NNE, path_PAR + self.path_nvfg_NNE, path_PAR + self.path_novo_NNE, path_PAR + self.path_falt_NNE,
                           ]
        # Limpando arquivos anteriores
        try:
            shutil.rmtree(path_baseCC)
        except Exception as e:
            print(f"Error deleting files in {path_baseCC}: {e}")

        # Acertando pastas dependentes
        for i in range(len(paths_to_create)):
            if os.path.isdir(paths_to_create[i]):
                shutil.rmtree(paths_to_create[i])
            os.makedirs(paths_to_create[i])

        # Inicializando a pasta original - SUL
        alt_files = [f for f in os.listdir(path_PAR) if f.upper().endswith(".ALT")] # or f.endswith(".ALT"))]
        for alt_file in alt_files:
            source_path = os.path.join(path_PAR, alt_file)
            if alt_file.startswith("SUL"):
                destination_path = os.path.join(path_PAR + self.path_orig_SUL, alt_file)
            elif alt_file.startswith("SEC"):
                destination_path = os.path.join(path_PAR + self.path_orig_SEC, alt_file)
            elif alt_file.startswith("NNE"):
                destination_path = os.path.join(path_PAR + self.path_orig_NNE, alt_file)
            try:
                shutil.copy(source_path, destination_path)
            except Exception as e:
                print(f"Error copying {source_path} to {destination_path}: {e}")
        return

    def get_stoppers(self):
        stoppers_deck = []
        stoppers_deck.append("(======================== OBRAS DE TRANSMISSÃO =================================")
        stoppers_deck.append("(============================== OBRAS DE GERAÇÃO ===============================")
        stoppers_deck.append("(=========== OBRAS NAS REDES DE DISTRIBUIÇÃO COM IMPACTO SISTÊMICO =============")
        stoppers_deck.append("(=========== DEMAIS OBRAS ======================================================")

        return stoppers_deck

    def get_sub_stoppers(self):
        sub_stoppers_deck = []
        sub_stoppers_deck.append("(*  UHE                                                                        *")
        sub_stoppers_deck.append("(*  PCH                                                                        *")
        sub_stoppers_deck.append("(*  UTE                                                                        *")
        sub_stoppers_deck.append("(*  UEE                                                                        *")
        sub_stoppers_deck.append("(*  UFV                                                                        *")

        return sub_stoppers_deck

    def get_dict_siger_obra(self, data_list, curr_year, df_robras):
        # Definindo cabeçalhos pré-definidos para pausar obra
        stoppers_deck = self.get_stoppers()
        sub_stoppers_deck = self.get_sub_stoppers()
        # Parâmetros a serem reiniciados a cada iteração
        flag_start_siger_obra = False
        data_SO = []
        dic_data_SO = {}
        group_tipo_obra = 'Acerto_Base'
        group_subtipo_obra = ""
        # df_robras.set_index('Código de Obra', inplace=True)
        # Varrendo o deck em busca dos cabeçalhos pré-definidos
        for i in range(len(data_list)):
            if data_list[i][:13] == "(#SIGER_OBRA:":
                # Finalizo e salvo o SIGER Obra
                if len(data_SO) > 2:
                    data_SO.pop()
                    dic_data_SO[siger_obra] = data_SO
                    data_SO = []
                # Identifica SIGER Obra
                siger_obra = data_list[i].strip()[13:]
                siger_obra = siger_obra.replace('"',"")
                # Verifica se existe a obra no SIGER
                if siger_obra in df_robras.index:
                    # data_siger = df_robras.loc[siger_obra]["Data"].strftime('%d/%m/%Y')
                    ano_siger = str(df_robras.loc[siger_obra]["Ano"])#.strftime('%Y')
                else:
                    indices = df_robras.loc[df_robras['Código de Obra de Saída'] == siger_obra].index
                    if len(indices) > 0:
                        ano_siger = str(df_robras.loc[indices[0]]["Ano"])#["Data de Saída"].strftime('%Y')
                    else:
                        ano_siger = "OBRA NÃO EXISTE SIGER"

                # Preencho dados do SIGER Obra
                data_SO.append("(GRUPO_PAR: " + group_tipo_obra)
                data_SO.append("(SUBGR_PAR: " + group_subtipo_obra)
                data_SO.append("(ANO_CICLO_ANT: " + curr_year)
                data_SO.append("(ANO_CICLO_NOV: " + ano_siger)
                data_SO.append("(")
                #
                data_SO.append(data_list[i-1])
                flag_start_siger_obra = True

            elif data_list[i].strip() in stoppers_deck:
                group_tipo_obra = data_list[i]
                group_tipo_obra = group_tipo_obra.replace('=',"")
                group_tipo_obra = group_tipo_obra.replace('(',"")
                group_tipo_obra = group_tipo_obra.strip()
                if len(data_SO) > 2:
                    data_SO.pop()
                    data_SO.pop()
                    dic_data_SO[siger_obra] = data_SO
                    data_SO = []
                    flag_start_siger_obra = False

            elif data_list[i].strip() in sub_stoppers_deck:
                group_subtipo_obra = data_list[i]
                group_subtipo_obra = group_subtipo_obra.replace('*',"")
                group_subtipo_obra = group_subtipo_obra.replace('(',"")
                group_subtipo_obra = group_subtipo_obra.strip()
                if len(data_SO) > 2:
                    data_SO.pop()
                    dic_data_SO[siger_obra] = data_SO
                    data_SO = []
                    flag_start_siger_obra = False

            if flag_start_siger_obra:
                data_SO.append(data_list[i])

        # Verifica se não ficou algo para trás
        if len(data_SO) > 2:
            dic_data_SO[siger_obra] = data_SO

        return dic_data_SO

    def make_folder_curr_PAR_desfrag(self, path_PAR, dic_data_SO, region, curr_year):
        # Criação das pastas e desfragmentação dos arquivos
        if region == "SUL":
            folder_PAR_orig_frag_year = path_PAR + self.path_orfg_SUL + "\\" + curr_year
        elif region == "SEC":
            folder_PAR_orig_frag_year = path_PAR + self.path_orfg_SEC + "\\" + curr_year
        elif region == "NNE":
            folder_PAR_orig_frag_year = path_PAR + self.path_orfg_NNE + "\\" + curr_year

        # Criação do diretório caso não exista
        if not os.path.isdir(folder_PAR_orig_frag_year):
            os.makedirs(folder_PAR_orig_frag_year)

        # Itera no dicionário fornecido
        for key, value in dic_data_SO.items():
            name_file = folder_PAR_orig_frag_year + "\\" + key + ".alt"

            with open(name_file, 'w') as f:
                string_value = "\n".join(value)
                f.write(string_value)

    def make_folder_next_PAR_desfrag(self, path_PAR, dic_data_SO, region):
        # Criação das pastas e desfragmentação dos arquivos
        if region == "SUL":
            folder_PAR_nvfg = path_PAR + self.path_nvfg_SUL
        elif region == "SEC":
            folder_PAR_nvfg = path_PAR + self.path_nvfg_SEC
        elif region == "NNE":
            folder_PAR_nvfg = path_PAR + self.path_nvfg_NNE

        for key, value in dic_data_SO.items():
            new_date = value[3][16:]
            if new_date == "OBRA NÃO EXISTE SIGER":
                # Cria pasta padrão
                if not os.path.isdir(folder_PAR_nvfg + "\\sem_data_siger"):
                    os.makedirs(folder_PAR_nvfg + "\\sem_data_siger")
                name_file = folder_PAR_nvfg + "\\sem_data_siger\\" + key + ".alt"
                name_folder = folder_PAR_nvfg + "\\sem_data_siger"
            else:
                # Cria pasta de ano
                if not os.path.isdir(folder_PAR_nvfg + "\\" + new_date):
                    os.makedirs(folder_PAR_nvfg + "\\" + new_date)
                name_file = folder_PAR_nvfg + "\\" + new_date + "\\" + key + ".alt"
                name_folder = folder_PAR_nvfg  + "\\" + new_date

            # Printa arquivos
            with open(name_file, 'w') as f:
                string_value = "\n".join(value)
                f.write(string_value)

    def explode_files(self, path_PAR, path_arqv_orig, region, list_files_par, df_robras):
        for index, file in enumerate(list_files_par):
            # Ano do deck do ciclo passado
            if region == "SEC":
                curr_year = "20" + file[4:6]
            else:
                curr_year = "20" + file[3:5]

            # Filtrando região
            if region == "SUL":
                estados = ["MS", "RS", "PR", "SC"]
                df_robras_region = df_robras[df_robras["Estado BR"].isin(estados)]
            elif region == "SEC":
                estados = ["MG", "ES", "RJ", "SP", "GO", "MT", "MS", "DF"]
                df_robras_region = df_robras[df_robras["Estado BR"].isin(estados)]
            elif region == "NNE":
                estados = ["AM", "PA", "AC", "RR", "RO", "AP", "TO", "MA", "PI",
                           "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
                df_robras_region = df_robras[df_robras["Estado BR"].isin(estados)]

            # Conteúdo do deck do ciclo passado
            with open(path_PAR + path_arqv_orig + "\\" + file, 'r') as file:
                data_list = file.read().splitlines()

            # Transforma conteúdo do deck analisado em um dicionário
            df_robras_mod = df_robras_region.set_index('Código de Obra')
            dic_data_SO = self.get_dict_siger_obra(data_list, curr_year, df_robras_mod)

            # Desfragmentando o deck atual em subpastas
            self.make_folder_curr_PAR_desfrag(path_PAR, dic_data_SO, region, curr_year)

            # Escrevendo as obras no arquivo devido - considerando anos do PAR novo
            self.make_folder_next_PAR_desfrag(path_PAR, dic_data_SO, region)

    def generate_skull_deck(self, region_CC, start_year, year_deck):
        list_temp = []
        list_temp.append("  1      1")
        list_temp.append("ONS = SISTEMA INTERLIGADO = CONFIG DEZ/2026 = VERSÃO 06/04/2022 = BR2612PF.ANA")
        list_temp.append("  2      1")
        list_temp.append("================================================================================")
        list_temp.append("  2      2")
        list_temp.append(f" CICLO DO PAR ANO {start_year} / {start_year+4} - VERSÃO 0")
        list_temp.append("  2      3")
        list_temp.append(" CASO DE REFERÊNCIA BR2612PF.ANA GERADO A PARTIR DO CASO DE REFERÊNCIA")
        list_temp.append("  2      4")
        list_temp.append(" BR2512PF.ANA DE 06/04/2022, APLICANDO-SE OS ARQUIVOS DE ALTERAÇÃO")
        list_temp.append("  2      5")
        list_temp.append(" NNE2612PF.ALT, SECO2612PF.ALT E SUL2612PF.ALT.")
        list_temp.append("  2      6")
        list_temp.append("================================================================================")
        list_temp.append("")
        list_temp.append("(===============================================================================")
        list_temp.append(f"(= EQUIPE DE TRABALHO: CICLO {start_year} - {start_year+4} / ANO {year_deck} {region_CC} / VERSÃO 0             ")
        list_temp.append("(===============================================================================")
        list_temp.append("(= EQUIPE DE TRABALHO:                                                         =")
        list_temp.append("(= EGP                                                                         =")
        list_temp.append("(= Guilherme da Siva Santos    (guilherme.santos@ons.org.br)  Tel: 21 34449270 =")
        list_temp.append("(= Marianna Nogueira Bacelar   (marianna@ons.org.br)          Tel: 21 34449685 =")
        list_temp.append("(= Pedro Guimarães Trindade    (ptrindade@ons.org.br)         Tel: 21 34449570 =")
        list_temp.append("(= Vinícius Amante Pineschi    (vinicius.pineschi@ons.org.br) Tel: 21 34449533 =")
        list_temp.append("(=                                                                             =")
        list_temp.append("(= EGN                                                                         =")
        list_temp.append("(= Carlos Alberto M. Cerqueira (carlosmc@ons.org.br)          Tel: 81 32178958 =")
        list_temp.append("(= Pedro S. de Oliveira Villela(pedrovillela@ons.org.br)      Tel: 81 32178940 =")
        list_temp.append("(= Rodolfo G. de Souza Leite   (rodolfo.leite@ons.org.br)     Tel: 81 32178941 =")
        list_temp.append("(=                                                                             =")
        list_temp.append("(= EGS                                                                         =")
        list_temp.append("(= Anderson Rotay Gaspar       (andersonrg@ons.org.br)        Tel: 48 32613938 =")
        list_temp.append("(= Nathan Kelvi de A. Bueno    (nathan.bueno@ons.org.br)      Tel: 48 32613928 =")
        list_temp.append("(===============================================================================")
        list_temp.append("")
        list_temp.append("")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("(======================== OBRAS DE TRANSMISSÃO =================================")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("(============================== OBRAS DE GERAÇÃO ===============================")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("")
        list_temp.append("(*******************************************************************************")
        list_temp.append("(*  UHE                                                                        *")
        list_temp.append("(*******************************************************************************")
        list_temp.append("")
        list_temp.append("(*******************************************************************************")
        list_temp.append("(*  PCH                                                                        *")
        list_temp.append("(*******************************************************************************")
        list_temp.append("")
        list_temp.append("(*******************************************************************************")
        list_temp.append("(*  UTE                                                                        *")
        list_temp.append("(*******************************************************************************")
        list_temp.append("")
        list_temp.append("(*******************************************************************************")
        list_temp.append("(*  UEE                                                                        *")
        list_temp.append("(*******************************************************************************")
        list_temp.append("")
        list_temp.append("(*******************************************************************************")
        list_temp.append("(*  UFV                                                                        *")
        list_temp.append("(*******************************************************************************")
        list_temp.append("")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("(=========== OBRAS NAS REDES DE DISTRIBUIÇÃO COM IMPACTO SISTÊMICO =============")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("(=========== DEMAIS OBRAS ======================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("(===============================================================================")
        list_temp.append("")

        return list_temp

    def insert_siger_obra_no_deck(self, path_to_join, list_files, list_deck_par, year_deck, dic_obras_ano):
        # Inserindo as obras nos decks
        for j in range(len(list_files)):
            with open(path_to_join + "\\" + list_files[j], 'r') as file:
                value = file.read().splitlines()
                deck = value[5:]
            #
            # Salva grupo
            group_tipo_obra = value[0][12:].strip()
            group_subtipo_obra = value[1][12:].strip()

            # Insere obra no deck
            if group_tipo_obra == 'OBRAS DE TRANSMISSÃO':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(======================== OBRAS DE TRANSMISSÃO =================================") - 3
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            # elif group_tipo_obra == 'OBRAS SEM CONCESSÃO DEFINIDA':
            #     # Acho grupo que aparece depois
            #     index_to_insert = list_deck_par.index("(=========== OBRAS NAS REDES DE DISTRIBUIÇÃO COM IMPACTO SISTÊMICO =============") - 3
            #     # Inserindo obra no deck
            #     list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            elif group_tipo_obra == 'OBRAS NAS REDES DE DISTRIBUIÇÃO COM IMPACTO SISTÊMICO':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(=========== OBRAS NAS REDES DE DISTRIBUIÇÃO COM IMPACTO SISTÊMICO =============") - 3
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            # elif group_tipo_obra == 'OBRAS INFORMADAS PELO AGENTE':
            #     # Acho grupo que aparece depois
            #     index_to_insert = list_deck_par.index("(============================== OBRAS DE GERAÇÃO ===============================") - 3
            #     # Inserindo obra no deck
            #     list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            elif group_subtipo_obra == 'UHE':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(*  PCH                                                                        *") - 2
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            elif group_subtipo_obra == 'PCH':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(*  UTE                                                                        *") - 2
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            elif group_subtipo_obra == 'UTE':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(*  UEE                                                                        *") - 2
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            elif group_subtipo_obra == 'UEE':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(*  UFV                                                                        *") - 2
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            elif group_subtipo_obra == 'UFV':
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:] + deck

            elif group_tipo_obra == 'Acerto_Base':
                # Acho grupo que aparece depois
                index_to_insert = list_deck_par.index("(=========== DEMAIS OBRAS ======================================================") - 3
                # Inserindo obra no deck
                list_deck_par = list_deck_par[:index_to_insert] + deck + list_deck_par[index_to_insert:]

            else:
                print(f"Erro na identificação de grupo e subgrupo para a obra {list_files[j]}")

            # Adiciono a obra no dicionário anual
            if year_deck not in dic_obras_ano:
                dic_obras_ano[year_deck] = [list_files[j][:-4]]
            else:
                dic_obras_ano[year_deck].append(list_files[j][:-4])

        return list_deck_par, dic_obras_ano

    def make_folder_next_PAR(self, start_year, region_CC, folder_PAR_nvfg, parfiles, folder_PAR_novo, df_robras):
        dic_obras_ano = {}
        # Filtrando região
        if region_CC == "SUL":
            estados = ["MS", "RS", "PR", "SC"]
            df_robras_region = df_robras[df_robras["Estado BR"].isin(estados)]
        elif region_CC == "SEC":
            estados = ["MG", "ES", "RJ", "SP", "GO", "MT", "DF"]
            df_robras_region = df_robras[df_robras["Estado BR"].isin(estados)]
        elif region_CC == "NNE":
            estados = ["AM", "PA", "AC", "RR", "RO", "AP", "TO", "MA", "PI",
                        "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
            df_robras_region = df_robras[df_robras["Estado BR"].isin(estados)]

        list_dic_missing = []
        for i in range (6):
            dic_missing = {}
            # Gerando o conteúdo do esqueleto do deck
            year_deck = start_year + i
            list_deck_par = self.generate_skull_deck(region_CC, start_year, year_deck)
            # Localizando arquivos na pasta do ano atual
            path_to_join = folder_PAR_nvfg + "\\" + str(year_deck)
            list_files = []
            list_missings_obras = []
            # Dados para criação do novo deck aglutinado
            new_file_name = parfiles[i][:3] + str(year_deck)[-2:] + parfiles[i][5:]
            if region_CC == "SEC":
                new_file_name = parfiles[i][:4] + str(year_deck)[-2:] + parfiles[i][6:]
            path_new_deck = folder_PAR_novo + "\\" + new_file_name
            path_deck_missing = folder_PAR_novo + "\\_siger_obra_faltante_em_" + new_file_name
            if os.path.isdir(path_to_join):
                list_files = os.listdir(path_to_join)
                # Inserindo as obras nos decks
                list_deck_par, dic_obras_ano = self.insert_siger_obra_no_deck(path_to_join, list_files, list_deck_par, year_deck, dic_obras_ano)
            else:
                dic_obras_ano[year_deck] = [""]
            # Checando obras que o SIGER acusou ausência
            list_robras = (df_robras_region["Código de Obra"][df_robras_region["Ano"] == year_deck]).to_list()
            for index, codigo_obra in enumerate(list_robras):
                if codigo_obra not in dic_obras_ano[(year_deck)]:
                    list_missings_obras.append(codigo_obra)

            # Escrevendo resultados
            with open(path_new_deck, 'w') as f:
                string_value = "\n".join(list_deck_par)
                f.write(string_value)

            if len(list_missings_obras) > 0:
                with open(path_deck_missing, 'w') as f:
                    string_value = "\n".join(list_missings_obras)
                    string_value = "(Obras presentes no SIGER mas NÃO no deck do ano de: " + str(year_deck) + "\n(\n" + string_value
                    f.write(string_value)

                dic_missing[year_deck] = list_missings_obras
                list_dic_missing.append(dic_missing)

        return list_dic_missing

    def make_folder_missing_decks_PAR(self, list_missing, path_faltante, oSIGER):
        for index_dic, dic_missings in enumerate(list_missing):
            for ano_deck, list_obras in dic_missings.items():
                dic_decks = oSIGER.get_decks_from_robras(list_obras)
                if len(dic_decks) > 0:
                    path_print = path_faltante + f"\\{ano_deck}\\"
                    os.makedirs(path_print, exist_ok=True)
                    for nome_deck, str_deck in dic_decks.items():
                        with open(path_print + f"{nome_deck}.alt", 'w', encoding='cp1252') as f:
                            str_deck = str_deck.replace('\r\n', '\n')
                            f.write(str_deck)

    def gera_estrutura_PAR(self, path_PAR, oSIGER, download_missing_decks):
        # Crio a estrutura de pastas para o PAR
        self.set_paths(path_PAR)

        # Obtenho as listas de obras que devem constar em cada ano
        df_robras_area = oSIGER.get_robras_area()

        # Agrupando anualmente
        df_robras_area['Data'] = pd.to_datetime(df_robras_area['Data'])
        df_robras_area['Ano'] = df_robras_area['Data'].dt.year

        # Localizando arquivos originais a serem desfragmentados
        parfiles_SUL = [filename for filename in os.listdir(path_PAR + self.path_orig_SUL)]
        parfiles_SEC = [filename for filename in os.listdir(path_PAR + self.path_orig_SEC)]
        parfiles_NNE = [filename for filename in os.listdir(path_PAR + self.path_orig_NNE)]

        # Gerando os arquivos desfragmentados
        self.explode_files(path_PAR, self.path_orig_SUL, "SUL", parfiles_SUL, df_robras_area)
        self.explode_files(path_PAR, self.path_orig_SEC, "SEC", parfiles_SEC, df_robras_area)
        self.explode_files(path_PAR, self.path_orig_NNE, "NNE", parfiles_NNE, df_robras_area)

        # Criando decks completos e identificando obras
        start_year = 2024
        missing_SUL = self.make_folder_next_PAR(start_year, "SUL", path_PAR + self.path_nvfg_SUL, parfiles_SUL, path_PAR + self.path_novo_SUL, df_robras_area)
        missing_SEC = self.make_folder_next_PAR(start_year, "SEC", path_PAR + self.path_nvfg_SEC, parfiles_SEC, path_PAR + self.path_novo_SEC, df_robras_area)
        missing_NNE = self.make_folder_next_PAR(start_year, "NNE", path_PAR + self.path_nvfg_NNE, parfiles_NNE, path_PAR + self.path_novo_NNE, df_robras_area)

        # Fazendo download
        if download_missing_decks:
            self.make_folder_missing_decks_PAR(missing_SUL, path_PAR + self.path_falt_SUL, oSIGER)
            self.make_folder_missing_decks_PAR(missing_SEC, path_PAR + self.path_falt_SEC, oSIGER)
            self.make_folder_missing_decks_PAR(missing_NNE, path_PAR + self.path_falt_NNE, oSIGER)

    def __run_INP(self, anafas_dir, inp_file):
        # EXECUTA INP
        inp_file = inp_file.replace("\\","/")
        comando = anafas_dir + " -WIN " + '"' + inp_file + '"'
        p = subprocess.Popen(comando)
        p.wait()
        p.terminate()

        # LÊ RESULTADOS
        with open(inp_file[:-4] + ".msg", 'r') as f:
            anafas_report = f.read()
        return anafas_report

    def set_folders_aplica_decks(self, caso_base, list_decks):
        workpath = list_decks[0][:list_decks[0].rfind("/")]
        path_arquivosCC = workpath + r"/arquivosCC"

        # path_base = path_arquivosCC + r"/0_caso_base"
        # path_alt = []

        # for index, deck in enumerate(list_decks):
        #     filename = deck[deck.rfind("/")+1:-4]
        #     path_temp = path_arquivosCC + f"/{index+1}_caso_mod_{filename}"
        #     path_alt.append(path_temp)

        # # Limpando arquivos anteriores
        # try:
        #     shutil.rmtree(path_arquivosCC)
        # except Exception as e:
        #     pass
            # print(f"Error deleting files in {path_arquivosCC}: {e}")

        # Acertando pastas dependentes
        for i in range(len(path_alt)):
            os.makedirs(path_alt[i])
            shutil.copy2(list_decks[i], path_alt[i])
        os.makedirs(path_arquivosCC + r"/0_caso_base")
        shutil.copy2(caso_base, path_arquivosCC + r"/0_caso_base")

        return path_arquivosCC, path_base, path_alt

    def aplica_decks(self, anafas_dir, caso_base, list_decks):

        ## Passo 1 - Montar estrutura de pastas
        # path_arquivosCC, path_base, path_alt = self.set_folders_aplica_decks(caso_base, list_decks)
        workpath = list_decks[0][:list_decks[0].rfind("/")]
        path_arquivosCC = workpath + r"/arquivosCC"
        # Limpando arquivos anteriores
        try:
            shutil.rmtree(path_arquivosCC)
        except Exception as e:
            print(f"Error deleting files in {path_arquivosCC}: {e}")
        os.makedirs(path_arquivosCC)
        shutil.copy2(caso_base, path_arquivosCC)

        ## Passo 2 - MONTAR INP
        inp_file = path_arquivosCC + "\\batch_inp_aplica_decks.INP"
        list_inp = []
        caso_base_novo = path_arquivosCC + caso_base[caso_base.rfind("/"):]
        casos_ana_gerados = [caso_base]

        for index, deck in enumerate(list_decks):
            caso_alt = path_arquivosCC + list_decks[index][list_decks[index].rfind("/"):]
            casos_ana_gerados.append(caso_alt[:-4] + ".ana")
            if index == 0:
                list_inp.append("(==============================================================================")
                list_inp.append("(APLICANDO DECK DE ALTERAÇÃO INICIAL")
                list_inp.append("ARQV DADO")
                list_inp.append(caso_base_novo)
                list_inp.append("ARQV DALT")
                list_inp.append(deck)
                list_inp.append("ARQV SAID")
                list_inp.append(caso_alt[:-4] + ".ana")
                list_inp.append("CART")
                list_inp.append("(==============================================================================")
            else:
                list_inp.append("(APLICANDO DECK DE ALTERAÇÃO N° " + str(index))
                list_inp.append("ARQV DALT")
                list_inp.append(deck)
                list_inp.append("ARQV SAID")
                list_inp.append(caso_alt[:-4] + ".ana")
                list_inp.append("CART")
                list_inp.append("(==============================================================================")
        list_inp.append("FIM")

        # Escrevendo arquivo INP
        with open(inp_file, 'w') as f:
            f.write("\n".join(list_inp))

        # Aplica deck
        self.__run_INP(anafas_dir, inp_file)

        # Cria df para comparar no SIGER
        df_comp_siger = pd.DataFrame({
            "ignorar": [0] * len(casos_ana_gerados),
            "diretorio": casos_ana_gerados,
            "data": ["31/12/2024"] * len(casos_ana_gerados),
        })
        df_comp_siger.to_excel(path_arquivosCC + r"/comparacao_siger.xlsx", index=False)

        return

    def extract_comp_siger(self, path_download, suffix =""):
        file_type = r'\*zip'
        files = glob.glob(path_download + file_type)
        last_downloaded_zip = max(files, key=os.path.getctime)
        if suffix == "":
            zip_siger = last_downloaded_zip[:-4] + "_" + str(len(files)) + ".zip"
        else:
            zip_siger = last_downloaded_zip[:-4] + "_" + suffix + "_" + str(len(files)) + ".zip"
        os.rename(last_downloaded_zip, zip_siger)
        file_comp_siger = path_download + "\\" + zip_siger[zip_siger.rfind("\\")+1:-4] + ".alt"

        with zipfile.ZipFile(zip_siger, 'r') as zip_file:
            # Assuming you want to read all CSV files from the zip
            for file_name in zip_file.namelist():
                if file_name.upper().endswith('.ALT') or file_name.endswith(".alt"):
                    with zip_file.open(file_name) as file:
                        deck_bin = file.read()
                        deck_str = deck_bin.decode('cp1252')
                        with open(file_comp_siger, 'w') as f:
                            deck_str = deck_str.replace('\r\n', '\n')
                            f.write(deck_str)
                        os.startfile(file_comp_siger)
        return

    def __calc_MVA_shunt(self, x0):
        if x0 == "":
            mva = 999999
        elif x0 == "999999":
            mva = 0
        elif "." in x0:
            x0_adj = float(x0)
            mva = (1/x0_adj) * 100 * 100
        else:
            x0_adj = float(x0) / 100
            mva = (1/x0_adj) * 100 * 100
        return mva

    def analise_cc_only(self, dic_ANA, dic_results):
        # CHECK 1.1 - Barras acima de 70.000 cuja área não é 998;
        df_DBAR_11 = (dic_ANA["DBAR"]).copy()
        df_DBAR_11 = df_DBAR_11[(df_DBAR_11["Numero"] >= 70000) & (df_DBAR_11["Area"] != "998")]
        dic_results["df_DBAR_11"] = df_DBAR_11

        # CHECK 1.2 - Barras de 1 a 70.000 que estão com área 998;
        df_DBAR_12 = (dic_ANA["DBAR"]).copy()
        df_DBAR_12 = df_DBAR_12[(df_DBAR_12["Numero"] < 70000) & (df_DBAR_12["Area"] == "998")]
        dic_results["df_DBAR_12"] = df_DBAR_12

        # CHECK 1.3 - Barras acima de 90.000;
        df_DBAR_13 = (dic_ANA["DBAR"]).copy()
        df_DBAR_13 = df_DBAR_13[(df_DBAR_13["Numero"] >= 90000)]
        dic_results["df_DBAR_13"] = df_DBAR_13

        # CHECK 1.4 - Barras sem informação de área;
        df_DBAR_14 = (dic_ANA["DBAR"]).copy()
        df_DBAR_14 = df_DBAR_14[(df_DBAR_14["Area"] == "")]
        dic_results["df_DBAR_14"] = df_DBAR_14

        # CHECK 1.5 - Barras com informação de subárea;
        df_DBAR_15 = (dic_ANA["DBAR"]).copy()
        df_DBAR_15 = df_DBAR_15[(df_DBAR_15["SubArea"] != "")]
        dic_results["df_DBAR_15"] = df_DBAR_15[["Numero","Nome","Tensao_base","SubArea","Area"]]

        # CHECK 1.4 - Área diferente de 998 para os códigos: DCIR / DMUT / DEOL / DSHL
        df_DCIR_14 = (dic_ANA["DCIR"]).copy()
        df_DCIR_14 = df_DCIR_14[df_DCIR_14["Area"] != "998"]
        df_DCIR_14 = df_DCIR_14[["Barra_De", "Barra_Para", "Num_Circuito", "Area"]]
        df_DCIR_14 = df_DCIR_14.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_De'), left_on='Barra_De', right_on='Numero_Barra_De', how='inner')
        df_DCIR_14 = df_DCIR_14.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_Para'), left_on='Barra_Para', right_on='Numero_Barra_Para', how='inner')
        df_DCIR_14 = df_DCIR_14.drop(['Numero_Barra_De', 'Numero_Barra_Para'], axis=1)
        dic_results["df_DCIR_14"] = df_DCIR_14
        #
        df_DMUT_14 = (dic_ANA["DMUT"]).copy()
        df_DMUT_14 = df_DMUT_14[df_DMUT_14["Area"] != "998"]
        dic_results["df_DMUT_14"] = df_DMUT_14
        #
        df_DEOL_14 = (dic_ANA["DEOL"]).copy()
        df_DEOL_14 = df_DEOL_14[df_DEOL_14["Area"] != "998"]
        dic_results["df_DEOL_14"] = df_DEOL_14
        #
        df_DSHL_14 = (dic_ANA["DSHL"]).copy()
        df_DSHL_14 = df_DSHL_14[df_DSHL_14["Area"] != "998"]
        dic_results["df_DSHL_14"] = df_DSHL_14
        #
        # CHECK 1.5 - Barras com nome duplicado;
        df_DBAR_16 = (dic_ANA["DBAR"]).copy()
        df_DBAR_16 = (df_DBAR_16[df_DBAR_16.duplicated("Nome", keep=False)]).sort_values(by='Nome', ascending=False)
        dic_results["df_DBAR_16"] = df_DBAR_16

        # CHECK 1.6 - Nome como NOVO
        df_DCIR_16 = (dic_ANA["DCIR"]).copy()
        df_DCIR_16 = df_DCIR_16[df_DCIR_16["Nome_Circuito"] == "NOVO"]
        df_DCIR_16 = df_DCIR_16[["Barra_De", "Barra_Para", "Num_Circuito", "Nome_Circuito"]]
        df_DCIR_16 = df_DCIR_16.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_De'), left_on='Barra_De', right_on='Numero_Barra_De', how='inner')
        df_DCIR_16 = df_DCIR_16.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_Para'), left_on='Barra_Para', right_on='Numero_Barra_Para', how='inner')
        df_DCIR_16 = df_DCIR_16.drop(['Numero_Barra_De', 'Numero_Barra_Para'], axis=1)
        dic_results["df_DCIR_16"] = df_DCIR_16
        #
        df_DSHL_16 = (dic_ANA["DSHL"]).copy()
        df_DSHL_16 = df_DSHL_16[df_DSHL_16["Nome"] == "NOVO"]
        # df_DSHL_16 = df_DSHL_16[["Barra_De", "Barra_Para", "Num_Circuito", "Nome_Circuito"]]
        df_DSHL_16 = df_DSHL_16.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_De'), left_on='Barra_De', right_on='Numero_Barra_De', how='inner')
        df_DSHL_16 = df_DSHL_16.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_Para'), left_on='Barra_Para', right_on='Numero_Barra_Para', how='inner')
        df_DSHL_16 = df_DSHL_16.drop(['Numero_Barra_De', 'Numero_Barra_Para'], axis=1)
        df_DSHL_16 = df_DSHL_16.drop(['Codigo_Atualizacao', 'Estado','Conexao','Resistencia_Aterramento','Reatancia_Aterramento','Estado_Aterramento','SubArea','Total_Unidades','Unidades_Operando'], axis=1)
        dic_results["df_DSHL_16"] = df_DSHL_16
        #
        df_DEOL_16 = (dic_ANA["DEOL"]).copy()
        df_DEOL_16 = df_DEOL_16[df_DEOL_16["Nome"] == "NOVO"]
        dic_results["df_DEOL_16"] = df_DEOL_16
        #
        # Verifica valores de MVA dos Shunts
        df_DCIR_17 = (dic_ANA["DCIR"]).copy()
        df_DCIR_17 = df_DCIR_17[["Barra_De","Barra_Para","Num_Circuito","Tipo_Circuito","R_pos","X_pos","R_zer","X_zer","MVA"]]
        df_DCIR_17 = df_DCIR_17[(df_DCIR_17["Tipo_Circuito"] == "H") & (df_DCIR_17["MVA"] == "")]
        df_DCIR_17["MVA_calc"] = np.vectorize(self.__calc_MVA_shunt)(df_DCIR_17["X_zer"])
        df_DCIR_17 = df_DCIR_17.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome","Tensao_base"]].add_suffix('_Barra_De'), left_on='Barra_De', right_on='Numero_Barra_De', how='left')
        df_DCIR_17 = df_DCIR_17.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome","Tensao_base"]].add_suffix('_Barra_Para'), left_on='Barra_Para', right_on='Numero_Barra_Para', how='left')
        df_DCIR_17 = df_DCIR_17.drop(['Numero_Barra_De', 'Numero_Barra_Para'], axis=1)
        df_DCIR_17 = df_DCIR_17[["Barra_De","Barra_Para","Nome_Barra_De","Nome_Barra_Para","Num_Circuito","Tensao_base_Barra_De", "Tensao_base_Barra_Para","Tipo_Circuito","R_pos","X_pos","R_zer","X_zer","MVA","MVA_calc"]]
        dic_results["df_DCIR_17"] = df_DCIR_17

         # Verifica valores de Nun e Nop do DEOL
        df_DEOL_18 = (dic_ANA["DEOL"]).copy()
        df_DEOL_18 = df_DEOL_18[df_DEOL_18["Total_Unidades"] != df_DEOL_18["Unidades_Operando"]]
        dic_results["df_DEOL_18"] = df_DEOL_18

        # Verifica valores de Nun e Nop do DEOL
        df_DCIR_18 = (dic_ANA["DCIR"]).copy()
        df_DCIR_18 = df_DCIR_18[df_DCIR_18["N_Unidades_Total"] != df_DCIR_18["N_Unidades_Operando"]]
        df_DCIR_18 = df_DCIR_18.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_De'), left_on='Barra_De', right_on='Numero_Barra_De', how='left')
        df_DCIR_18 = df_DCIR_18.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_Para'), left_on='Barra_Para', right_on='Numero_Barra_Para', how='left')
        df_DCIR_18 = df_DCIR_18.drop(['Numero_Barra_De', 'Numero_Barra_Para'], axis=1)
        df_DCIR_18 = df_DCIR_18[["Barra_De","Barra_Para","Nome_Barra_De","Nome_Barra_Para","Num_Circuito","Tipo_Circuito","N_Unidades_Total","N_Unidades_Operando"]]
        df_DCIR_18 = df_DCIR_18.sort_values(by="Tipo_Circuito")
        dic_results["df_DCIR_18"] = df_DCIR_18

        # Verificações do DEOL adicionais - Vmax diferente de vazio
        df_DEOL_19_1 = (dic_ANA["DEOL"]).copy()
        df_DEOL_19_1 = df_DEOL_19_1[["Numero_Barra","Tensao_Maxima_Conexao"]]
        df_DEOL_19_1 = df_DEOL_19_1[df_DEOL_19_1["Tensao_Maxima_Conexao"] != ""]
        dic_results["df_DEOL_19_1"] = df_DEOL_19_1

        #  FP Pre Falta diferente de vazio
        df_DEOL_19_2 = (dic_ANA["DEOL"]).copy()
        df_DEOL_19_2 = df_DEOL_19_2[["Numero_Barra","FP_pre_falta"]]
        df_DEOL_19_2 = df_DEOL_19_2[df_DEOL_19_2["FP_pre_falta"] != ""]
        dic_results["df_DEOL_19_2"] = df_DEOL_19_2

        #  FP CC diferente de 0.1
        df_DEOL_19_3 = (dic_ANA["DEOL"]).copy()
        df_DEOL_19_3 = df_DEOL_19_3[["Numero_Barra","FP_curto_circuito"]]
        df_DEOL_19_3 = df_DEOL_19_3[df_DEOL_19_3["FP_curto_circuito"] != "0.1"]
        dic_results["df_DEOL_19_3"] = df_DEOL_19_3

        #  K diferente de 1
        df_DEOL_19_4 = (dic_ANA["DEOL"]).copy()
        df_DEOL_19_4 = df_DEOL_19_4[["Numero_Barra","K"]]
        df_DEOL_19_4 = df_DEOL_19_4[df_DEOL_19_4["K"] != "1"]
        dic_results["df_DEOL_19_4"] = df_DEOL_19_4

        # Valor da base de tensão superior a 765 kV
        df_DBAR_17 = (dic_ANA["DBAR"]).copy()
        df_DBAR_17['Tensao_base'] = pd.to_numeric(df_DBAR_17['Tensao_base'], errors='coerce')
        df_DBAR_17 = df_DBAR_17[df_DBAR_17["Tensao_base"] > 765]
        dic_results["df_DBAR_17"] = df_DBAR_17

        # Nome da Barra fora de padrão
        df_DBAR_18 = (dic_ANA["DBAR"]).copy()
        df_DBAR_18['Numero'] = pd.to_numeric(df_DBAR_18['Numero'], errors='coerce')
        # Filtrar o DataFrame com condições combinadas
        df_DBAR_18 = df_DBAR_18[
            (df_DBAR_18['Nome'].str.len() != 12) & 
            (df_DBAR_18['Numero'] < 70000)
        ]
        # df_DBAR_18 = df_DBAR_18[(df_DBAR_18['Nome'].str.len() != 12) & (df_DBAR_18[df_DBAR_18['Numero'] < 70000])]
        dic_results["df_DBAR_18"] = df_DBAR_18

        # Comprimento (km) acima de 500 km
        df_DCIR_19 = (dic_ANA["DCIR"]).copy()
        df_DCIR_19['Comprimento'] = pd.to_numeric(df_DCIR_19['Comprimento'].str.replace(',', '.'), errors='coerce')
        df_DCIR_19 = df_DCIR_19[df_DCIR_19["Tipo_Circuito"] == "L"]
        df_DCIR_19 = df_DCIR_19[df_DCIR_19["Comprimento"]>500]
        df_DCIR_19 = df_DCIR_19.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_De'), left_on='Barra_De', right_on='Numero_Barra_De', how='left')
        df_DCIR_19 = df_DCIR_19.merge(((dic_ANA["DBAR"]).copy())[["Numero", "Nome"]].add_suffix('_Barra_Para'), left_on='Barra_Para', right_on='Numero_Barra_Para', how='left')
        df_DCIR_19 = df_DCIR_19.drop(['Numero_Barra_De', 'Numero_Barra_Para'], axis=1)
        df_DCIR_19 = df_DCIR_19[["Barra_De","Barra_Para","Nome_Barra_De","Nome_Barra_Para","Num_Circuito","Tipo_Circuito","Comprimento"]]
        df_DCIR_19 = df_DCIR_19.sort_values(by="Comprimento")
        dic_results["df_DCIR_19"] = df_DCIR_19

        return dic_results

    def analise_cc_only_ilha(self, path_exe_anafas, path_caso_anafas, dic_results):
        # CHECK 1.5 - Ilhas Topológicas;
        path_anafas_folder = path_exe_anafas[:path_exe_anafas.rfind("/")+1]
        inp_file = path_anafas_folder + "inp_relatorio_ilhas.INP"
        list_inp = []
        relatorio_saida = path_anafas_folder + "relatorio_ilhas.txt"

        list_inp.append("(=================================================================================")
        list_inp.append("(=                    GERA RELATÓRIO RILH                                        =")
        list_inp.append("(=================================================================================")
        list_inp.append("ARQV DADO")
        list_inp.append(path_caso_anafas)
        list_inp.append("ARQV SAID")
        list_inp.append(relatorio_saida)
        list_inp.append("RELA RILH")
        list_inp.append("FIM")

        # Escrevendo arquivo INP
        with open(inp_file, 'w') as f:
            f.write("\n".join(list_inp))

        # Aplica deck
        self.__run_INP(path_exe_anafas, inp_file)

        # Processa deck
        with open(relatorio_saida, 'r') as f:
            rel_lines = f.readlines()

        # Inicia obtenção dos dados
        list_dic_dados = []
        list_barras = []
        dic_dados = {}
        save_deck = False
        for index, row in enumerate(rel_lines):
            if row[:9] ==  " ILHA No.":
                if save_deck:
                    dic_dados["barras"] = "\n".join(list_barras)
                    list_dic_dados.append(dic_dados)
                    dic_dados = {}
                    list_barras = []

                dic_dados["numero_ilha"] = row[9:12].strip()
                dic_dados["numero_barras"] = row[16:20].strip()
                dic_dados["ref_seqP"] = row[29:32].strip()
                dic_dados["ref_seqZ"] = row[55:58].strip()
                save_deck = True

            elif save_deck:
                if row.strip() != "":
                    list_barras.append(row.strip())
        dic_results["df_ILHA"] = pd.DataFrame(list_dic_dados)

        return dic_results

    def __make_estado_global(self, Estado, Estado_De, Estado_Para):
        Estado_Global = "L" if ((Estado == "") and (Estado_De == "") and (Estado_Para == "")) else "D"
        return Estado_Global


    def analise_cc_flow(self, dic_ANA, dic_PWF, dic_results):
        # # Unindo os códigos DBAR
        # df_DBAR_PWF = (dic_PWF["DBAR"]).copy()
        # df_DBAR_ANA = (dic_ANA["DBAR"]).copy()

        # list_columns = ["Numero", "Nome", "Area"]
        # df_DBAR_PWF = df_DBAR_PWF[list_columns]
        # df_DBAR_ANA = df_DBAR_ANA[list_columns]

        # df_DBAR_PWF['Prefixo_Nome'] = df_DBAR_PWF['Nome'].str.slice(0, 9)
        # df_DBAR_ANA['Prefixo_Nome'] = df_DBAR_ANA['Nome'].str.slice(0, 9)
        # df_DBAR_PWF['Tipo_Nome'] = df_DBAR_PWF['Nome'].str.slice(6, 9)
        # df_DBAR_ANA['Tipo_Nome'] = df_DBAR_ANA['Nome'].str.slice(6, 9)
        # df_DBAR_PWF['Tensao_Nome'] = df_DBAR_PWF['Nome'].str.slice(9, 12)
        # df_DBAR_ANA['Tensao_Nome'] = df_DBAR_ANA['Nome'].str.slice(9, 12)

        # df_DBAR_Unido = pd.merge(df_DBAR_ANA, df_DBAR_PWF, on='Numero', how='outer', suffixes=('_ANF', '_ANR'))

        # # CHECK 2.1 - Nomes de Barras diferentes entre Anafas e Anarede;
        # df_DBAR_21 = df_DBAR_Unido.copy()
        # condicao = ~df_DBAR_21['Nome_ANR'].isnull() & ~df_DBAR_21['Nome_ANF'].isnull()
        # df_DBAR_21 = df_DBAR_21[condicao]
        # # Checando condição
        # df_DBAR_21['Nome_Diferencas'] = df_DBAR_21['Prefixo_Nome_ANR'] != df_DBAR_21['Prefixo_Nome_ANF']
        # df_DBAR_21 = df_DBAR_21[df_DBAR_21["Nome_Diferencas"] == True]
        # df_DBAR_21 = df_DBAR_21[["Numero", "Nome_ANR", "Nome_ANF"]]
        # dic_results["df_DBAR_21"] = df_DBAR_21

        # # CHECK 2.2 - Número de Área diferente entre Anafas e Anarede;
        # df_DBAR_22 = df_DBAR_Unido.copy()
        # condicao = ~df_DBAR_22['Area_ANR'].isnull() & ~df_DBAR_22['Area_ANF'].isnull()
        # df_DBAR_22 = df_DBAR_22[condicao]
        # # Checando condição
        # df_DBAR_22['Area_Diferencas'] = df_DBAR_22['Area_ANR'] != df_DBAR_22['Area_ANF']
        # df_DBAR_22 = df_DBAR_22[df_DBAR_22["Area_Diferencas"] == True]
        # df_DBAR_22 = df_DBAR_22[["Numero", "Nome_ANR", "Nome_ANF", "Area_ANR", "Area_ANF"]]
        # dic_results["df_DBAR_22"] = df_DBAR_22

        # # CHECK 2.3 - Barras de 1 a 70.000 que existem no Anafas, mas não no Anarede
        # df_23_bruto = df_DBAR_Unido.copy()
        # df_23_bruto = df_23_bruto[df_23_bruto["Numero"] <= 70000]
        # df_23_bruto = df_23_bruto[df_23_bruto["Nome_ANR"].isnull()]
        # # Removendo tipo usinas
        # condicao = ["UNE", "UHE", "SIN", "UTE", "UFV", "BIO", "PCH", "EOL"]
        # df_DBAR_23 = df_23_bruto[~df_23_bruto['Tipo_Nome_ANF'].isin(condicao)]

        # df_DBAR_23 = df_DBAR_23[['Numero','Nome_ANF','Area_ANF','Prefixo_Nome_ANF','Tipo_Nome_ANF','Tensao_Nome_ANF',]]
        # dic_results["df_DBAR_23"] = df_DBAR_23

        # PREPARA DADOS ANAREDE
        df_dbar = pd.DataFrame()
        df_dlin = pd.DataFrame()

        for key, dic_temp in dic_PWF.items():
            df_dbar_temp = dic_temp["DBAR"][["Numero","Nome","Estado"]].replace("","L")
            df_dlin_temp = dic_temp["DLIN"][["Barra_De","Barra_Para","Num_Circuito","Estado_De","Estado_Para","Estado"]]

            if len(df_dbar) == 0:
                df_dbar = df_dbar_temp
                # Ajuste de estado para DLIN
                df_dlin_temp["Estado_Global"] = np.vectorize(self.__make_estado_global)(df_dlin_temp["Estado"], df_dlin_temp["Estado_De"], df_dlin_temp["Estado_Para"])
                df_dlin = df_dlin_temp.drop(["Estado","Estado_De","Estado_Para"],axis=1)
                #
                # Acerto de nomes
                df_dbar.columns = df_dbar.columns[:-1].tolist() + [key]
                df_dlin.columns = df_dlin.columns[:-1].tolist() + [key]

            else:
                # Ajuste DLIN
                df_dlin_temp["Estado_Global"] = np.vectorize(self.__make_estado_global)(df_dlin_temp["Estado"], df_dlin_temp["Estado_De"], df_dlin_temp["Estado_Para"])
                df_dlin_temp = df_dlin_temp.drop(["Estado","Estado_De","Estado_Para"],axis=1)
                # Merge
                df_dbar = pd.merge(df_dbar, df_dbar_temp, how="outer")
                df_dlin = pd.merge(df_dlin, df_dlin_temp, how="outer")
                # Acerto de nomes
                df_dbar.columns = df_dbar.columns[:-1].tolist() + [key]
                df_dlin.columns = df_dlin.columns[:-1].tolist() + [key]
        # Verifica estados de todos
        df_dbar['Estado'] = np.where(df_dbar.iloc[:, 2:].eq('L').any(axis=1), 'L', 'D')
        df_dlin['Estado'] = np.where(df_dlin.iloc[:, 3:].eq('L').any(axis=1), 'L', 'D')
        # Acerta dataframe
        df_dbar.drop(df_dbar.columns[2:-1], axis=1, inplace=True)
        df_dlin.drop(df_dlin.columns[3:-1], axis=1, inplace=True)

        # CHECK 2.4 - ELEMENTOS COM ESTADOS OPERATIVOS DIFERENTES NO ANAREDE E ANAFAS - DBAR
        df_DBAR_PWF = (df_dbar).copy()
        df_DBAR_ANA = (dic_ANA["DBAR"]).copy()

        list_columns = ["Numero", "Nome", "Estado"]
        df_DBAR_PWF = df_DBAR_PWF[list_columns]
        df_DBAR_ANA = df_DBAR_ANA[list_columns]
        df_DBAR_ANA['Estado'] = df_DBAR_ANA['Estado'].replace({"": "L", "d": "D"})

        # Fazendo o merge dos dois dataframes na coluna 'Numero'
        df_DBAR_merged = pd.merge(df_DBAR_PWF, df_DBAR_ANA, on='Numero', suffixes=('_PWF', '_ANA'))
        df_DBAR_merged = df_DBAR_merged[df_DBAR_merged['Estado_PWF'] != df_DBAR_merged['Estado_ANA']]
        df_DBAR_merged = df_DBAR_merged[["Numero", "Nome_ANA", "Nome_PWF", "Estado_ANA", "Estado_PWF"]]
        df_DBAR_merged['Região'] = df_DBAR_merged['Nome_ANA'].apply(lambda s: s[-6:-3] if isinstance(s, str) else '')
        df_DBAR_merged = df_DBAR_merged.sort_values(by=['Estado_ANA', 'Região', 'Nome_ANA'])

        dic_results["df_DBAR_21"] = df_DBAR_merged

        # CHECK 2.5 - ELEMENTOS COM ESTADOS OPERATIVOS DIFERENTES NO ANAREDE E ANAFAS - DLIN/DCIR
        df_DLIN = (df_dlin).copy()
        df_DCIR = (dic_ANA["DCIR"]).copy()
        list_columns_DCIR = ["Barra_De", "Barra_Para", "Num_Circuito", "Estado"]
        # list_columns_DLIN = list_columns_DCIR + ["Estado_De", "Estado_Para"]

        df_DLIN = df_DLIN[list_columns_DCIR]
        list_columns_DCIR.append("Tipo_Circuito")
        df_DCIR = df_DCIR[list_columns_DCIR]
        df_DCIR['Estado'] = df_DCIR['Estado'].replace({"": "L", "d": "D"})
        # df_DLIN["Estado_Global"] = np.vectorize(self.__make_estado_global)(df_DLIN["Estado"], df_DLIN["Estado_De"], df_DLIN["Estado_Para"])

        # Fazendo o merge dos dois dataframes na coluna 'Numero'
        df_DLIN_merged = pd.merge(df_DLIN[['Barra_De', 'Barra_Para', 'Num_Circuito', 'Estado']],
                                df_DCIR[['Barra_De', 'Barra_Para', 'Num_Circuito', 'Estado','Tipo_Circuito']],
                                on=['Barra_De', 'Barra_Para', 'Num_Circuito'],
                                suffixes=('_ANR', '_ANF'))
        df_DLIN_merged = df_DLIN_merged[df_DLIN_merged['Estado_ANR'] != df_DLIN_merged['Estado_ANF']]
        # Criando o dicionário de mapeamento
        mapa_nomes = df_DBAR_ANA.set_index('Numero')['Nome'].to_dict()
        # Mapeando os nomes para as colunas 'Barra_De' e 'Barra_Para'
        df_DLIN_merged['Nome_Barra_De'] = df_DLIN_merged['Barra_De'].map(mapa_nomes)
        df_DLIN_merged['Nome_Barra_Para'] = df_DLIN_merged['Barra_Para'].map(mapa_nomes)
        cols_order = ['Barra_De', 'Barra_Para', 'Num_Circuito', 'Tipo_Circuito', 'Nome_Barra_De', 'Nome_Barra_Para','Estado_ANR', 'Estado_ANF']
        df_DLIN_merged = df_DLIN_merged[cols_order]
        df_DLIN_merged = df_DLIN_merged.rename(columns={'Estado_ANR': 'Estado_PWF', 'Estado_ANF': 'Estado_ANA'})
        df_DLIN_merged['Estado_PWF'] = df_DLIN_merged['Estado_PWF'].replace({"": "L"})
        df_DLIN_merged['Estado_ANA'] = df_DLIN_merged['Estado_ANA'].replace({"": "L"})
        #
        df_DLIN_merged['Região'] = df_DLIN_merged.apply(
            lambda row: f"{row['Nome_Barra_De'][-6:-3] if isinstance(row['Nome_Barra_De'], str) else ''}/{row['Nome_Barra_Para'][-6:-3] if isinstance(row['Nome_Barra_Para'], str) else ''}",
            axis=1
        )
        df_DLIN_merged = df_DLIN_merged.sort_values(by=['Estado_ANA', 'Região'])

        dic_results["df_DBAR_22"] = df_DLIN_merged

        # df_DBAR_PWF = (dic_PWF["DBAR"]).copy()
        # df_DBAR_ANA = (dic_ANA["DBAR"]).copy()

        # list_columns = ["Numero", "Nome", "Estado"]
        # df_DBAR_PWF = df_DBAR_PWF[list_columns]
        # df_DBAR_ANA = df_DBAR_ANA[list_columns]
        # df_DBAR_ANA['Estado'] = df_DBAR_ANA['Estado'].replace({"": "L", "d": "D"})

        # # Fazendo o merge dos dois dataframes na coluna 'Numero'
        # df_DBAR_merged = pd.merge(df_DBAR_PWF, df_DBAR_ANA, on='Numero', suffixes=('_PWF', '_ANA'))
        # df_DBAR_merged = df_DBAR_merged[df_DBAR_merged['Estado_PWF'] != df_DBAR_merged['Estado_ANA']]
        # df_DBAR_merged = df_DBAR_merged[["Numero", "Nome_ANA", "Nome_PWF", "Estado_ANA", "Estado_PWF"]]
        # df_DBAR_merged = df_DBAR_merged.sort_values(by=['Estado_ANA', 'Nome_ANA'])

        # dic_results["df_DBAR_24"] = df_DBAR_merged

        # # CHECK 2.5 - ELEMENTOS COM ESTADOS OPERATIVOS DIFERENTES NO ANAREDE E ANAFAS - DLIN/DCIR
        # df_DLIN = (dic_PWF["DLIN"]).copy()
        # df_DCIR = (dic_ANA["DCIR"]).copy()
        # list_columns_DCIR = ["Barra_De", "Barra_Para", "Num_Circuito", "Estado"]
        # list_columns_DLIN = list_columns_DCIR + ["Estado_De", "Estado_Para"]

        # df_DLIN = df_DLIN[list_columns_DLIN]
        # df_DCIR = df_DCIR[list_columns_DCIR]
        # df_DLIN["Estado_Global"] = np.vectorize(self.__make_estado_global)(df_DLIN["Estado"], df_DLIN["Estado_De"], df_DLIN["Estado_Para"])

        # # Fazendo o merge dos dois dataframes na coluna 'Numero'
        # df_DLIN_merged = pd.merge(df_DLIN[['Barra_De', 'Barra_Para', 'Num_Circuito', 'Estado_Global']],
        #                         df_DCIR[['Barra_De', 'Barra_Para', 'Num_Circuito', 'Estado']],
        #                         on=['Barra_De', 'Barra_Para', 'Num_Circuito'],
        #                         suffixes=('_DLIN', '_DCIR'))
        # df_DLIN_merged = df_DLIN_merged[df_DLIN_merged['Estado_Global'] != df_DLIN_merged['Estado']]
        # # Criando o dicionário de mapeamento
        # mapa_nomes = df_DBAR_ANA.set_index('Numero')['Nome'].to_dict()
        # # Mapeando os nomes para as colunas 'Barra_De' e 'Barra_Para'
        # df_DLIN_merged['Nome_Barra_De'] = df_DLIN_merged['Barra_De'].map(mapa_nomes)
        # df_DLIN_merged['Nome_Barra_Para'] = df_DLIN_merged['Barra_Para'].map(mapa_nomes)
        # cols_order = ['Nome_Barra_De', 'Nome_Barra_Para', 'Barra_De', 'Barra_Para', 'Num_Circuito', 'Estado', 'Estado_Global']
        # df_DLIN_merged = df_DLIN_merged[cols_order]
        # df_DLIN_merged = df_DLIN_merged.rename(columns={'Estado_Global': 'Estado_PWF', 'Estado': 'Estado_ANA'})
        # df_DLIN_merged['Estado_PWF'] = df_DLIN_merged['Estado_PWF'].replace({"": "L"})
        # df_DLIN_merged['Estado_ANA'] = df_DLIN_merged['Estado_ANA'].replace({"": "L"})
        # df_DLIN_merged = df_DLIN_merged.sort_values(by='Estado_ANA')

        # dic_results["df_DBAR_25"] = df_DLIN_merged

        return dic_results

    def analise_cc_siger(self, dic_ANA, oSIGER, dic_results, data_horizonte_siger):
        df_SIGER_Barras = oSIGER.get_barra()

        # Ajustando meu df barras para representar o caso no meu horizonte
        # data_horizonte = "31/12/2023"
        data_filtro = pd.to_datetime(data_horizonte_siger, format="%d/%m/%Y")
        df_SIGER_Barras['Data de Entrada'] = pd.to_datetime(df_SIGER_Barras['Data de Entrada'])
        df_SIGER_Barras['Data de Saída'] = pd.to_datetime(df_SIGER_Barras['Data de Saída'])
        df_SIGER_Barras = df_SIGER_Barras[(df_SIGER_Barras['Data de Entrada'] <= data_filtro)]
        df_SIGER_Barras = df_SIGER_Barras[~(df_SIGER_Barras['Data de Saída'] <= data_filtro)]

        # Agrupando ANAFAS x SIGER
        df_DBAR_ANF = (dic_ANA["DBAR"]).copy()
        df_DBAR_SIG = (df_SIGER_Barras).copy()

        ajuste_nomes = {'Número': 'Numero', 'Área': 'Area'}
        df_DBAR_SIG = df_DBAR_SIG.rename(columns=ajuste_nomes)
        list_columns = ["Numero", "Nome", "Area"]
        df_DBAR_ANF = df_DBAR_ANF[list_columns]
        df_DBAR_SIG = df_DBAR_SIG[list_columns]
        data_types = {"Numero": int, "Nome": str, "Area": str}
        df_DBAR_ANF = df_DBAR_ANF.astype(data_types)
        df_DBAR_SIG = df_DBAR_SIG.astype(data_types)

        df_DBAR_SIG['Prefixo_Nome'] = df_DBAR_SIG['Nome'].str.slice(0, 9)
        df_DBAR_ANF['Prefixo_Nome'] = df_DBAR_ANF['Nome'].str.slice(0, 9)
        df_DBAR_SIG['Tipo_Nome'] = df_DBAR_SIG['Nome'].str.slice(6, 9)
        df_DBAR_ANF['Tipo_Nome'] = df_DBAR_ANF['Nome'].str.slice(6, 9)
        df_DBAR_SIG['Tensao_Nome'] = df_DBAR_SIG['Nome'].str.slice(9, 12)
        df_DBAR_ANF['Tensao_Nome'] = df_DBAR_ANF['Nome'].str.slice(9, 12)

        df_DBAR_Unido = pd.merge(df_DBAR_ANF, df_DBAR_SIG, on='Numero', how='outer', suffixes=('_ANF', '_SIG'))

        # CHECK 3.1 - Nomes de Barras diferentes entre Anafas e SIGER;
        df_DBAR_31 = df_DBAR_Unido.copy()
        condicao = ~df_DBAR_31['Nome_ANF'].isnull() & ~df_DBAR_31['Nome_SIG'].isnull()
        df_DBAR_31 = df_DBAR_31[condicao]
        # Checando condição
        df_DBAR_31['Nome_Diferencas'] = df_DBAR_31['Prefixo_Nome_ANF'] != df_DBAR_31['Prefixo_Nome_SIG']
        df_DBAR_31 = df_DBAR_31[df_DBAR_31["Nome_Diferencas"] == True]
        df_DBAR_31 = df_DBAR_31[["Numero", "Nome_ANF", "Nome_SIG"]]
        df_DBAR_31 = df_DBAR_31.sort_values(by='Nome_ANF')
        dic_results["df_DBAR_31"] = df_DBAR_31

        # CHECK 3.2 - Número de Área diferente entre Anafas e SIGER;
        df_DBAR_32 = df_DBAR_Unido.copy()
        condicao = ~df_DBAR_32['Area_ANF'].isnull() & ~df_DBAR_32['Area_SIG'].isnull()
        df_DBAR_32 = df_DBAR_32[condicao]
        # Checando condição
        df_DBAR_32['Area_Diferencas'] = df_DBAR_32['Area_ANF'] != df_DBAR_32['Area_SIG']
        df_DBAR_32 = df_DBAR_32[df_DBAR_32["Area_Diferencas"] == True]
        df_DBAR_32 = df_DBAR_32[["Numero", "Nome_ANF", "Nome_SIG", "Area_ANF", "Area_SIG"]]
        df_DBAR_32 = df_DBAR_32.sort_values(by='Nome_ANF')
        dic_results["df_DBAR_32"] = df_DBAR_32

        # CHECK 3.3 - Barras de 1 a 70.000 que existem no Anafas, mas não no SIGER para regiões unificadas
        df_33_bruto = df_DBAR_Unido.copy()
        df_33_bruto = df_33_bruto[df_33_bruto["Numero"] <= 70000]
        df_33_bruto = df_33_bruto[df_33_bruto["Nome_SIG"].isnull()]
        # Removendo tipo usinas
        condicao = ["UNE", "UHE", "SIN", "UTE", "UFV", "BIO", "PCH", "EOL"]
        df_33_bruto = df_33_bruto[~df_33_bruto['Tipo_Nome_ANF'].isin(condicao)]

        estados_unificados = ["-MS", "-PR", "-SC", "-RS"]
        df_33_bruto = df_33_bruto[df_33_bruto['Tipo_Nome_ANF'].isin(estados_unificados)]
        df_33_bruto = df_33_bruto[['Numero','Nome_ANF','Area_ANF','Prefixo_Nome_ANF','Tipo_Nome_ANF','Tensao_Nome_ANF',]]
        df_33_bruto = df_33_bruto.sort_values(by=['Tipo_Nome_ANF','Nome_ANF'])
        dic_results["df_DBAR_33"] = df_33_bruto

        return dic_results

    def check_base_cc(self, oDeck, arquivo_anafas, arquivo_anarede="", analise_cc_only=True, analise_cc_flow=False, analise_cc_siger=False, oSIGER=""):
        ## Reforçando as seguintes conferências devem ser implementadas:
        # Análise CC
            # Barras acima de 70.000 cuja área não é 998;
            # Barras de 1 a 70.000 que estão com área 998;
            # Barras acima de 90.000;
            # Área diferente de 998 para os códigos: DCIR / DMUT / DEOL / DSHL
            # Verifica Ilhas Topológicas no caso

        # Análise CC + Flow
            # Nomes de Barras diferentes entre Anafas e Anarede;
            # Número de Área diferente entre Anafas e Anarede;
            # Barras de 1 a 70.000 que existem no Anafas, mas não no Anarede;

        # Análise CC + SIGER
            # Nomes de Barras diferentes entre Anafas e SIGER;
            # Número de Área diferente entre Anafas e SIGER;
        # Puxando decks para memória
        dic_ANA = oDeck.get_df_ANA(arquivo_anafas)
        dic_PWF = oDeck.get_df_PWF(arquivo_anarede)
        dic_results = {}

        # Análise exclusiva CC
        if analise_cc_only:
            dic_results = self.analise_cc_only(dic_ANA, dic_results)

        # Análise conjunta CC + Caso Anarede
        if analise_cc_flow:
            dic_results = self.analise_cc_flow(dic_ANA, dic_PWF, dic_results, region=[])

        if analise_cc_siger:
            dic_results = self.analise_cc_siger(dic_ANA, oSIGER, dic_results)

        return dic_results

if __name__ == "__main__":
    import sys
    sys.path.append(r'C:\Users\natha\OneDrive - Operador Nacional do Sistema Eletrico\_Home Office ONS\Ferramentas - Programação\GitHub\Codigos-Python-ONS\01_Biblioteca_CEPEL\cepel_tools')
    import siger, decks
    import pandas as pd

    # Inicializa instância do objeto
    oBaseCC = BaseCC()
    oDeck = decks.DECKS()

    # Inicializo o SIGER
    url = r"https://siger.cepel.br/"
    user = "admin@cepel.br"
    password = "Dre@123456"
    oSIGER = siger.SIGER(url, user, password)

    # Funções disponíveis
    func_01_PAR_init = False
    func_02_PAR_compSIGER = False
    func_03_PAR_applyDecks = False
    func_04_PAR_confere = True

    #==========================================================================
    # FUNÇÃO 01 - MANIPULAÇÃO E CRIAÇÃO DA PASTA DO CICLO DO PAR
    if func_01_PAR_init:
        path_PAR = r"C:\_APAGAR\_BaseCC\func01"
        download_missing_decks = True
        # Realizando as operações para gerar os decks do próximo PAR
        oBaseCC.gera_estrutura_PAR(path_PAR, oSIGER, download_missing_decks)

    #==========================================================================
    # FUNÇÃO 02 - COMPARAR DECKS COM SIGER
    if func_02_PAR_compSIGER:
        caso_base = r"C:\_APAGAR\_BaseCC\func02\01_BR2303A.ANA"
        filters_path = r"C:\_APAGAR\_BaseCC\func02\_SUL_SIGER_FiltroComparacao_sem DITDIS.txt"
        data_final = "31/03/2023"
        chromedriver_path = r"C:\_APAGAR\_Chromedriver\chromedriver.exe"
        path_download = caso_base[:caso_base.rfind("\\")] + r"\downloads_siger"
        suffix = "SUL_23"

        # Passo 1 - Compara arquivo .ANA com SIGER e baixa a comparação para a pasta de download acima
        oSIGER.comparar_deck_siger(chromedriver_path, caso_base, filters_path, data_final, path_download)

        # Passo 2 - Extrair comparação do ANAFAS e abrir o .ALT resultante
        oBaseCC.extract_comp_siger(path_download, suffix)

    #==========================================================================
    # FUNÇÃO 03 - APLICAR DECKS DO PAR
    if func_03_PAR_applyDecks:
        caso_base = r"C:\_APAGAR\_BaseCC\func03\BR2303A.ANA"
        list_decks = [r"C:\_APAGAR\_BaseCC\func03\1_SUL03B_4.alt",
                    r"C:\_APAGAR\_BaseCC\func03\2_SUL2312PG_V4.ALT",
                    r"C:\_APAGAR\_BaseCC\func03\3_SUL2412PG_V2.ALT",
                    r"C:\_APAGAR\_BaseCC\func03\4_SUL2512PG_V2.ALT",
                    r"C:\_APAGAR\_BaseCC\func03\5_SUL2612PG_V2.ALT",
                    r"C:\_APAGAR\_BaseCC\func03\6_SUL2712PG_V2.ALT",
                    r"C:\_APAGAR\_BaseCC\func03\7_SUL2812PG_V2.ALT",]
        anafas_dir = r"C:\CEPEL\Anafas\7.6.2\Anafas.exe"

        oBaseCC.aplica_decks(anafas_dir, caso_base, list_decks)

    #==========================================================================
    # FUNÇÃO 04 - CONFERÊNCIA ARQUIVO CC
    if func_04_PAR_confere:
        # Entradas e Saída
        arquivo_anafas =  r"C:\_APAGAR\_BaseCC\func04\BR2303B_SUL06A.ANA"
        arquivo_anarede = r"C:\_APAGAR\_BaseCC\func04\CART.PWF"
        analise_cc_only, analise_cc_flow, analise_cc_siger = True, True, True

        # Obtendo dicionário com dataframes e análises realizadas
        dic_confere_cc = oBaseCC.check_base_cc(oDeck, arquivo_anafas, arquivo_anarede, analise_cc_only, analise_cc_flow, analise_cc_siger, oSIGER)

    #==========================================================================
    pass