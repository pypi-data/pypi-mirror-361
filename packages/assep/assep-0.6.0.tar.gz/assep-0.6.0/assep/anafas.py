import pandas as pd
import numpy as np
import os
import subprocess
import time
import sys

class ANAFAS():
    r"""Classe destinada a automatizar a extração de dados diretamente dos arquivos ANA.

    É condensado nessa classe métodos para obter dados diretamente dos arquivos em formatos
    ANA. São gerados decks para alimentar o ANAFAS que por sua vez irá gerar relatórios de saída
    que após tratamento irão fornecer os dados desejados

    Parameters
    ----------
    Classe inicializada com o Path do ANAFAS e a lista de ANAs a serem trabalhados.

    Examples
    --------
    Para inicializar a classe, basta chamar ela para o objeto de interesse.

    >>> import CEPEL_Tools as cp
    >>> Path_Anafas = str(r"C:\Cepel\Anafas\7.5.1\Anafas.exe")
    >>> lista_casos = easygui.fileopenbox(default="D:\\_APAGAR\\LIXO\\*.ANA", title="Selecionar os Decks ANA - ANAFAS", multiple=True)
    >>> newRun = True
    >>> oAnafas = cp.ANAFAS(Path_Anafas, lista_casos, newRun=newRun)
    """
    ###================================================================================================================
    ###
    ### CÓDIGOS DE INICIALIZAÇÃO
    ###
    ###================================================================================================================
    def __init__(self, path, listCases, newRun = True):
        # Definindo engine
        self.engine = path

        # Já deixa na memória todas os casos a serem trabalhados
        self.lista_casos = listCases

        # Limpa ou cria a pasta TEMP
        self.path_decks = self.__initialize_TEMP_folder(newRun)

        # Guarda informação se é para rodar o Anafas ou não
        self.newRun = newRun

    def __initialize_TEMP_folder(self, newRun):
        r"""
        Função auxiliar chamada pela inicialização da classe

        Responsável por limpar a pasta TEMP ou criar esta na sua ausência
        """
        # Limpar e criar a pasta TEMP
        index = self.lista_casos[0].rfind("/")
        path_decks = self.lista_casos[0][:index] + "/TEMP_ANF/"

        # Checa se a pasta temporária existe
        TEMP_exist = os.path.exists(path_decks)
        if not TEMP_exist:
            os.makedirs(path_decks)

        # Limpa pasta TEMP
        if newRun:
            for file_name in os.listdir(path_decks):
                file = path_decks + file_name
                if os.path.isfile(file):
                    os.remove(file)

        # Retorna o diretório de trabalho
        return path_decks

    ###================================================================================================================
    ###
    ### CÓDIGOS PARA OBTER O NÍVEL DE CURTO-CIRCUITO
    ###
    ###================================================================================================================
    def __generateINPfile(self, resultsKA, resultsMVA):
        r"""
        Responsável por gerar o deck INP na pasta dos decks ANA contendo as informações para alimentar o ANAFAS
        """
        start_time = time.time()
        # Criar o arquivo INP
        path_INP = self.path_decks + "CURTO.INP"
        line_separator_1 = "(" + "="*80
        line_separator_2 = "(" + "*"*80
        list_INP = []
        #
        list_INP.append(line_separator_1)
        list_INP.append("(=                    RELATORIO DO NIVEL DE CC")
        list_INP.append(line_separator_1)
        list_INP.append("(")
        list_INP.append(line_separator_2)
        list_INP.append("( CONSTANTES DO PROGRAMA")
        list_INP.append(line_separator_2)
        list_INP.append("(")
        list_INP.append("DCTE")
        list_INP.append("RBTP N")
        list_INP.append("TNCC SIMU")
        list_INP.append("9999")
        list_INP.append("(")
        #
        for i in range(len(self.lista_casos)):
            path_ana_file = self.lista_casos[i]
            # path_ana_file = path_ana_file.replace("/","\\")
            filename_ana = path_ana_file[path_ana_file.rindex("/")+1:-4]
            path_ana_result_ka = self.path_decks + filename_ana + "_kA.txt"
            path_ana_result_mva = self.path_decks + filename_ana + "_Mva.txt"
            #
            if resultsKA:
                list_INP.append(line_separator_2)
                list_INP.append("(* Curto kA - Caso ANAFAS " + filename_ana)
                list_INP.append(line_separator_2)
                list_INP.append("( Acerto da constante referente à unidade utilizada no relatório")
                list_INP.append("DCTE")
                list_INP.append("RUNI KA")
                list_INP.append("NCOL 132")
                list_INP.append("9999")
                list_INP.append("(")
                list_INP.append("( Arquivo de dados:")
                list_INP.append("ARQV DADO")
                list_INP.append(path_ana_file)
                list_INP.append("(")
                list_INP.append("( Arquivo onde sera impresso o relatorio resultante:")
                list_INP.append("ARQV SAID")
                list_INP.append(path_ana_result_ka)
                list_INP.append("(")
                list_INP.append("( Gerar relatorio do nivel de CC")
                list_INP.append("RELA RNCC")
                list_INP.append("(")
            #
            if resultsMVA:
                list_INP.append(line_separator_2)
                list_INP.append("(* Curto MVA - Caso ANAFAS " + filename_ana)
                list_INP.append(line_separator_2)
                list_INP.append("( Acerto da constante referente à unidade utilizada no relatório")
                list_INP.append("DCTE")
                list_INP.append("RUNI MVA")
                list_INP.append("NCOL 132")
                list_INP.append("9999")
                list_INP.append("(")
                list_INP.append("( Arquivo de dados:")
                list_INP.append("ARQV DADO")
                list_INP.append(path_ana_file)
                list_INP.append("(")
                list_INP.append("( Arquivo onde sera impresso o relatorio resultante:")
                list_INP.append("ARQV SAID")
                list_INP.append(path_ana_result_mva)
                list_INP.append("(")
                list_INP.append("( Gerar relatorio do nivel de CC")
                list_INP.append("RELA RNCC")
                list_INP.append("(")
        list_INP.append("FIM")
        path_INP = path_INP.replace("\\","/")
        with open(path_INP, 'w') as f:
            string_value = "\n".join(list_INP)
            f.write(string_value)

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO DECK INP")
        return path_INP

    def __exeCommandAnafas(self, path_INP):
        r"""
        Responsável por executar o comando de passar o deck INP dentro do Anafas
        """
        # Executa o arquivo INP
        comando = self.engine + " -WIN " + path_INP
        #
        start_time = time.time()
        p = subprocess.Popen(comando)
        p.wait()
        p.terminate()

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO ANAFAS - GERANDO RELATÓRIOS TXT")

    def __transformReportsCC(self):
        r"""
        Responsável por transformar os relatórios txt para csv na pasta
        """
        start_time = time.time()
        path_result = []
        dic_dfs = {}
        for file in os.listdir(self.path_decks):
            if file.endswith(".TXT"):
                path_result.append(self.path_decks +  file)

        for i in range(len(path_result)):
            file_result = path_result[i]
            filename_result = file_result[file_result.rindex("/")+1:-4]
            path_csv = self.path_decks + filename_result + ".csv"
            if self.newRun:
                # Lendo arquivo
                with open(file_result, 'r') as file:
                    data = file.read()
                # Reescrevendo o arquivo no enconding
                with open(file_result, 'w', encoding="utf-8") as f:
                    f.write(data)

            # Montando o dataframe
            if file_result[-7:] == "_KA.TXT":
                # COLUNAS - RELATORIO NIVEIS CC - KA
                list_columns=['Numero', 'Nome', 'Tensao_Base', 'kA_CC3F', 'ang_CC3F', 'x/r_CC3F', 'ass_CC3F',
                        'kA_CC1F', 'ang_CC1F', 'x/r_CC1F', 'ass_CC1F', 'kA_CC2F', 'ang_CC2F', 'x/r_CC2F', 'ass_CC2F', 'F']
                list_columns_float = ['Tensao_Base', 'kA_CC3F', 'ang_CC3F', 'x/r_CC3F', 'ass_CC3F','kA_CC1F', 'ang_CC1F', 'x/r_CC1F',
                        'ass_CC1F', 'kA_CC2F', 'ang_CC2F', 'x/r_CC2F', 'ass_CC2F']
                #
            elif file_result[-8:] == "_MVA.TXT":
                # COLUNAS - RELATORIO NIVEIS CC - KA
                list_columns=['Numero', 'Nome', 'Tensao_Base', 'Mva_CC3F', 'ang_CC3F', 'x/r_CC3F', 'ass_CC3F',
                        'Mva_CC1F', 'ang_CC1F', 'x/r_CC1F', 'ass_CC1F', 'Mva_CC2F', 'ang_CC2F', 'x/r_CC2F', 'ass_CC2F', 'F']
                list_columns_float = ['Tensao_Base', 'Mva_CC3F', 'ang_CC3F', 'x/r_CC3F', 'ass_CC3F','Mva_CC1F', 'ang_CC1F', 'x/r_CC1F',
                        'ass_CC1F', 'Mva_CC2F', 'ang_CC2F', 'x/r_CC2F', 'ass_CC2F']
            #
            # Tamanho das colunas
            colspecs = [  (2,7),    (8,20),  (21,27),       (28,37),  (38,44),    (45,53),    (54,61),
                        (62,71),   (72,78),    (79,87),    (88,95),    (96,105),   (106,112), (113,121),  (122,129), (130,131)]
            df_temp = pd.read_fwf(file_result, skiprows=0, skipfooter=0, names=list_columns, colspecs=colspecs,  dtype=str)
            #
            # Limpando linhas do df ondeo número da barra não seja inteiro
            df_temp = df_temp.replace('********', np.NaN)
            df_temp = df_temp.replace('*******', np.NaN)
            cols = ["Numero"]
            df_temp[cols] = df_temp[cols].apply(pd.to_numeric, errors='coerce')
            df_temp = df_temp[df_temp['Numero'].notna()]
            #
            # Acertando tipo de colunas do dataframe
            df_temp[list_columns_float] = df_temp[list_columns_float].astype(float)
            cols = ['Numero']
            df_temp[cols] = df_temp[cols].astype(int)
            df_temp = df_temp.reset_index(drop=True)
            #
            df_temp.to_csv(path_csv, sep=";", decimal=",", encoding='utf-8')
            dic_dfs[filename_result] = df_temp

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - TRANSFORMANDO RELATÓRIOS TXT ANAFAS PARA DF")
        return dic_dfs

    def __importsReportsCC(self):
        r"""
        Responsável por importar os relatórios csv na pasta
        """
        start_time = time.time()
        dic_dfs = {}
        for file in os.listdir(self.path_decks):
            # Checando se o arquivo bate com as especificações
            if file[:1] != "_" and file[-4:] == ".csv":
                df_temp = pd.read_csv(self.path_decks + file, sep=";", decimal=",", encoding='utf-8', index_col=0)
                dic_dfs[file[:-4]] = df_temp

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - IMPORTANDO RELATÓRIOS TXT ANAFAS PARA DF")
        return dic_dfs

    def runNivelCC(self, resultskA = True, resultsMva = True):
        r"""
        Responsável por gerar na pasta dos arquivos .ANA, os dataframes dos resultados
        da avaliação do nível de curto-circuito
        """
        # O primeiro passo é gerar o arquivo .INP, que é o deck que irá alimentar o ANAFAS
        path_INP = self.__generateINPfile(resultskA, resultsMva)

        # O próximo passo é executar o deck .INP
        if self.newRun:
            print("--- AGUARDANDO EXECUÇÃO ANAFAS...")
            self.__exeCommandAnafas(path_INP)
            # Finalmente, o passo final é transformar os resultados do formato .TXT para .CSV
            dic_dfs = self.__transformReportsCC()
        else:
            dic_dfs = self.__importsReportsCC()


        return dic_dfs

    ###================================================================================================================
    ###
    ### CÓDIGOS PARA OBTER A COMPARAÇÃO DO NÍVEL DE CURTO-CIRCUITO
    ###
    ###================================================================================================================
    def __ask_reference_case(self, lista_casos):
        list_Cases = []
        print("\nLista de casos disponíveis para escolha de referência:")
        for i in range(0, len(lista_casos)):
            option = f"[{i}]. {lista_casos[i]}"
            list_Cases.append(option)
            print(option)

        print("Informar o número [x] do caso que deseja selecionar como referência:")
        user_casos = int(input()) + 3

        return user_casos

    def __increasedf(self, col_NCC, df_fix, df_to_increase, key, df):
        r"""
        Responsável por executar o comando de passar o deck INP dentro do Anafas
        """
        list_cols = ['Numero']
        list_cols.append(col_NCC)
        df_values = df[list_cols]
        df_values.columns = [(key[:-3] + '_' + col) if col != 'Numero' else col for col in df_values.columns]
        if df_to_increase.empty:
            df_to_increase = pd.merge(df_fix, df_values)
        else:
            df_to_increase = pd.merge(df_to_increase, df_values, how='outer')

        return df_to_increase

    def __auxDF_PercentualEvol(self, NCC_old,NCC_new):
        r"""
        Função auxiliar a ser vetorizada pelo DataFrame"""
        if str(NCC_old) != "-" and str(NCC_new) != "-" and NCC_old != 0:
            return round(100*((NCC_new-NCC_old)/NCC_old),3)
        else:
            return np.nan

    def __complementdfevol(self, df_comp):
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
        # df_result.to_csv(self.path_decks + grandeza + "_comparador.csv", sep=";", decimal=",", encoding='utf-8')

        return df_result

    def __complementdfevol(self, df_comp):
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
        # df_result.to_csv(self.path_decks + grandeza + "_comparador.csv", sep=";", decimal=",", encoding='utf-8')

        return df_result

    def __getdfevol(self, df_NCC,fixed_columns, reference_case, typeReference):
        r"""
        Função auxiliar a ser vetorizada pelo DataFrame"""
        #
        df_NCC_evol = df_NCC[fixed_columns]

        for i in range(3,len(df_NCC.columns)):
            if typeReference == 0:
                col_referencia = df_NCC.columns[reference_case]
            elif i == 3:
                col_referencia = df_NCC.columns[i]
            else:
                col_referencia = df_NCC.columns[i-1]
            #
            col_novovalor = df_NCC.columns[i]
            col_evol = "evol_" + df_NCC.columns[i]

            df_temp = df_NCC[[col_referencia, col_novovalor]].copy()
            df_temp[col_evol] = np.vectorize(self.__auxDF_PercentualEvol)(df_NCC[col_referencia], df_NCC[col_novovalor])
            df_temp.columns = ["A","B", col_evol]
            df_temp = df_temp.rename(columns={"A": "ref_" + col_referencia, "B": "comp_" + col_novovalor})
            if i > 3:
                df_temp = df_temp.iloc[:,1:]
            df_NCC_evol = pd.merge(df_NCC_evol, df_temp, left_index=True, right_index=True)

        df_NCC_evol_mod = self.__complementdfevol(df_NCC_evol)

        return df_NCC_evol_mod

    def compareNivelCC(self, dic_dfs, lista_casos, typeReference, resultskA = True, resultsMva = True):
        r"""
        Responsável por gerar na pasta dos arquivos .ANA, os dataframes dos resultados
        da avaliação do nível de curto-circuito
        """
        # Caso de referência
        if typeReference == 0:
            reference_case = self.__ask_reference_case(lista_casos)
        else:
            reference_case = None

        start_time = time.time()
        fixed_columns=['Numero', 'Nome', 'Tensao_Base']
        # Dataframes futuros
        df_NCC3f_kA = pd.DataFrame()
        df_NCC2f_kA = pd.DataFrame()
        df_NCC1f_kA = pd.DataFrame()
        df_NCC3f_Mva = pd.DataFrame()
        df_NCC2f_Mva = pd.DataFrame()
        df_NCC1f_Mva = pd.DataFrame()
        #
        list_dfs = []
        excel_path = []
        # Dataframes discriminados dos Níveis de CC
        for key, df in dic_dfs.items():
            type_df = key[-3:]
            df_fix = df[fixed_columns]
            #
            if type_df == "_KA":
                df_NCC3f_kA = self.__increasedf('kA_CC3F', df_fix, df_NCC3f_kA, key, df)
                df_NCC2f_kA = self.__increasedf('kA_CC2F', df_fix, df_NCC2f_kA, key, df)
                df_NCC1f_kA = self.__increasedf('kA_CC1F', df_fix, df_NCC1f_kA, key, df)

            if type_df == "MVA":
                df_NCC3f_Mva = self.__increasedf('Mva_CC3F', df_fix, df_NCC3f_Mva, key, df)
                df_NCC2f_Mva = self.__increasedf('Mva_CC2F', df_fix, df_NCC2f_Mva, key, df)
                df_NCC1f_Mva = self.__increasedf('Mva_CC1F', df_fix, df_NCC1f_Mva, key, df)

        # Calcula evoluções - kA
        if resultskA:
            df_NCC3f_kA_evol = self.__getdfevol(df_NCC3f_kA,fixed_columns, reference_case, typeReference)
            df_NCC2f_kA_evol = self.__getdfevol(df_NCC2f_kA,fixed_columns, reference_case, typeReference)
            df_NCC1f_kA_evol = self.__getdfevol(df_NCC1f_kA,fixed_columns, reference_case, typeReference)
            #
            df_NCC3f_kA_evol.to_csv(self.path_decks + "_compara_NCC3f_kA.csv", sep=";", decimal=",", encoding='utf-8')
            df_NCC2f_kA_evol.to_csv(self.path_decks + "_compara_NCC2f_kA.csv", sep=";", decimal=",", encoding='utf-8')
            df_NCC1f_kA_evol.to_csv(self.path_decks + "_compara_NCC1f_kA.csv", sep=";", decimal=",", encoding='utf-8')
            #
            list_dfs = [df_NCC3f_kA_evol, df_NCC2f_kA_evol, df_NCC1f_kA_evol]
            excel_path = [self.path_decks + "_compara_NCC3f_kA.xlsx", self.path_decks + "_compara_NCC2f_kA.xlsx", self.path_decks + "_compara_NCC1f_kA.xlsx"]

        if resultsMva:
            df_NCC3f_Mva_evol = self.__getdfevol(df_NCC3f_Mva,fixed_columns, reference_case, typeReference)
            df_NCC2f_Mva_evol = self.__getdfevol(df_NCC2f_Mva,fixed_columns, reference_case, typeReference)
            df_NCC1f_Mva_evol = self.__getdfevol(df_NCC1f_Mva,fixed_columns, reference_case, typeReference)
            #
            df_NCC3f_Mva_evol.to_csv(self.path_decks + "_compara_NCC3f_Mva.csv", sep=";", decimal=",", encoding='utf-8')
            df_NCC2f_Mva_evol.to_csv(self.path_decks + "_compara_NCC2f_Mva.csv", sep=";", decimal=",", encoding='utf-8')
            df_NCC1f_Mva_evol.to_csv(self.path_decks + "_compara_NCC1f_Mva.csv", sep=";", decimal=",", encoding='utf-8')
            #
            if resultskA:
                list_dfs = [df_NCC3f_kA_evol, df_NCC2f_kA_evol, df_NCC1f_kA_evol, df_NCC3f_Mva_evol, df_NCC2f_Mva_evol, df_NCC1f_Mva_evol]
                excel_path = [self.path_decks + "_compara_NCC3f_kA.xlsx", self.path_decks + "_compara_NCC2f_kA.xlsx", self.path_decks + "_compara_NCC1f_kA.xlsx",
                              self.path_decks + "_compara_NCC3f_Mva.xlsx", self.path_decks + "_compara_NCC2f_Mva.xlsx", self.path_decks + "_compara_NCC1f_Mva.xlsx"]
            else:
                list_dfs = [df_NCC3f_Mva_evol, df_NCC2f_Mva_evol, df_NCC1f_Mva_evol]
                excel_path = [self.path_decks + "_compara_NCC3f_Mva.xlsx", self.path_decks + "_compara_NCC2f_Mva.xlsx", self.path_decks + "_compara_NCC1f_Mva.xlsx"]

        print(f"--- {round((time.time() - start_time),3)} seconds --- FUNÇÃO: EXECUÇÃO PYTHON - COMPARAÇÃO ARQUIVOS NCC")
        return list_dfs, excel_path

    ###================================================================================================================
    ###
    ### CÓDIGOS EXPORT DATAFRAME
    ###
    ###================================================================================================================

    def plot_table_Excel(self, GrandMonit, list_df_GrandMonit):
        r"""
        Cria um arquivo excel com tabela a partir de um DataFrame

        Parameters
        ----------
        df: Pandas.DataFrame
            DataFrame com dados a serem plotados
        Title: Diretório do Arquivo
            Arquivo excel a ser gerado

        Examples
        --------
        >>> Import CEPEL_Tools as cp
        >>> ...
        >>> excel_df_tensao = r"D:\_APAGAR\LIXO\df_tensao.xlsx"
        >>> df_Tensao = oAnarede.plot_table_Excel(df_Tensao, excel_df_tensao)
        """
        start_time = time.time()
        print("--- INICIANDO CONVERSÃO PARA EXCEL...")

        for j in range(0, len(GrandMonit)):
            df = list_df_GrandMonit[j]
            Title = GrandMonit[j]

            writer = pd.ExcelWriter(Title, engine='xlsxwriter')
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

            print(f"--- {round((time.time() - start_time),3)} seconds --- TEMPO PYTHON: CRIAÇÃO DOS ARQUIVO EXCEL: {GrandMonit[j]}")
            start_time= time.time()

        # print("--- %s seconds --- FUNÇÃO: EXECUÇÃO PYTHON - GERANDO EXCEL DF GRANDEZAS" % (time.time() - start_time))




