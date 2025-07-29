import os

class Barra:
    # Inicializa a representação dos dados de uma barra
    def __init__(self):
        # Coleto apenas os dicionários com os delimitadores de campo
        self.dicInfo_BarraAnarede = self.__create_dicInfo_BarraAnarede()
        self.dicInfo_BarraAnafas = self.__create_dicInfo_BarraAnafas()
    
    ###================================================================================================================
    ###
    ### CRIAÇÃO DOS DICIONÁRIOS CONTENDO DADOS DE BARRA
    ###
    ###================================================================================================================
    def __create_dicInfo_BarraAnarede(self):
        dicInfo_BarraAnarede = {}
        dicInfo_BarraAnarede["numero"] = (0,5)
        dicInfo_BarraAnarede["operacao"] = (5,6)
        dicInfo_BarraAnarede["estado"] = (6,7)
        dicInfo_BarraAnarede["tipo"] = (7,8)
        dicInfo_BarraAnarede["grupo_base_tensao"] = (8,10)
        dicInfo_BarraAnarede["nome"] = (10,22)
        dicInfo_BarraAnarede["grupo_limite_tensao"] = (22,24)
        dicInfo_BarraAnarede["tensao"] = (24,28)
        dicInfo_BarraAnarede["angulo"] = (28,32)
        dicInfo_BarraAnarede["ger_ativa"] = (32,37)
        dicInfo_BarraAnarede["ger_reativa"] = (37,42)
        dicInfo_BarraAnarede["ger_reativa_min"] = (42,47)
        dicInfo_BarraAnarede["ger_reativa_max"] = (47,52)
        dicInfo_BarraAnarede["barra_controlada"] = (52,58)
        dicInfo_BarraAnarede["carga_ativa"] = (58,63)
        dicInfo_BarraAnarede["carga_reativa"] = (63,68)
        dicInfo_BarraAnarede["capacitor_reator"] = (68,73)
        dicInfo_BarraAnarede["area"] = (73,76)
        dicInfo_BarraAnarede["tensao_definicao_carga"] = (76,80)
        dicInfo_BarraAnarede["modo_visualizacao"] = (80,81)
        #
        return dicInfo_BarraAnarede

    def __create_dicInfo_BarraAnafas(self):
        dicInfo_BarraAnafas = {}
        dicInfo_BarraAnafas["numero"] = (0,5)
        dicInfo_BarraAnafas["codigo_atualizacao"] = (5,6)
        dicInfo_BarraAnafas["estado"] = (6,7)
        dicInfo_BarraAnafas["tipo"] = (7,8)
        dicInfo_BarraAnafas["nome_barra"] = (9,21)
        dicInfo_BarraAnafas["tensao_prefalta"] = (22,26)
        dicInfo_BarraAnafas["angulo_prefalta"] = (26,30)
        dicInfo_BarraAnafas["tensao_base"] = (31,35)
        dicInfo_BarraAnafas["capac_dj"] = (36,42)
        dicInfo_BarraAnafas["data_entrada"] = (52,60)
        dicInfo_BarraAnafas["data_saida"] = (60,68)
        dicInfo_BarraAnafas["area"] = (69,72)
        dicInfo_BarraAnafas["subarea"] = (72,75)
        dicInfo_BarraAnafas["fronteira"] = (76,77)
        #
        return dicInfo_BarraAnafas

    def __get_dataANR(self):
        # Atribuicao dos valores nos objetos
        dic = {}
        dic["numero"] = self.line_code[self.dicInfo_BarraAnarede["numero"][0]:self.dicInfo_BarraAnarede["numero"][1]].strip()
        dic["operacao"] = self.line_code[self.dicInfo_BarraAnarede["operacao"][0]:self.dicInfo_BarraAnarede["operacao"][1]].strip()
        dic["estado"] = self.line_code[self.dicInfo_BarraAnarede["estado"][0]:self.dicInfo_BarraAnarede["estado"][1]].strip()
        dic["tipo"] = self.line_code[self.dicInfo_BarraAnarede["tipo"][0]:self.dicInfo_BarraAnarede["tipo"][1]].strip()
        dic["grupo_base_tensao"] = self.line_code[self.dicInfo_BarraAnarede["grupo_base_tensao"][0]:self.dicInfo_BarraAnarede["grupo_base_tensao"][1]].strip()
        dic["nome"] = self.line_code[self.dicInfo_BarraAnarede["nome"][0]:self.dicInfo_BarraAnarede["nome"][1]].strip()
        dic["grupo_limite_tensao"] = self.line_code[self.dicInfo_BarraAnarede["grupo_limite_tensao"][0]:self.dicInfo_BarraAnarede["grupo_limite_tensao"][1]].strip()
        dic["tensao"] = self.line_code[self.dicInfo_BarraAnarede["tensao"][0]:self.dicInfo_BarraAnarede["tensao"][1]].strip()
        dic["angulo"] = self.line_code[self.dicInfo_BarraAnarede["angulo"][0]:self.dicInfo_BarraAnarede["angulo"][1]].strip()
        dic["ger_ativa"] = self.line_code[self.dicInfo_BarraAnarede["ger_ativa"][0]:self.dicInfo_BarraAnarede["ger_ativa"][1]].strip()
        dic["ger_reativa"] = self.line_code[self.dicInfo_BarraAnarede["ger_reativa"][0]:self.dicInfo_BarraAnarede["ger_reativa"][1]].strip()
        dic["ger_reativa_min"] = self.line_code[self.dicInfo_BarraAnarede["ger_reativa_min"][0]:self.dicInfo_BarraAnarede["ger_reativa_min"][1]].strip()
        dic["ger_reativa_max"] = self.line_code[self.dicInfo_BarraAnarede["ger_reativa_max"][0]:self.dicInfo_BarraAnarede["ger_reativa_max"][1]].strip()
        dic["barra_controlada"] = self.line_code[self.dicInfo_BarraAnarede["barra_controlada"][0]:self.dicInfo_BarraAnarede["barra_controlada"][1]].strip()
        dic["carga_ativa"] = self.line_code[self.dicInfo_BarraAnarede["carga_ativa"][0]:self.dicInfo_BarraAnarede["carga_ativa"][1]].strip()
        dic["carga_reativa"] = self.line_code[self.dicInfo_BarraAnarede["carga_reativa"][0]:self.dicInfo_BarraAnarede["carga_reativa"][1]].strip()
        dic["capacitor_reator"] = self.line_code[self.dicInfo_BarraAnarede["capacitor_reator"][0]:self.dicInfo_BarraAnarede["capacitor_reator"][1]].strip()
        dic["area"] = self.line_code[self.dicInfo_BarraAnarede["area"][0]:self.dicInfo_BarraAnarede["area"][1]].strip()
        dic["tensao_definicao_carga"] = self.line_code[self.dicInfo_BarraAnarede["tensao_definicao_carga"][0]:self.dicInfo_BarraAnarede["tensao_definicao_carga"][1]].strip()
        dic["modo_visualizacao"] = self.line_code[self.dicInfo_BarraAnarede["modo_visualizacao"][0]:self.dicInfo_BarraAnarede["modo_visualizacao"][1]].strip()

        return dic

    def __get_dataANF(self):
        # Atribuicao dos valores nos objetos
        dic = {}
        dic["numero"] = self.line_code[self.dicInfo_BarraAnafas["numero"][0]:self.dicInfo_BarraAnafas["numero"][1]].strip()
        dic["codigo_atualizacao"] = self.line_code[self.dicInfo_BarraAnafas["codigo_atualizacao"][0]:self.dicInfo_BarraAnafas["codigo_atualizacao"][1]].strip()
        dic["estado"] = self.line_code[self.dicInfo_BarraAnafas["estado"][0]:self.dicInfo_BarraAnafas["estado"][1]].strip()
        dic["tipo"] = self.line_code[self.dicInfo_BarraAnafas["tipo"][0]:self.dicInfo_BarraAnafas["tipo"][1]].strip()
        dic["nome_barra"] = self.line_code[self.dicInfo_BarraAnafas["nome_barra"][0]:self.dicInfo_BarraAnafas["nome_barra"][1]].strip()
        dic["tensao_prefalta"] = self.line_code[self.dicInfo_BarraAnafas["tensao_prefalta"][0]:self.dicInfo_BarraAnafas["tensao_prefalta"][1]].strip()
        dic["angulo_prefalta"] = self.line_code[self.dicInfo_BarraAnafas["angulo_prefalta"][0]:self.dicInfo_BarraAnafas["angulo_prefalta"][1]].strip()
        dic["tensao_base"] = self.line_code[self.dicInfo_BarraAnafas["tensao_base"][0]:self.dicInfo_BarraAnafas["tensao_base"][1]].strip()
        dic["capac_dj"] = self.line_code[self.dicInfo_BarraAnafas["capac_dj"][0]:self.dicInfo_BarraAnafas["capac_dj"][1]].strip()
        dic["data_entrada"] = self.line_code[self.dicInfo_BarraAnafas["data_entrada"][0]:self.dicInfo_BarraAnafas["data_entrada"][1]].strip()
        dic["data_saida"] = self.line_code[self.dicInfo_BarraAnafas["data_saida"][0]:self.dicInfo_BarraAnafas["data_saida"][1]].strip()
        dic["area"] = self.line_code[self.dicInfo_BarraAnafas["area"][0]:self.dicInfo_BarraAnafas["area"][1]].strip()
        dic["subarea"] = self.line_code[self.dicInfo_BarraAnafas["subarea"][0]:self.dicInfo_BarraAnafas["subarea"][1]].strip()
        dic["fronteira"] = self.line_code[self.dicInfo_BarraAnafas["fronteira"][0]:self.dicInfo_BarraAnafas["fronteira"][1]].strip()

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

    def create_dic_barra(self, filename):
        # Convertendo arquivo em lista
        with open(filename, 'r', errors="ignore") as file:
            str_data = file.read()
            self.list_data = str_data.splitlines()

        # Obtendo tipo de arquivo
        TypeDeck = filename[-3:].upper()
        codes_cepel = ["DBAR"]

        # Varrendo arquivo:
        dic_dbar = {}
        list_dic_dbar = []
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
            if actual_code_pwf == "DBAR":
                # Inicializa objeto com dados de barra
                dic_dbar = self.__get_lineofcode(line_of_code, TypeDeck)
                dic_dbar["linha_deck"] = i+1
                list_dic_dbar.append(dic_dbar)

        return list_dic_dbar

    ###================================================================================================================
    ###
    ### ANÁLISE DOS DICIONÁRIOS CONTENDO DADOS DE BARRA
    ###
    ###================================================================================================================
    def analyze_barra_pwf(self, list_dic_dbar):
        """
        Análise da linha de código DBAR - PWF, visando encontrar algum valor faltante ou conflitante. Seguem as excepcionalidades procuradas:
        '
        [1] Grupo base tensão vazio, exceto nos casos de exclusão de barra;
        [2] Grupo limite tensão vazio, exceto nos casos de exclusão de barra;
        [3] Area vazio, exceto nos casos de exclusão de barra
        [4] Grupo limite tensão diferente dos valores esperados
        [5] Grupo base tensão em minúsculo
        [6] Área inválida
        """
        errors = []
        for index, dic in enumerate(list_dic_dbar):
            
            # Obtendo objeto referente a linha de código
            row_error = dic["linha_deck"]

            # Erros caso a operação seja "A"
            if dic["operacao"] == "" or dic["operacao"] == "0" or dic["operacao"] == "A":
                #
                ## Check crítico A.1 - Grupo base de tensão
                if (dic["grupo_base_tensao"] == ""):
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo base tensão está vazio!")

                # Check crítico A.2 - Grupo limite de tensão
                if (dic["grupo_limite_tensao"] == ""):
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo limite de tensão está vazio!")

                # Check crítico A.3 - Área
                if (dic["area"] == ""):
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Área está vazio!")

                # Check crítico A.4 - Grupo limite tensão diferente dos valores esperados - SIGER
                # expected_gl = [1, 2, 3, 4, 5, 6, 8]
                # if (dic["grupo_limite_tensao"] != ""):
                #     try: 
                #         glt = int(dic["grupo_limite_tensao"])
                #         if int(dic["grupo_limite_tensao"]) not in expected_gl:
                #             errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo Limite tensão informado ({dic['grupo_limite_tensao']}) não pré-cadastrado!")
                #     except:
                #         errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo Limite tensão informado ({dic['grupo_limite_tensao']}) não é um número inteiro!")
                
                # if (dic["grupo_limite_tensao"] != "") and isinstance(dic["grupo_limite_tensao"], int):
                #     if int(dic["grupo_limite_tensao"]) not in expected_gl:
                #         errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo Limite tensão informado ({dic['grupo_limite_tensao']}) não pré-cadastrado!")

                # # Check crítico A.5 - Grupo base de tensão em minúsculo
                # expected_gb_1 = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",]
                # expected_gb_2 = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20",
                #                 "21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39",]
                
                # if (dic["grupo_base_tensao"] != "") and (dic["grupo_base_tensao"] not in expected_gb_1 and dic["grupo_base_tensao"] not in expected_gb_2):
                #     errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo base tensão inválido: {dic['grupo_base_tensao']}!")

                # # Check crítico A.6 - Área inválida
                # expected_areas =    [1 ,2  ,3  ,4  ,5  ,6  ,51 ,52 ,53 ,54 ,101,102,103,104,105,201,202,203,204,205,206,207,208,209,210,211,212,213,214,216,217,241,251,252,
                #                     253,254,255,256,258,259,260,261,301,302,303,304,305,306,351,352,353,354,355,356,357,358,359,360,361,362,401,402,403,404,431,432,451,452,
                #                     453,454,455,456,457,458,459,460,471,472,473,474,475,476,477,478,479,480,511,512,513,514,515,516,517,518,519,520,561,562,563,564,581,582,
                #                     583,701,702,703,704,711,712,713,714,715,716,721,722,723,724,741,742,743,744,761,762,763,764,771,772,773,801,802,803,804,805,806,821,822,
                #                     841,842,843,844,845,846,847,848,861,862,863,864,865,866,881,882,883,998,999,]
                # if (dic["area"] != "") and (int(dic["area"]) not in expected_areas):
                #     errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Área informada ({dic['area']}) não faz parte das áreas pré-cadastradas no SIGER!")

        return errors
    
    def analyze_barra_ana(self, list_dic_dbar):
        """
        Análise da linha de código DBAR - ANA, visando encontrar algum valor faltante ou conflitante. Seguem as excepcionalidades procuradas:
        '
        [1] Area vazio, exceto nos casos de exclusão de barra;
        [2] ...;
        [3] ...;
        [4] ...
        """
        errors = []
        for index, dic in enumerate(list_dic_dbar):
            
            # Obtendo objeto referente a linha de código
            row_error = dic["linha_deck"]

            # Erros caso o código de operação seja "A"
            if dic["codigo_atualizacao"] == "" or dic["codigo_atualizacao"] == "0" or dic["codigo_atualizacao"] == "A":
                #
                ## Check crítico A.1 - Área
                if (dic["area"] == ""):
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Área está vazio!")

                # # Check crítico A.2 - Área inválida
                # expected_areas =    [1 ,2  ,3  ,4  ,5  ,6  ,51 ,52 ,53 ,54 ,101,102,103,104,105,201,202,203,204,205,206,207,208,209,210,211,212,213,214,216,217,241,251,252,
                #                     253,254,255,256,258,259,260,261,301,302,303,304,305,306,351,352,353,354,355,356,357,358,359,360,361,362,401,402,403,404,431,432,451,452,
                #                     453,454,455,456,457,458,459,460,471,472,473,474,475,476,477,478,479,480,511,512,513,514,515,516,517,518,519,520,561,562,563,564,581,582,
                #                     583,701,702,703,704,711,712,713,714,715,716,721,722,723,724,741,742,743,744,761,762,763,764,771,772,773,801,802,803,804,805,806,821,822,
                #                     841,842,843,844,845,846,847,848,861,862,863,864,865,866,881,882,883,998,999,]
                # if (dic["area"] != "") and (int(dic["area"]) not in expected_areas):
                #     errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Área informada ({dic['area']}) não faz parte das áreas pré-cadastradas no SIGER!")

        return errors

    def analyze_barra_from_folder(self, path_decks):        
        # Análise deck a deck
        dic_errors = {}
        for index, deck in enumerate(path_decks):
            list_dic_dbar = self.create_dic_barra(deck)
            extension = (deck[-3:]).upper()
            filename = deck[deck.rfind("/")+1:]

            if extension == "PWF":
                list_errors = self.analyze_barra_pwf(list_dic_dbar)
            else:
                list_errors = self.analyze_barra_ana(list_dic_dbar)

            if len(list_errors) > 0:
                dic_errors[filename] = list_errors

        return dic_errors
    
    ###================================================================================================================
    ###
    ### ANÁLISE DOS DICIONÁRIOS CONTENDO DADOS DE BARRA + SIGER
    ###
    ###================================================================================================================
    def analyze_barra_pwf_SIGER(self, list_dic_dbar, list_glt_mod, list_gbt_mod, list_area):
        """
        Análise da linha de código DBAR - PWF, visando encontrar algum valor faltante ou conflitante. Seguem as excepcionalidades procuradas:
        '
        [1] Grupo limite tensão diferente dos valores esperados
        [2] Grupo base tensão em minúsculo
        [3] Área inválida
        """
        errors = []
        for index, dic in enumerate(list_dic_dbar):
            
            # Obtendo objeto referente a linha de código
            row_error = dic["linha_deck"]

            # Erros caso a operação seja "A"
            if dic["operacao"] == "" or dic["operacao"] == "0" or dic["operacao"] == "A":
                #
                # Check crítico A.4 - Grupo limite tensão diferente dos valores esperados - SIGER
                # list_glt = (oSIGER.get_LimiteTensao())["Grupo"].to_list()
                # list_glt_mod = [item.replace('=', '').replace('"', '').replace('\xa0', '') for item in list_glt]
                # list_gbt = (oSIGER.get_BaseTensao())["Grupo"].to_list()
                # list_gbt_mod = [item.replace('=', '').replace('"', '').replace('\xa0', '') for item in list_gbt]
                # list_area = (oSIGER.get_Area())["Número"].to_list()

                # Check crítico A.1 - Grupo limite tensão diferente dos valores esperados - SIGER
                if (dic["grupo_limite_tensao"] != "") and (dic["grupo_limite_tensao"]) not in list_glt_mod:
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo Limite tensão informado ({dic['grupo_limite_tensao']}) não pré-cadastrado!")

                # Check crítico A.2 - Grupo base tensão diferente dos valores esperados - SIGER
                if (dic["grupo_base_tensao"] != ""):
                    if (dic["grupo_base_tensao"]).isdigit() and len((dic["grupo_base_tensao"])) == 1:
                        dic["grupo_base_tensao"] = "0" + dic["grupo_base_tensao"]
                    if (dic["grupo_base_tensao"]) not in list_gbt_mod:
                        errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Grupo base tensão informado {dic['grupo_base_tensao']} não pré-cadastrado!!")

                # Check crítico A.3 - Área inválida
                if (dic["area"] != "") and int(dic["area"]) not in list_area:
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Área informada ({dic['area']}) não faz parte das áreas pré-cadastradas no SIGER!")

        return errors
    
    def analyze_barra_ana_SIGER(self, list_dic_dbar, list_area):
        """
        Análise da linha de código DBAR - ANA, visando encontrar algum valor faltante ou conflitante. Seguem as excepcionalidades procuradas:
        '
        [1] Area vazio, exceto nos casos de exclusão de barra;
        [2] ...;
        [3] ...;
        [4] ...
        """
        errors = []
        for index, dic in enumerate(list_dic_dbar):
            
            # Obtendo objeto referente a linha de código
            row_error = dic["linha_deck"]

            # Erros caso o código de operação seja "A"
            if dic["codigo_atualizacao"] == "" or dic["codigo_atualizacao"] == "0" or dic["codigo_atualizacao"] == "A":
                #
                # Check crítico A.1 - Área inválida
                # list_area = (oSIGER.get_Area())["Número"].to_list()
                if (dic["area"] != "") and int(dic["area"]) not in list_area:
                    errors.append(f"ERRO L{row_error} - BARRA {dic['numero']}: Área informada ({dic['area']}) não faz parte das áreas pré-cadastradas no SIGER!")

        return errors
    
    def analyze_barra_from_folder_SIGER(self, path_decks, list_glt_mod, list_gbt_mod, list_area):        
        # Análise deck a deck
        dic_errors = {}
        for index, deck in enumerate(path_decks):
            list_dic_dbar = self.create_dic_barra(deck)
            extension = (deck[-3:]).upper()
            filename = deck[deck.rfind("/")+1:]

            if extension == "PWF":
                list_errors = self.analyze_barra_pwf_SIGER(list_dic_dbar, list_glt_mod, list_gbt_mod, list_area)
            else:
                list_errors = self.analyze_barra_ana_SIGER(list_dic_dbar, list_area)

            if len(list_errors) > 0:
                dic_errors[filename] = list_errors

        return dic_errors
    


if __name__ == "__main__":
    oBarra = Barra()

    file_pwf = r"D:\_APAGAR\caso\CART.PWF"
    list_dic_dbar_pwf = oBarra.create_dic_barra(file_pwf)
    errors_pwf = oBarra.analyze_barra_pwf(list_dic_dbar_pwf)

    file_ana = r"D:\_APAGAR\caso\BR2306A.ANA"
    list_dic_dbar_ana = oBarra.create_dic_barra(file_ana)
    errors_ana = oBarra.analyze_barra_ana(list_dic_dbar_ana)    
    
    pass



