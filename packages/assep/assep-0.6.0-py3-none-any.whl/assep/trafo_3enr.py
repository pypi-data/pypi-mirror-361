import pandas as pd

class Trafo_3enr():
    r"""Classe destinada a montar os transformadores de 3 enrolamentos.

    ...

    Parameters
    ----------
    ...

    Examples
    --------
    Para inicializar a classe, basta chamar ela para o objeto de interesse.

    >>> ...
    >>> ...
    >>> ...
    >>> ...
    """
    ###================================================================================================================
    ###
    ### CÓDIGOS DE INICIALIZAÇÃO
    ###
    ###================================================================================================================
    def __init__(self):
        # Coletando inicialização
        pass

    ###================================================================================================================
    ###
    ### CÓDIGOS PARA COLETAR DATAFRAME
    ###
    ###================================================================================================================
    def GetDF_TR(self, df_ANA):

        # 1-) Filtrar DF para conter apenas ramos de transformadores
        df_TR = df_ANA[df_ANA["Tap"] != ""]
        cols = ['Tap']
        df_TR[cols] = df_TR[cols].astype(float)

        # 2-) Filtrando TFs de 3 enrolamentos - Uma das barras apenas é midpoint
        df_TR = df_TR[(df_TR["Modo_Visualizacao_BarraDe"] == "1") & (df_TR["Modo_Visualizacao_BarraPara"] == "0") |
                            (df_TR["Modo_Visualizacao_BarraDe"] == "0") & (df_TR["Modo_Visualizacao_BarraPara"] == "1")]

        # 3-) Extraindo dicionários do DF - Método mais eficiente de iteração!
        dic_df_TR_3enr = df_TR.to_dict('records')
        dic_TR_3enr = {}

        # 4-) Montando dicionário aninhando com dados dos TFs de 3 enrolamentos
        for RamoTR in dic_df_TR_3enr:
            # ARMADILHA
            if RamoTR["Barra_De"] == "42430" or RamoTR["Barra_Para"] == "42430":
                pass

            # Identifica onde está o Midpoint
            if RamoTR["Modo_Visualizacao_BarraDe"] == "1":
                pos_Mid = "D"
            elif RamoTR["Modo_Visualizacao_BarraPara"] == "1":
                pos_Mid = "P"

            # Identifica se o TF já existe na pilha
            # Caso o MidPoint esteja na BarraDe

            # if pos_Mid == "D": ###TODO: Comentado para resolver problemas de casos mal feitos!!! 

            if pos_Mid == "D" and RamoTR["TAP"] == 1: 
                # Verifica se o MidPoint já está presente no dicionário
                if RamoTR["Barra_De"] in dic_TR_3enr:
                    # MidPoint já havia sido coletado! Checando se existem dados secundários
                    dic_DadosTF = dic_TR_3enr[RamoTR["Barra_De"]]
                    
                    # Adicionando dados no enrolamento secundário
                    if dic_DadosTF["Barra_Enr_Sec"] == "":
                        # Portanto, só havia o primário sido coletado! Observar qual a maior tensão!
                        Tensao_Pri_Orig = dic_DadosTF["Pri_Tensao"]
                        Tensao_Nova = RamoTR["Nome_3_BarraPara"]
                        #
                        try: Tensao_Pri_Orig = int(Tensao_Pri_Orig) 
                        except: Tensao_Pri_Orig = 0
                        try: Tensao_Nova = int(Tensao_Nova) 
                        except: Tensao_Nova = 0
                        #
                        # Caso 1 - O primário já estava correto
                        if Tensao_Pri_Orig >= Tensao_Nova:
                            dic_DadosTF["Barra_Enr_Sec"] = RamoTR["Barra_Para"]
                            dic_DadosTF["Sec_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Sec_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = RamoTR["Nome_3_BarraPara"]
                            dic_DadosTF["Sec_EstadoBR"] = RamoTR["Estado_BR_BarraPara"]
                            dic_DadosTF["Sec_Nome"] = RamoTR["Nome_BarraPara"]
                            dic_DadosTF["Sec_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Sec_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Sec_NConex"] = RamoTR["Numero_Conexoes_BarraPara"]
                            dic_DadosTF["Sec_CargaAtiv"] = RamoTR["Carga_Ativa_BarraPara"]
                            dic_DadosTF["Sec_GerAtiva"] = RamoTR["Geracao_Ativa_BarraPara"]
                            dic_DadosTF["Sec_GerReativa"] = RamoTR["Geracao_Reativa_BarraPara"]
                            dic_DadosTF["Barra_Enr_Ter"] = ""

                            dic_TR_3enr[RamoTR["Barra_De"]] = dic_DadosTF
                        # Caso 2 - O primário estava errado
                        else:
                            # Jogando os dados do primário para o secundário
                            dic_DadosTF["Barra_Enr_Sec"] = dic_DadosTF["Barra_Enr_Pri"]
                            dic_DadosTF["Sec_R_pos"] = dic_DadosTF["Pri_R_pos"]
                            dic_DadosTF["Sec_X_pos"] = dic_DadosTF["Pri_R_pos"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = dic_DadosTF["Pri_Tensao"]
                            dic_DadosTF["Sec_EstadoBR"] = dic_DadosTF["Pri_EstadoBR"]
                            dic_DadosTF["Sec_Nome"] = dic_DadosTF["Pri_Nome"]
                            dic_DadosTF["Sec_Defasag"] = dic_DadosTF["Pri_Defasag"]
                            dic_DadosTF["Sec_TAP"] = dic_DadosTF["Pri_TAP"]
                            dic_DadosTF["Sec_NConex"] = dic_DadosTF["Pri_NConex"]
                            dic_DadosTF["Sec_CargaAtiv"] = dic_DadosTF["Pri_CargaAtiv"]
                            dic_DadosTF["Sec_GerAtiva"] = dic_DadosTF["Pri_GerAtiva"]
                            dic_DadosTF["Sec_GerReativa"] = dic_DadosTF["Pri_GerReativa"]
                            # Inserindo novos dados no primário
                            dic_DadosTF["Barra_Enr_Pri"] = RamoTR["Barra_Para"]
                            dic_DadosTF["Pri_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Pri_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Pri_R_zer"] = ""
                            # dic_DadosTF["Pri_X_zer"] = ""
                            dic_DadosTF["Pri_Tensao"] = RamoTR["Nome_3_BarraPara"]
                            dic_DadosTF["Pri_EstadoBR"] = RamoTR["Estado_BR_BarraPara"]
                            dic_DadosTF["Pri_Nome"] = RamoTR["Nome_BarraPara"]
                            dic_DadosTF["Pri_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Pri_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Pri_NConex"] = RamoTR["Numero_Conexoes_BarraPara"]
                            dic_DadosTF["Pri_CargaAtiv"] = RamoTR["Carga_Ativa_BarraPara"]
                            dic_DadosTF["Pri_GerAtiva"] = RamoTR["Geracao_Ativa_BarraPara"]
                            dic_DadosTF["Pri_GerReativa"] = RamoTR["Geracao_Reativa_BarraPara"]
                            dic_DadosTF["Barra_Enr_Ter"] = ""

                            dic_TR_3enr[RamoTR["Barra_De"]] = dic_DadosTF

                    # Adicionando dados no enrolamento terciário
                    elif dic_DadosTF["Barra_Enr_Ter"] == "":
                        # Portanto, só havia o primário sido coletado! Observar qual a maior tensão!
                        Tensao_Pri_Orig = dic_DadosTF["Pri_Tensao"]
                        Tensao_Sec_Orig = dic_DadosTF["Sec_Tensao"]
                        Tensao_Nova = RamoTR["Nome_3_BarraDe"]
                        #
                        try: Tensao_Pri_Orig = int(Tensao_Pri_Orig) 
                        except: Tensao_Pri_Orig = 0
                        try: Tensao_Sec_Orig = int(Tensao_Sec_Orig) 
                        except: Tensao_Sec_Orig = 0
                        try: Tensao_Nova = int(Tensao_Nova) 
                        except: Tensao_Nova = 0

                        # Caso 1 - O terciário já estava correto
                        if Tensao_Nova <= Tensao_Sec_Orig:
                            dic_DadosTF["Barra_Enr_Ter"] = RamoTR["Barra_Para"]
                            dic_DadosTF["Ter_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Ter_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Ter_R_zer"] = ""
                            # dic_DadosTF["Ter_X_zer"] = ""
                            dic_DadosTF["Ter_Tensao"] = RamoTR["Nome_3_BarraPara"]
                            dic_DadosTF["Ter_EstadoBR"] = RamoTR["Estado_BR_BarraPara"]
                            dic_DadosTF["Ter_Nome"] = RamoTR["Nome_BarraPara"]
                            dic_DadosTF["Ter_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Ter_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Ter_NConex"] = RamoTR["Numero_Conexoes_BarraPara"]
                            dic_DadosTF["Ter_CargaAtiv"] = RamoTR["Carga_Ativa_BarraPara"]
                            dic_DadosTF["Ter_GerAtiva"] = RamoTR["Geracao_Ativa_BarraPara"]
                            dic_DadosTF["Ter_GerReativa"] = RamoTR["Geracao_Reativa_BarraPara"]

                            dic_TR_3enr[RamoTR["Barra_De"]] = dic_DadosTF

                        # Caso 2 - O novo ramo é o secundário
                        elif Tensao_Nova > Tensao_Sec_Orig and Tensao_Nova <= Tensao_Pri_Orig:
                            # Jogando os dados do secundário para o terciário
                            dic_DadosTF["Barra_Enr_Ter"] = dic_DadosTF["Barra_Enr_Sec"]
                            dic_DadosTF["Ter_R_pos"] = dic_DadosTF["Sec_R_pos"]
                            dic_DadosTF["Ter_X_pos"] = dic_DadosTF["Sec_R_pos"]
                            # dic_DadosTF["Ter_R_zer"] = ""
                            # dic_DadosTF["Ter_X_zer"] = ""
                            dic_DadosTF["Ter_Tensao"] = dic_DadosTF["Sec_Tensao"]
                            dic_DadosTF["Ter_EstadoBR"] = dic_DadosTF["Sec_EstadoBR"]
                            dic_DadosTF["Ter_Nome"] = dic_DadosTF["Sec_Nome"]
                            dic_DadosTF["Ter_Defasag"] = dic_DadosTF["Sec_Defasag"]
                            dic_DadosTF["Ter_TAP"] = dic_DadosTF["Sec_TAP"]
                            dic_DadosTF["Ter_NConex"] = dic_DadosTF["Sec_NConex"]
                            dic_DadosTF["Ter_CargaAtiv"] = dic_DadosTF["Sec_CargaAtiv"]
                            dic_DadosTF["Ter_GerAtiva"] = dic_DadosTF["Sec_GerAtiva"]
                            dic_DadosTF["Ter_GerReativa"] = dic_DadosTF["Sec_GerReativa"]
                            # Inserindo novos dados no primário
                            dic_DadosTF["Barra_Enr_Sec"] = RamoTR["Barra_Para"]
                            dic_DadosTF["Sec_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Sec_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = RamoTR["Nome_3_BarraPara"]
                            dic_DadosTF["Sec_EstadoBR"] = RamoTR["Estado_BR_BarraPara"]
                            dic_DadosTF["Sec_Nome"] = RamoTR["Nome_BarraPara"]
                            dic_DadosTF["Sec_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Sec_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Sec_NConex"] = RamoTR["Numero_Conexoes_BarraPara"]
                            dic_DadosTF["Sec_CargaAtiv"] = RamoTR["Carga_Ativa_BarraPara"]
                            dic_DadosTF["Sec_GerAtiva"] = RamoTR["Geracao_Ativa_BarraPara"]
                            dic_DadosTF["Sec_GerReativa"] = RamoTR["Geracao_Reativa_BarraPara"]

                            dic_TR_3enr[RamoTR["Barra_De"]] = dic_DadosTF

                        # Caso 3 - O novo ramo é o primário
                        elif Tensao_Nova > Tensao_Pri_Orig:
                            # Jogando os dados do secundário para o terciário
                            dic_DadosTF["Barra_Enr_Ter"] = dic_DadosTF["Barra_Enr_Sec"]
                            dic_DadosTF["Ter_R_pos"] = dic_DadosTF["Sec_R_pos"]
                            dic_DadosTF["Ter_X_pos"] = dic_DadosTF["Sec_R_pos"]
                            # dic_DadosTF["Ter_R_zer"] = ""
                            # dic_DadosTF["Ter_X_zer"] = ""
                            dic_DadosTF["Ter_Tensao"] = dic_DadosTF["Sec_Tensao"]
                            dic_DadosTF["Ter_EstadoBR"] = dic_DadosTF["Sec_EstadoBR"]
                            dic_DadosTF["Ter_Nome"] = dic_DadosTF["Sec_Nome"]
                            dic_DadosTF["Ter_Defasag"] = dic_DadosTF["Sec_Defasag"]
                            dic_DadosTF["Ter_TAP"] = dic_DadosTF["Sec_TAP"]
                            dic_DadosTF["Ter_NConex"] = dic_DadosTF["Sec_NConex"]
                            dic_DadosTF["Ter_CargaAtiv"] = dic_DadosTF["Sec_CargaAtiv"]
                            dic_DadosTF["Ter_GerAtiva"] = dic_DadosTF["Sec_GerAtiva"]
                            dic_DadosTF["Ter_GerReativa"] = dic_DadosTF["Sec_GerReativa"]
                            #
                            # Jogando os dados do primário para o secundário
                            dic_DadosTF["Barra_Enr_Sec"] = dic_DadosTF["Barra_Enr_Pri"]
                            dic_DadosTF["Sec_R_pos"] = dic_DadosTF["Pri_R_pos"]
                            dic_DadosTF["Sec_X_pos"] = dic_DadosTF["Pri_R_pos"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = dic_DadosTF["Pri_Tensao"]
                            dic_DadosTF["Sec_EstadoBR"] = dic_DadosTF["Pri_EstadoBR"]
                            dic_DadosTF["Sec_Nome"] = dic_DadosTF["Pri_Nome"]
                            dic_DadosTF["Sec_Defasag"] = dic_DadosTF["Pri_Defasag"]
                            dic_DadosTF["Sec_TAP"] = dic_DadosTF["Pri_TAP"]
                            dic_DadosTF["Sec_NConex"] = dic_DadosTF["Pri_NConex"]
                            dic_DadosTF["Sec_CargaAtiv"] = dic_DadosTF["Pri_CargaAtiv"]
                            dic_DadosTF["Sec_GerAtiva"] = dic_DadosTF["Pri_GerAtiva"]
                            dic_DadosTF["Sec_GerReativa"] = dic_DadosTF["Pri_GerReativa"]
                            #
                            # Inserindo novos dados no primário
                            dic_DadosTF["Barra_Enr_Pri"] = RamoTR["Barra_Para"]
                            dic_DadosTF["Pri_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Pri_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Pri_R_zer"] = ""
                            # dic_DadosTF["Pri_X_zer"] = ""
                            dic_DadosTF["Pri_Tensao"] = RamoTR["Nome_3_BarraPara"]
                            dic_DadosTF["Pri_EstadoBR"] = RamoTR["Estado_BR_BarraPara"]
                            dic_DadosTF["Pri_Nome"] = RamoTR["Nome_BarraPara"]
                            dic_DadosTF["Pri_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Pri_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Pri_NConex"] = RamoTR["Numero_Conexoes_BarraPara"]
                            dic_DadosTF["Pri_CargaAtiv"] = RamoTR["Carga_Ativa_BarraPara"]
                            dic_DadosTF["Pri_GerAtiva"] = RamoTR["Geracao_Ativa_BarraPara"]
                            dic_DadosTF["Pri_GerReativa"] = RamoTR["Geracao_Reativa_BarraPara"]

                            dic_TR_3enr[RamoTR["Barra_De"]] = dic_DadosTF
                
                # Adiciona os dados pela primeira vez no dicionário
                else:
                    try: Tensao_Nova = int(RamoTR["Nome_3_BarraPara"]) 
                    except: Tensao_Nova = 0
                    dic_DadosTF =  {
                        # Dados de Enrolamento
                        "Barra_Enr_Mid": RamoTR["Barra_De"],
                        "Barra_Enr_Pri": RamoTR["Barra_Para"],
                        # Dados do Primário
                        "Pri_R_pos": RamoTR["Resistencia"],
                        "Pri_X_pos": RamoTR["Reatancia"],
                        # "Pri_R_zer": "",
                        # "Pri_X_zer": "",
                        "Pri_Tensao": Tensao_Nova,
                        "Pri_EstadoBR": RamoTR["Estado_BR_BarraPara"],
                        "Pri_Nome": RamoTR["Nome_BarraPara"],
                        # "Pri_Conexao": "",
                        "Pri_Defasag": RamoTR["Defasagem"],
                        "Pri_TAP": RamoTR["TAP"],
                        "Pri_NConex": RamoTR["Numero_Conexoes_BarraPara"],
                        "Pri_CargaAtiv": RamoTR["Carga_Ativa_BarraPara"],
                        "Pri_GerAtiva": RamoTR["Geracao_Ativa_BarraPara"],
                        "Pri_GerReativa": RamoTR["Geracao_Reativa_BarraPara"],
                        # Deixa
                        "Numero_TR": RamoTR["Numero_Circuito"],
                        "Barra_Enr_Sec": ""
                        }
                    dic_TR_3enr[RamoTR["Barra_De"]] = dic_DadosTF
                    
            # Caso o MidPoint esteja na BarraPara
            elif pos_Mid == "P": 
                # Verifica se o MidPoint já está presente no dicionário
                if RamoTR["Barra_Para"] in dic_TR_3enr:
                    # MidPoint já havia sido coletado! Checando se existem dados secundários
                    dic_DadosTF = dic_TR_3enr[RamoTR["Barra_Para"]]
                    
                    # Adicionando dados no enrolamento secundário
                    if dic_DadosTF["Barra_Enr_Sec"] == "":
                        # Portanto, só havia o primário sido coletado! Observar qual a maior tensão!
                        Tensao_Pri_Orig = dic_DadosTF["Pri_Tensao"]
                        Tensao_Nova = RamoTR["Nome_3_BarraDe"]
                        #
                        try: Tensao_Pri_Orig = int(Tensao_Pri_Orig) 
                        except: Tensao_Pri_Orig = 0
                        try: Tensao_Nova = int(Tensao_Nova) 
                        except: Tensao_Nova = 0
                        #
                        # Caso 1 - O primário já estava correto
                        if Tensao_Pri_Orig >= Tensao_Nova:
                            dic_DadosTF["Barra_Enr_Sec"] = RamoTR["Barra_De"]
                            dic_DadosTF["Sec_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Sec_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = RamoTR["Nome_3_BarraDe"]
                            dic_DadosTF["Sec_EstadoBR"] = RamoTR["Estado_BR_BarraDe"]
                            dic_DadosTF["Sec_Nome"] = RamoTR["Nome_BarraDe"]
                            dic_DadosTF["Sec_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Sec_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Sec_NConex"] = RamoTR["Numero_Conexoes_BarraDe"]
                            dic_DadosTF["Sec_CargaAtiv"] = RamoTR["Carga_Ativa_BarraDe"]
                            dic_DadosTF["Sec_GerAtiva"] = RamoTR["Geracao_Ativa_BarraDe"]
                            dic_DadosTF["Sec_GerReativa"] = RamoTR["Geracao_Reativa_BarraDe"]
                            dic_DadosTF["Barra_Enr_Ter"] = ""

                            dic_TR_3enr[RamoTR["Barra_Para"]] = dic_DadosTF
                        # Caso 2 - O primário estava errado
                        else:
                            # Jogando os dados do primário para o secundário
                            dic_DadosTF["Barra_Enr_Sec"] = dic_DadosTF["Barra_Enr_Pri"]
                            dic_DadosTF["Sec_R_pos"] = dic_DadosTF["Pri_R_pos"]
                            dic_DadosTF["Sec_X_pos"] = dic_DadosTF["Pri_R_pos"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = dic_DadosTF["Pri_Tensao"]
                            dic_DadosTF["Sec_EstadoBR"] = dic_DadosTF["Pri_EstadoBR"]
                            dic_DadosTF["Sec_Nome"] = dic_DadosTF["Pri_Nome"]
                            dic_DadosTF["Sec_Defasag"] = dic_DadosTF["Pri_Defasag"]
                            dic_DadosTF["Sec_TAP"] = dic_DadosTF["Pri_TAP"]
                            dic_DadosTF["Sec_NConex"] = dic_DadosTF["Pri_NConex"]
                            dic_DadosTF["Sec_CargaAtiv"] = dic_DadosTF["Pri_CargaAtiv"]
                            dic_DadosTF["Sec_GerAtiva"] = dic_DadosTF["Pri_GerAtiva"]
                            dic_DadosTF["Sec_GerReativa"] = dic_DadosTF["Pri_GerReativa"]
                            # Inserindo novos dados no primário
                            dic_DadosTF["Barra_Enr_Pri"] = RamoTR["Barra_De"]
                            dic_DadosTF["Pri_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Pri_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Pri_R_zer"] = ""
                            # dic_DadosTF["Pri_X_zer"] = ""
                            dic_DadosTF["Pri_Tensao"] = RamoTR["Nome_3_BarraDe"]
                            dic_DadosTF["Pri_EstadoBR"] = RamoTR["Estado_BR_BarraDe"]
                            dic_DadosTF["Pri_Nome"] = RamoTR["Nome_BarraDe"]
                            dic_DadosTF["Pri_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Pri_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Pri_NConex"] = RamoTR["Numero_Conexoes_BarraDe"]
                            dic_DadosTF["Pri_CargaAtiv"] = RamoTR["Carga_Ativa_BarraDe"]
                            dic_DadosTF["Pri_GerAtiva"] = RamoTR["Geracao_Ativa_BarraDe"]
                            dic_DadosTF["Pri_GerReativa"] = RamoTR["Geracao_Reativa_BarraDe"]
                            dic_DadosTF["Barra_Enr_Ter"] = ""

                            dic_TR_3enr[RamoTR["Barra_Para"]] = dic_DadosTF

                    # Adicionando dados no enrolamento terciário
                    elif dic_DadosTF["Barra_Enr_Ter"] == "":
                        # Portanto, só havia o primário sido coletado! Observar qual a maior tensão!
                        Tensao_Pri_Orig = dic_DadosTF["Pri_Tensao"]
                        Tensao_Sec_Orig = dic_DadosTF["Sec_Tensao"]
                        Tensao_Nova = RamoTR["Nome_3_BarraDe"]
                        #
                        try: Tensao_Pri_Orig = int(Tensao_Pri_Orig) 
                        except: Tensao_Pri_Orig = 0
                        try: Tensao_Sec_Orig = int(Tensao_Sec_Orig) 
                        except: Tensao_Sec_Orig = 0
                        try: Tensao_Nova = int(Tensao_Nova) 
                        except: Tensao_Nova = 0

                        # Caso 1 - O terciário já estava correto
                        if Tensao_Nova <= Tensao_Sec_Orig:
                            dic_DadosTF["Barra_Enr_Ter"] = RamoTR["Barra_De"]
                            dic_DadosTF["Ter_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Ter_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Ter_R_zer"] = ""
                            # dic_DadosTF["Ter_X_zer"] = ""
                            dic_DadosTF["Ter_Tensao"] = RamoTR["Nome_3_BarraDe"]
                            dic_DadosTF["Ter_EstadoBR"] = RamoTR["Estado_BR_BarraDe"]
                            dic_DadosTF["Ter_Nome"] = RamoTR["Nome_BarraDe"]
                            dic_DadosTF["Ter_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Ter_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Ter_NConex"] = RamoTR["Numero_Conexoes_BarraDe"]
                            dic_DadosTF["Ter_CargaAtiv"] = RamoTR["Carga_Ativa_BarraDe"]
                            dic_DadosTF["Ter_GerAtiva"] = RamoTR["Geracao_Ativa_BarraDe"]
                            dic_DadosTF["Ter_GerReativa"] = RamoTR["Geracao_Reativa_BarraDe"]

                            dic_TR_3enr[RamoTR["Barra_Para"]] = dic_DadosTF

                        # Caso 2 - O novo ramo é o secundário
                        elif Tensao_Nova > Tensao_Sec_Orig and Tensao_Nova <= Tensao_Pri_Orig:
                            # Jogando os dados do secundário para o terciário
                            dic_DadosTF["Barra_Enr_Ter"] = dic_DadosTF["Barra_Enr_Sec"]
                            dic_DadosTF["Ter_R_pos"] = dic_DadosTF["Sec_R_pos"]
                            dic_DadosTF["Ter_X_pos"] = dic_DadosTF["Sec_R_pos"]
                            # dic_DadosTF["Ter_R_zer"] = ""
                            # dic_DadosTF["Ter_X_zer"] = ""
                            dic_DadosTF["Ter_Tensao"] = dic_DadosTF["Sec_Tensao"]
                            dic_DadosTF["Ter_EstadoBR"] = dic_DadosTF["Sec_EstadoBR"]
                            dic_DadosTF["Ter_Nome"] = dic_DadosTF["Sec_Nome"]
                            dic_DadosTF["Ter_Defasag"] = dic_DadosTF["Sec_Defasag"]
                            dic_DadosTF["Ter_TAP"] = dic_DadosTF["Sec_TAP"]
                            dic_DadosTF["Ter_NConex"] = dic_DadosTF["Sec_NConex"]
                            dic_DadosTF["Ter_CargaAtiv"] = dic_DadosTF["Sec_CargaAtiv"]
                            dic_DadosTF["Ter_GerAtiva"] = dic_DadosTF["Sec_GerAtiva"]
                            dic_DadosTF["Ter_GerReativa"] = dic_DadosTF["Sec_GerReativa"]
                            # Inserindo novos dados no primário
                            dic_DadosTF["Barra_Enr_Sec"] = RamoTR["Barra_De"]
                            dic_DadosTF["Sec_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Sec_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = RamoTR["Nome_3_BarraDe"]
                            dic_DadosTF["Sec_EstadoBR"] = RamoTR["Estado_BR_BarraDe"]
                            dic_DadosTF["Sec_Nome"] = RamoTR["Nome_BarraDe"]
                            dic_DadosTF["Sec_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Sec_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Sec_NConex"] = RamoTR["Numero_Conexoes_BarraDe"]
                            dic_DadosTF["Sec_CargaAtiv"] = RamoTR["Carga_Ativa_BarraDe"]
                            dic_DadosTF["Sec_GerAtiva"] = RamoTR["Geracao_Ativa_BarraDe"]
                            dic_DadosTF["Sec_GerReativa"] = RamoTR["Geracao_Reativa_BarraDe"]

                            dic_TR_3enr[RamoTR["Barra_Para"]] = dic_DadosTF

                        # Caso 3 - O novo ramo é o primário
                        elif Tensao_Nova > Tensao_Pri_Orig:
                            # Jogando os dados do secundário para o terciário
                            dic_DadosTF["Barra_Enr_Ter"] = dic_DadosTF["Barra_Enr_Sec"]
                            dic_DadosTF["Ter_R_pos"] = dic_DadosTF["Sec_R_pos"]
                            dic_DadosTF["Ter_X_pos"] = dic_DadosTF["Sec_R_pos"]
                            # dic_DadosTF["Ter_R_zer"] = ""
                            # dic_DadosTF["Ter_X_zer"] = ""
                            dic_DadosTF["Ter_Tensao"] = dic_DadosTF["Sec_Tensao"]
                            dic_DadosTF["Ter_EstadoBR"] = dic_DadosTF["Sec_EstadoBR"]
                            dic_DadosTF["Ter_Nome"] = dic_DadosTF["Sec_Nome"]
                            dic_DadosTF["Ter_Defasag"] = dic_DadosTF["Sec_Defasag"]
                            dic_DadosTF["Ter_TAP"] = dic_DadosTF["Sec_TAP"]
                            dic_DadosTF["Ter_NConex"] = dic_DadosTF["Sec_NConex"]
                            dic_DadosTF["Ter_CargaAtiv"] = dic_DadosTF["Sec_CargaAtiv"]
                            dic_DadosTF["Ter_GerAtiva"] = dic_DadosTF["Sec_GerAtiva"]
                            dic_DadosTF["Ter_GerReativa"] = dic_DadosTF["Sec_GerReativa"]
                            #
                            # Jogando os dados do primário para o secundário
                            dic_DadosTF["Barra_Enr_Sec"] = dic_DadosTF["Barra_Enr_Pri"]
                            dic_DadosTF["Sec_R_pos"] = dic_DadosTF["Pri_R_pos"]
                            dic_DadosTF["Sec_X_pos"] = dic_DadosTF["Pri_R_pos"]
                            # dic_DadosTF["Sec_R_zer"] = ""
                            # dic_DadosTF["Sec_X_zer"] = ""
                            dic_DadosTF["Sec_Tensao"] = dic_DadosTF["Pri_Tensao"]
                            dic_DadosTF["Sec_EstadoBR"] = dic_DadosTF["Pri_EstadoBR"]
                            dic_DadosTF["Sec_Nome"] = dic_DadosTF["Pri_Nome"]
                            dic_DadosTF["Sec_Defasag"] = dic_DadosTF["Pri_Defasag"]
                            dic_DadosTF["Sec_TAP"] = dic_DadosTF["Pri_TAP"]
                            dic_DadosTF["Sec_NConex"] = dic_DadosTF["Pri_NConex"]
                            dic_DadosTF["Sec_CargaAtiv"] = dic_DadosTF["Pri_CargaAtiv"]
                            dic_DadosTF["Sec_GerAtiva"] = dic_DadosTF["Pri_GerAtiva"]
                            dic_DadosTF["Sec_GerReativa"] = dic_DadosTF["Pri_GerReativa"]
                            #
                            # Inserindo novos dados no primário
                            dic_DadosTF["Barra_Enr_Pri"] = RamoTR["Barra_De"]
                            dic_DadosTF["Pri_R_pos"] = RamoTR["Resistencia"]
                            dic_DadosTF["Pri_X_pos"] = RamoTR["Reatancia"]
                            # dic_DadosTF["Pri_R_zer"] = ""
                            # dic_DadosTF["Pri_X_zer"] = ""
                            dic_DadosTF["Pri_Tensao"] = RamoTR["Nome_3_BarraDe"]
                            dic_DadosTF["Pri_EstadoBR"] = RamoTR["Estado_BR_BarraDe"]
                            dic_DadosTF["Pri_Nome"] = RamoTR["Nome_BarraDe"]
                            dic_DadosTF["Pri_Defasag"] = RamoTR["Defasagem"]
                            dic_DadosTF["Pri_TAP"] = RamoTR["TAP"]
                            dic_DadosTF["Pri_NConex"] = RamoTR["Numero_Conexoes_BarraDe"]
                            dic_DadosTF["Pri_CargaAtiv"] = RamoTR["Carga_Ativa_BarraDe"]
                            dic_DadosTF["Pri_GerAtiva"] = RamoTR["Geracao_Ativa_BarraDe"]
                            dic_DadosTF["Pri_GerReativa"] = RamoTR["Geracao_Reativa_BarraDe"]

                            dic_TR_3enr[RamoTR["Barra_Para"]] = dic_DadosTF
                
                # Adiciona os dados pela primeira vez no dicionário
                else:
                    try: Tensao_Nova = int(RamoTR["Nome_3_BarraDe"]) 
                    except: Tensao_Nova = 0
                    dic_DadosTF =  {
                        # Dados de Enrolamento
                        "Barra_Enr_Mid": RamoTR["Barra_Para"],
                        "Barra_Enr_Pri": RamoTR["Barra_De"],
                        # Dados do Primário
                        "Pri_R_pos": RamoTR["Resistencia"],
                        "Pri_X_pos": RamoTR["Reatancia"],
                        # "Pri_R_zer": "",
                        # "Pri_X_zer": "", 
                        "Pri_Tensao": Tensao_Nova,
                        "Pri_EstadoBR": RamoTR["Estado_BR_BarraDe"],
                        "Pri_Nome": RamoTR["Nome_BarraDe"],
                        # "Pri_Conexao": "",
                        "Pri_Defasag": RamoTR["Defasagem"],
                        "Pri_TAP": RamoTR["TAP"],
                        "Pri_NConex": RamoTR["Numero_Conexoes_BarraDe"],
                        "Pri_CargaAtiv": RamoTR["Carga_Ativa_BarraDe"],
                        "Pri_GerAtiva": RamoTR["Geracao_Ativa_BarraDe"],
                        "Pri_GerReativa": RamoTR["Geracao_Reativa_BarraDe"],
                        # Deixa
                        "Numero_TR": RamoTR["Numero_Circuito"],
                        "Barra_Enr_Sec": ""
                        }
                    dic_TR_3enr[RamoTR["Barra_Para"]] = dic_DadosTF
                    
            else:
                print(RamoTR["ID_Linha"])        
        # 5-) Salvando dataframe com dados dos dicionários            
        df_DadosTF_tot = pd.DataFrame(dic_TR_3enr).T            

        # 6-) Limpando Trafos sem informação válida no secundário - MidPoint do Trafo se ligando a dois MidPoints por exemplo
        df_DadosTF_filt = df_DadosTF_tot.dropna(subset="Sec_Nome")

        # 7-) Limpando Trafos sem informação válida no terciário - MidPoint do Trafo se ligando a um outro MidPoint por exemplo
        df_DadosTF_filt = df_DadosTF_tot.dropna(subset="Ter_Nome")

        # 8-) Complementando dados do TF
        cols = ["Pri_R_pos", "Pri_X_pos", "Sec_R_pos", "Sec_X_pos", "Ter_R_pos", "Ter_X_pos", "Pri_TAP", "Sec_TAP", "Ter_TAP"]
        df_DadosTF_filt[cols] = df_DadosTF_filt[cols].astype(float)
        #
        df_DadosTF_filt["Rps"] = df_DadosTF_filt["Pri_R_pos"] + df_DadosTF_filt["Sec_R_pos"]
        df_DadosTF_filt["Xps"] = df_DadosTF_filt["Pri_X_pos"] + df_DadosTF_filt["Sec_X_pos"]

        return df_DadosTF_filt
