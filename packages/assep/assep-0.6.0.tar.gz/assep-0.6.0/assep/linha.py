class Linha:
    # Inicializa a representação dos dados de uma barra
    def __init__(self):
        # Coleto apenas os dicionários com os delimitadores de campo
        self.dicInfo_LinhaAnarede = self.__create_dicInfo_LinhaAnarede()
        self.dicInfo_LinhaAnafas = self.__create_dicInfo_LinhaAnafas()

    ###================================================================================================================
    ###
    ### CRIAÇÃO DOS DICIONÁRIOS CONTENDO DADOS DE BARRA
    ###
    ###================================================================================================================
    def __create_dicInfo_LinhaAnafas(self):
        dicinfo_linhaAnafas = {}
        #
        dicinfo_linhaAnafas["barra_de"] = (0,5)
        dicinfo_linhaAnafas["codigo_atualizacao"] = (5,6)
        dicinfo_linhaAnafas["estado"] = (6,7)
        dicinfo_linhaAnafas["barra_para"] = (7,12)
        dicinfo_linhaAnafas["num_circuito"] = (14,16)
        dicinfo_linhaAnafas["tipo_circuito"] = (16,17)
        dicinfo_linhaAnafas["resist_pos"] = (17,23)
        dicinfo_linhaAnafas["reat_pos"] = (23,29)
        dicinfo_linhaAnafas["resist_zer"] = (29,35)
        dicinfo_linhaAnafas["reat_zer"] = (35,41)
        dicinfo_linhaAnafas["nome_circuito"] = (41,47)
        dicinfo_linhaAnafas["suscept_pos"] = (47,52)
        dicinfo_linhaAnafas["suscept_zer"] = (52,57)
        dicinfo_linhaAnafas["tap"] = (57,62)
        dicinfo_linhaAnafas["tb"] = (62,67)
        dicinfo_linhaAnafas["tc"] = (67,69)
        dicinfo_linhaAnafas["area"] = (69,72)
        dicinfo_linhaAnafas["defasagem"] = (72,75)
        dicinfo_linhaAnafas["ind_defasagem"] = (75,76)
        dicinfo_linhaAnafas["km"] = (76,80)
        dicinfo_linhaAnafas["conexao_de"] = (80,82)
        dicinfo_linhaAnafas["resist_aterr_de"] = (82,88)
        dicinfo_linhaAnafas["reat_aterr_de"] = (88,94)
        dicinfo_linhaAnafas["conexao_para"] = (94,96)
        dicinfo_linhaAnafas["resist_aterr_para"] = (96,102)
        dicinfo_linhaAnafas["reat_aterr_para"] = (102,108)
        dicinfo_linhaAnafas["sub_area"] = (108,111)
        dicinfo_linhaAnafas["unidades_total"] = (115,118)
        dicinfo_linhaAnafas["unidades_oper"] = (118,121)
        dicinfo_linhaAnafas["capac_dj_de"] = (121,128)
        dicinfo_linhaAnafas["cic_capac_dj_de"] = (128,131)
        dicinfo_linhaAnafas["capac_dj_para"] = (131,137)
        dicinfo_linhaAnafas["cic_capac_dj_para"] = (137,140)
        dicinfo_linhaAnafas["data_entrada"] = (160,168)
        dicinfo_linhaAnafas["data_saida"] = (168,176)
        dicinfo_linhaAnafas["mva"] = (177,182)
        dicinfo_linhaAnafas["td"] = (196,198)
        dicinfo_linhaAnafas["nome_extenso"] = (199,219)
        #
        return dicinfo_linhaAnafas

    def __create_dicInfo_LinhaAnarede(self):
        dicInfo_LinhaAnarede = {}
        #
        dicInfo_LinhaAnarede["barra_de"] = (0,5)
        dicInfo_LinhaAnarede["estado_barra_de"] = (5,6)
        dicInfo_LinhaAnarede["operacao"] = (7,8)
        dicInfo_LinhaAnarede["estado_barra_para"] = (9,10)
        dicInfo_LinhaAnarede["barra_para"] = (10,15)
        dicInfo_LinhaAnarede["num_circuito"] = (15,17)
        dicInfo_LinhaAnarede["estado_circuito"] = (17,18)
        dicInfo_LinhaAnarede["proprietario"] = (18,19)
        dicInfo_LinhaAnarede["tap_manobravel"] = (19,20)
        dicInfo_LinhaAnarede["resist_pos"] = (20,26)
        dicInfo_LinhaAnarede["reat_pos"] = (26,32)
        dicInfo_LinhaAnarede["suscept_pos"] = (32,48)
        dicInfo_LinhaAnarede["tap"] = (38,43)
        dicInfo_LinhaAnarede["tap_minimo"] = (43,48)
        dicInfo_LinhaAnarede["tap_maximo"] = (48,53)
        dicInfo_LinhaAnarede["defasagem"] = (53,58)
        dicInfo_LinhaAnarede["barra_controlada"] = (58,64)
        dicInfo_LinhaAnarede["capac_normal"] = (64,68)
        dicInfo_LinhaAnarede["capac_emerg"] = (68,72)
        dicInfo_LinhaAnarede["numero_taps"] = (72,74)
        dicInfo_LinhaAnarede["capac_equip"] = (74,78)
        #
        return dicInfo_LinhaAnarede

    def __get_dataANR(self):
        # Atribuicao dos valores nos objetos
        dic = {}
        dic["barra_de"] = self.line_code[self.dicInfo_LinhaAnarede["barra_de"][0]:self.dicInfo_LinhaAnarede["barra_de"][1]].strip()
        dic["estado_barra_de"] = self.line_code[self.dicInfo_LinhaAnarede["estado_barra_de"][0]:self.dicInfo_LinhaAnarede["estado_barra_de"][1]].strip()
        dic["operacao"] = self.line_code[self.dicInfo_LinhaAnarede["operacao"][0]:self.dicInfo_LinhaAnarede["operacao"][1]].strip()
        dic["estado_barra_para"] = self.line_code[self.dicInfo_LinhaAnarede["estado_barra_para"][0]:self.dicInfo_LinhaAnarede["estado_barra_para"][1]].strip()
        dic["barra_para"] = self.line_code[self.dicInfo_LinhaAnarede["barra_para"][0]:self.dicInfo_LinhaAnarede["barra_para"][1]].strip()
        dic["num_circuito"] = self.line_code[self.dicInfo_LinhaAnarede["num_circuito"][0]:self.dicInfo_LinhaAnarede["num_circuito"][1]].strip()
        dic["estado_circuito"] = self.line_code[self.dicInfo_LinhaAnarede["estado_circuito"][0]:self.dicInfo_LinhaAnarede["estado_circuito"][1]].strip()
        dic["proprietario"] = self.line_code[self.dicInfo_LinhaAnarede["proprietario"][0]:self.dicInfo_LinhaAnarede["proprietario"][1]].strip()
        dic["tap_manobravel"] = self.line_code[self.dicInfo_LinhaAnarede["tap_manobravel"][0]:self.dicInfo_LinhaAnarede["tap_manobravel"][1]].strip()
        dic["resist_pos"] = self.line_code[self.dicInfo_LinhaAnarede["resist_pos"][0]:self.dicInfo_LinhaAnarede["resist_pos"][1]].strip()
        dic["reat_pos"] = self.line_code[self.dicInfo_LinhaAnarede["reat_pos"][0]:self.dicInfo_LinhaAnarede["reat_pos"][1]].strip()
        dic["suscept_pos"] = self.line_code[self.dicInfo_LinhaAnarede["suscept_pos"][0]:self.dicInfo_LinhaAnarede["suscept_pos"][1]].strip()
        dic["tap"] = self.line_code[self.dicInfo_LinhaAnarede["tap"][0]:self.dicInfo_LinhaAnarede["tap"][1]].strip()
        dic["tap_minimo"] = self.line_code[self.dicInfo_LinhaAnarede["tap_minimo"][0]:self.dicInfo_LinhaAnarede["tap_minimo"][1]].strip()
        dic["tap_maximo"] = self.line_code[self.dicInfo_LinhaAnarede["tap_maximo"][0]:self.dicInfo_LinhaAnarede["tap_maximo"][1]].strip()
        dic["defasagem"] = self.line_code[self.dicInfo_LinhaAnarede["defasagem"][0]:self.dicInfo_LinhaAnarede["defasagem"][1]].strip()
        dic["barra_controlada"] = self.line_code[self.dicInfo_LinhaAnarede["barra_controlada"][0]:self.dicInfo_LinhaAnarede["barra_controlada"][1]].strip()
        dic["capac_normal"] = self.line_code[self.dicInfo_LinhaAnarede["capac_normal"][0]:self.dicInfo_LinhaAnarede["capac_normal"][1]].strip()
        dic["capac_emerg"] = self.line_code[self.dicInfo_LinhaAnarede["capac_emerg"][0]:self.dicInfo_LinhaAnarede["capac_emerg"][1]].strip()
        dic["numero_taps"] = self.line_code[self.dicInfo_LinhaAnarede["numero_taps"][0]:self.dicInfo_LinhaAnarede["numero_taps"][1]].strip()
        dic["capac_equip"] = self.line_code[self.dicInfo_LinhaAnarede["capac_equip"][0]:self.dicInfo_LinhaAnarede["capac_equip"][1]].strip()

        return dic

    def __get_dataANF(self):
        # Atribuicao dos valores nos objetos
        dic = {}
        dic["barra_de"] = self.line_code[self.dicInfo_LinhaAnafas["barra_de"][0]:self.dicInfo_LinhaAnafas["barra_de"][1]].strip()
        dic["codigo_atualizacao"] = self.line_code[self.dicInfo_LinhaAnafas["codigo_atualizacao"][0]:self.dicInfo_LinhaAnafas["codigo_atualizacao"][1]].strip()
        dic["estado"] = self.line_code[self.dicInfo_LinhaAnafas["estado"][0]:self.dicInfo_LinhaAnafas["estado"][1]].strip()
        dic["barra_para"] = self.line_code[self.dicInfo_LinhaAnafas["barra_para"][0]:self.dicInfo_LinhaAnafas["barra_para"][1]].strip()
        dic["num_circuito"] = self.line_code[self.dicInfo_LinhaAnafas["num_circuito"][0]:self.dicInfo_LinhaAnafas["num_circuito"][1]].strip()
        dic["tipo_circuito"] = self.line_code[self.dicInfo_LinhaAnafas["tipo_circuito"][0]:self.dicInfo_LinhaAnafas["tipo_circuito"][1]].strip()
        dic["resist_pos"] = self.line_code[self.dicInfo_LinhaAnafas["resist_pos"][0]:self.dicInfo_LinhaAnafas["resist_pos"][1]].strip()
        dic["reat_pos"] = self.line_code[self.dicInfo_LinhaAnafas["reat_pos"][0]:self.dicInfo_LinhaAnafas["reat_pos"][1]].strip()
        dic["resist_zer"] = self.line_code[self.dicInfo_LinhaAnafas["resist_zer"][0]:self.dicInfo_LinhaAnafas["resist_zer"][1]].strip()
        dic["reat_zer"] = self.line_code[self.dicInfo_LinhaAnafas["reat_zer"][0]:self.dicInfo_LinhaAnafas["reat_zer"][1]].strip()
        dic["nome_circuito"] = self.line_code[self.dicInfo_LinhaAnafas["nome_circuito"][0]:self.dicInfo_LinhaAnafas["nome_circuito"][1]].strip()
        dic["suscept_pos"] = self.line_code[self.dicInfo_LinhaAnafas["suscept_pos"][0]:self.dicInfo_LinhaAnafas["suscept_pos"][1]].strip()
        dic["suscept_zer"] = self.line_code[self.dicInfo_LinhaAnafas["suscept_zer"][0]:self.dicInfo_LinhaAnafas["suscept_zer"][1]].strip()
        dic["tap"] = self.line_code[self.dicInfo_LinhaAnafas["tap"][0]:self.dicInfo_LinhaAnafas["tap"][1]].strip()
        dic["tb"] = self.line_code[self.dicInfo_LinhaAnafas["tb"][0]:self.dicInfo_LinhaAnafas["tb"][1]].strip()
        dic["tc"] = self.line_code[self.dicInfo_LinhaAnafas["tc"][0]:self.dicInfo_LinhaAnafas["tc"][1]].strip()
        dic["area"] = self.line_code[self.dicInfo_LinhaAnafas["area"][0]:self.dicInfo_LinhaAnafas["area"][1]].strip()
        dic["defasagem"] = self.line_code[self.dicInfo_LinhaAnafas["defasagem"][0]:self.dicInfo_LinhaAnafas["defasagem"][1]].strip()
        dic["ind_defasagem"] = self.line_code[self.dicInfo_LinhaAnafas["ind_defasagem"][0]:self.dicInfo_LinhaAnafas["ind_defasagem"][1]].strip()
        dic["km"] = self.line_code[self.dicInfo_LinhaAnafas["km"][0]:self.dicInfo_LinhaAnafas["km"][1]].strip()
        dic["conexao_de"] = self.line_code[self.dicInfo_LinhaAnafas["conexao_de"][0]:self.dicInfo_LinhaAnafas["conexao_de"][1]].strip()
        dic["resist_aterr_de"] = self.line_code[self.dicInfo_LinhaAnafas["resist_aterr_de"][0]:self.dicInfo_LinhaAnafas["resist_aterr_de"][1]].strip()
        dic["reat_aterr_de"] = self.line_code[self.dicInfo_LinhaAnafas["reat_aterr_de"][0]:self.dicInfo_LinhaAnafas["reat_aterr_de"][1]].strip()
        dic["conexao_para"] = self.line_code[self.dicInfo_LinhaAnafas["conexao_para"][0]:self.dicInfo_LinhaAnafas["conexao_para"][1]].strip()
        dic["resist_aterr_para"] = self.line_code[self.dicInfo_LinhaAnafas["resist_aterr_para"][0]:self.dicInfo_LinhaAnafas["resist_aterr_para"][1]].strip()
        dic["reat_aterr_para"] = self.line_code[self.dicInfo_LinhaAnafas["reat_aterr_para"][0]:self.dicInfo_LinhaAnafas["reat_aterr_para"][1]].strip()
        dic["sub_area"] = self.line_code[self.dicInfo_LinhaAnafas["sub_area"][0]:self.dicInfo_LinhaAnafas["sub_area"][1]].strip()
        dic["unidades_total"] = self.line_code[self.dicInfo_LinhaAnafas["unidades_total"][0]:self.dicInfo_LinhaAnafas["unidades_total"][1]].strip()
        dic["unidades_oper"] = self.line_code[self.dicInfo_LinhaAnafas["unidades_oper"][0]:self.dicInfo_LinhaAnafas["unidades_oper"][1]].strip()
        dic["capac_dj_de"] = self.line_code[self.dicInfo_LinhaAnafas["capac_dj_de"][0]:self.dicInfo_LinhaAnafas["capac_dj_de"][1]].strip()
        dic["cic_capac_dj_de"] = self.line_code[self.dicInfo_LinhaAnafas["cic_capac_dj_de"][0]:self.dicInfo_LinhaAnafas["cic_capac_dj_de"][1]].strip()
        dic["capac_dj_para"] = self.line_code[self.dicInfo_LinhaAnafas["capac_dj_para"][0]:self.dicInfo_LinhaAnafas["capac_dj_para"][1]].strip()
        dic["cic_capac_dj_para"] = self.line_code[self.dicInfo_LinhaAnafas["cic_capac_dj_para"][0]:self.dicInfo_LinhaAnafas["cic_capac_dj_para"][1]].strip()
        dic["data_entrada"] = self.line_code[self.dicInfo_LinhaAnafas["data_entrada"][0]:self.dicInfo_LinhaAnafas["data_entrada"][1]].strip()
        dic["data_saida"] = self.line_code[self.dicInfo_LinhaAnafas["data_saida"][0]:self.dicInfo_LinhaAnafas["data_saida"][1]].strip()
        dic["mva"] = self.line_code[self.dicInfo_LinhaAnafas["mva"][0]:self.dicInfo_LinhaAnafas["mva"][1]].strip()
        dic["td"] = self.line_code[self.dicInfo_LinhaAnafas["td"][0]:self.dicInfo_LinhaAnafas["td"][1]].strip()
        dic["nome_extenso"] = self.line_code[self.dicInfo_LinhaAnafas["nome_extenso"][0]:self.dicInfo_LinhaAnafas["nome_extenso"][1]].strip()

        return dic

    def __get_lineofcode(self, line_code, typeSoftware):
        # Ajusto informações necessárias
        self.line_code = line_code
        self.typeSoftware = typeSoftware.upper()

        # Informações de construção do deck - ANAREDE
        if typeSoftware == "ANR" or typeSoftware == "ANAREDE" or typeSoftware == "PWF":
            dic = self.__get_dataANR()

        elif typeSoftware == "ANF" or typeSoftware == "ANAFAS" or typeSoftware == "ANA" or typeSoftware == "ALT":
            dic = self.__get_dataANF()

        return dic

    def create_dic_linha(self, filename):
        # Convertendo arquivo em lista
        with open(filename, 'r', errors="ignore") as file:
            str_data = file.read()
            self.list_data = str_data.splitlines()

        # Obtendo tipo de arquivo
        TypeDeck = filename[-3:].upper()
        codes_cepel = ["DCIR", "DLIN"]

        # Varrendo arquivo:
        dic_dlin = {}
        list_dic_dlin = []
        actual_code_pwf = ""
        for i in range(0, len(self.list_data)):
            line_of_code = self.list_data[i]

            # Checa se linha é comentário
            if line_of_code[:1] == "(" or line_of_code.strip() == "":
                continue

            # Salva na memória o código "ANAREDE"
            if line_of_code.strip().upper() in codes_cepel:
                actual_code_pwf = line_of_code.strip().upper()
                continue

            # Verifica fim de código
            if line_of_code[:5] == "99999":
                actual_code_pwf = ""
                continue

            # Avalia DBAR
            if actual_code_pwf == "DCIR" or actual_code_pwf == "DLIN":
                # Inicializa objeto com dados de barra
                dic_dlin = self.__get_lineofcode(line_of_code, TypeDeck)
                dic_dlin["linha_deck"] = i+1
                list_dic_dlin.append(dic_dlin)

        return list_dic_dlin

    ###================================================================================================================
    ###
    ### ANÁLISE DOS DICIONÁRIOS CONTENDO DADOS DE LINHA
    ###
    ###================================================================================================================
    def analyze_linha_pwf(self, list_dic_dlin):
        """
        Análise da linha de código DLIN - PWF, visando encontrar algum valor faltante ou conflitante. Seguem as excepcionalidades procuradas:
        ' BLOCO A - ADICIONANDO OBRA
        [1] Número do circuito vazio;
        [2] Capacidade Normal vazio;
        [3] Capacidade Equipamento vazio;
        [4] Capacidade Emergência vazio;
        [5] Número de taps vazio;
        """
        errors = []
        for index, dic in enumerate(list_dic_dlin):

            # Obtendo objeto referente a linha de código
            row_error = dic["linha_deck"]

            # Erros caso a operação seja "A"
            if dic["operacao"] == "" or dic["operacao"] == "0" or dic["operacao"] == "A":

                # Check crítico A.1 - Número do circuito vazio
                if (dic["num_circuito"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-X: Numero do circuito está vazio!")

                # Check crítico A.2 - Capacidade Normal Vazio
                if (dic["capac_normal"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Capacidade Normal está vazio!")

                # Check crítico A.3 - Número de taps vazio
                if (dic['numero_taps'] == "") and (dic["tap_minimo"] != ""):
                    if float(dic["tap_minimo"] or 0) != float(dic["tap_maximo"] or 0):
                        errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Número de taps está vazio!")

                # Check crítico A.4 - Número de taps vazio
                if (dic['numero_taps'] != "") and (dic["tap_minimo"] == "" or dic["tap_maximo"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Número de taps preenchido, porém sem informar TAP mínimo e/ou máximo!")

                # Check crítico A.5 - Barra controlada se tap fixo
                if (dic["tap_minimo"] == "" or dic["tap_maximo"] == "") and (dic["barra_controlada"] != ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Campo Barra Controlada preenchido em transformador sem variação de TAP!")

                # Check crítico A.6 - Resistência vazia para transformador
                if dic["tap"] != "" and (dic["resist_pos"] == "" or float(dic["resist_pos"] or 0) == 0):
                    errors.append(f"ERRO L{row_error} - TRAFO {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Campo resistência de sequência positiva não preenchido ou igual a zero!")

                # Check crítico A.7 - Susceptância nula positiva
                if dic["tap"] == "" and float(dic["suscept_pos"] or 0) == 0:
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência positiva informada como zero!")

                # Check crítico A.8 - Resistência vazia para linha
                if dic["tap"] == "" and (dic["resist_pos"] == "" or float(dic["resist_pos"] or 0) == 0):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Campo resistência de sequência positiva não preenchido ou igual a zero!")

        return errors

    def analyze_linha_ana(self, list_dic_dlin, dic_dbar):
        """
        Análise da linha de código DCIR - ANA, visando encontrar algum valor faltante ou conflitante. Seguem as excepcionalidades procuradas:
        '
        [1] Número do circuito vazio
        [2] Transformador sem dados de conexão
        [3] ...;
        [4] ...
        """
        errors = []
        for index, dic in enumerate(list_dic_dlin):

            # Obtendo objeto referente a linha de código
            row_error = dic["linha_deck"]

            # Erros caso o código de operação seja "A"
            if dic["codigo_atualizacao"] == "" or dic["codigo_atualizacao"] == "0" or dic["codigo_atualizacao"] == "A":
                #
                # Check crítico 1 - Circuito
                if (dic["num_circuito"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-X: Numero do circuito está vazio!")

                # Check crítico 2 - Tipo Circuito
                if (dic["tipo_circuito"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Tipo do circuito está vazio!")

                # Check crítico 3 - Tipo Circuito L com conexão
                if (dic["conexao_de"] != "") or (dic["conexao_para"] != ""):
                    if (dic["tipo_circuito"] == "L"):
                        errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Tipo do circuito inválido! Foram informados dados de conexão para tipo LT! Verificar se o tipo não seria 'T'")

                # Check 4 - Susceptância zero
                if (dic["suscept_pos"] != "") and (dic["suscept_zer"] == "") and dic["reat_zer"] != "999998":
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência zero não informada!")

                # Check crítico 5 - Barra DE tipo MIDPOINT com Conexão DE
                if (dic["tipo_circuito"] == "T"):
                    # Verifica se a barra existe no servidor SIGER
                    if not dic_dbar[dic_dbar["Número"] == dic["barra_de"]].empty:
                        tipo_barra_de = (dic_dbar["Tipo MidPoint"][dic_dbar["Número"] == dic["barra_de"]]).iloc[0]
                        if (tipo_barra_de == "Derivação") and (dic["conexao_de"] != ""):
                            errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Transformador com conexão especificada para a barra DE tipo DERIVAÇÃO!")
                        if (tipo_barra_de == "Midpoint") and (dic['conexao_de'] != ""):
                            errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Transformador com conexão especificada para a barra DE tipo MIDPOINT!")

                # Check crítico 6 - Barra PARA tipo MIDPOINT com Conexão PARA
                if (dic["tipo_circuito"] == "T"):
                    # Verifica se a barra existe no servidor SIGER
                    if not (dic_dbar["Tipo MidPoint"][dic_dbar["Número"] == dic["barra_para"]]).empty:
                        tipo_barra_para = (dic_dbar["Tipo MidPoint"][dic_dbar["Número"] == dic["barra_para"]]).iloc[0]
                        if (tipo_barra_para == "Derivação") and (dic["conexao_para"] != ""):
                            errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Transformador com conexão especificada para a barra PARA tipo DERIVAÇÃO!")

                        if (tipo_barra_para == "Midpoint") and (dic["conexao_para"] != ""):
                            errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Transformador com conexão especificada para a barra PARA tipo MIDPOINT!")

                # Check crítico 7 - Trafo sem resistência
                if dic["tipo_circuito"] == "T" and (dic["resist_pos"] == "" or float(dic["resist_pos"] or 0) == 0):
                    errors.append(f"ERRO L{row_error} - TRAFO {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Campo resistência de sequência positiva não preenchido ou igual a zero!")

                # Check crítico 8 - Trafo sem resistência
                if dic["tipo_circuito"] == "T" and (dic["resist_zer"] == "" or float(dic["resist_zer"] or 0) == 0):
                    errors.append(f"ERRO L{row_error} - TRAFO {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Campo resistência de sequência zero não preenchido ou igual a zero!")

                # Check 9 - Susceptância nula positiva
                if dic["tipo_circuito"] == "L" and float(dic["suscept_pos"] or 0) == 0:
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência positiva informada como zero!")

                # Check 10 - Susceptância nula zero
                if dic["tipo_circuito"] == "L" and float(dic["suscept_zer"] or 0) == 0 and dic["reat_zer"] != "999998":
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência zero informada como zero!")

                # Check 11 - Susceptância nula zero
                if dic["tipo_circuito"] == "L" and float(dic["suscept_zer"] or 0) > float(dic["suscept_pos"] or 0):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência zero informada é maior que o de sequência positiva!")

                if dic["tipo_circuito"] == "L" and dic["km"].strip() != "()":
                    if float(dic["km"] or 0) > 500:
                        errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Comprimento da LT informado extremamente elevado ({float(dic['km'] or 0)} km)!")

            # Erros caso o código de operação seja "M"
            if dic["codigo_atualizacao"] == "2" or dic["codigo_atualizacao"] == "4" or dic["codigo_atualizacao"] == "M":
                #
                # Check crítico 1 - Circuito
                if (dic["num_circuito"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-X: Numero do circuito está vazio!")

                # Check crítico 2 - Tipo Circuito
                if (dic["tipo_circuito"] == ""):
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Tipo do circuito está vazio!")

                # Check 3 - Susceptância zero
                if (dic["suscept_pos"] != "") and (dic["suscept_zer"] == "") and dic["reat_zer"] != "999998":
                    errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência zero não informada!")

                # Check 4 - Susceptância nula positiva
                if dic["tipo_circuito"] == "L" and dic["suscept_pos"] != "":
                    if float(dic["suscept_pos"] or 0) == 0:
                        errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência positiva informada como zero!")

                # Check 5 - Susceptância nula zero
                if dic["tipo_circuito"] == "L" and dic["suscept_zer"] != "":
                    if float(dic["suscept_zer"] or 0) == 0 and dic["reat_zer"] != "999998":
                        errors.append(f"ERRO L{row_error} - LINHA {dic['barra_de']}-{dic['barra_para']}-{dic['num_circuito']}: Susceptância de sequência zero informada como zero!")
        return errors

    def analyze_linha_from_folder(self, path_decks, dic_dbar):
        # Análise deck a deck
        dic_errors = {}
        for index, deck in enumerate(path_decks):
            list_dic = self.create_dic_linha(deck)
            extension = (deck[-3:]).upper()
            filename = deck[deck.rfind("/")+1:]

            if not filename.startswith(tuple(["1_", "2_", "3_", "4_", "7_"])):
                if extension == "PWF":
                    list_errors = self.analyze_linha_pwf(list_dic)
                else:
                    list_errors = self.analyze_linha_ana(list_dic, dic_dbar)

                if len(list_errors) > 0:
                    dic_errors[filename] = list_errors

        return dic_errors

if __name__ == "__main__":
    oLinha = Linha()

    file_pwf = r"D:\_APAGAR\caso\CART.PWF"
    list_dic_dlin_pwf = oLinha.create_dic_linha(file_pwf)
    errors_pwf = oLinha.analyze_linha_pwf(list_dic_dlin_pwf)

    file_ana = r"D:\_APAGAR\caso\BR2306A.ANA"
    list_dic_dlin_ana = oLinha.create_dic_linha(file_ana)
    errors_ana = oLinha.analyze_linha_alt(list_dic_dlin_ana)

    pass