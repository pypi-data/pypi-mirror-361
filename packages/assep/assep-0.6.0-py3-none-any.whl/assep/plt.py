import pandas as pd
import numpy as np
import os
import time

class PLT():
    r"""   
    Classe destinada a trabalhar com arquivos de plotagem do ANATEM.

    É condensado nessa classe diversas ferramentas destinadas a facilitar a importação
    para dentro do código Python, facilitando a manipulação das curvas e execução de análises

    Parameters
    ----------
    Classe inicializada sem necessidade de parâmetros iniciais.

    Examples
    --------
    Para inicializar a classe, basta chamar ela para o objeto de interesse.

    >>> import CEPEL_Tools as cp
    >>> DadosPLT = cp.PLT()'
    """

    def __init__(self):
        pass
    ###================================================================================================================
    ###
    ### I/O
    ###
    ###================================================================================================================
    def __get_data_file(self, filename, type_encoding=""):
        r"""
        Função para coletar o arquivo PLT em uma lista a ser manipulada.

        Parameters
        ----------
        filename: str
            Nome do Arquivo com extensão ou Diretório Completo 

        Returns
        -------
        data: str 
            Variável string com texto contido em filename
            """
        if type_encoding == "":
            with open(filename) as file_object:
                data_file = file_object.readlines()
        elif type_encoding == "iso8859-1" :
            with open(filename, encoding='iso8859-1') as file_object:
                data_file = file_object.readlines()            

        return data_file

    def __get_legend_names(self, data_PLT, legenda_eixo_tempo, numero_curvas):
        r"""
        Obtém o nome das legendas das curvas dentro do PLT.

        Parameters
        ----------
        data_PLT: str
            Nome do Arquivo com extensão ou Diretório Completo 

        Returns
        -------
        data: str 
            Variável string com texto contido em filename
        """
        """Coleta para uma lista, todos os dados dentro de um PLT"""
        # Inicializo a lista com o nome do eixo X
        nome_curvas = [legenda_eixo_tempo]
        for line in data_PLT[2:]:
            if line[1:13] != "0.000000E+00":
            # if not line[1:13].isdigit():
                nome_curvas.append(line[:-2].strip())
            else:
                break
        return nome_curvas
    
    def __get_dados_array(self, data_PLT, numero_curvas):
        r"""
        Obtém uma lista contendo todos os dados do eixo Y das curvas no PLT.

        Parameters
        ----------
        data_PLT: str
            Lista com todos os dados do PLT

        numero_curvas: int
            Número de curvas presentes no eixo Y

        Returns
        -------
        dados_eixo_xy: list 
            Matriz com dados do PLT devidamenete convertidos em float
        """
        # Coletando os dados do eixo x e eixo y
        size_cols = int(data_PLT[0].strip())

        dados_curva_totais  = ''.join(data_PLT[numero_curvas+1:])
        dados_curva_totais = dados_curva_totais.replace("\n","").strip()
        dados_curva_totais = dados_curva_totais.split(" ")
        size_rows = int(len(dados_curva_totais) / (size_cols))

        dados_eixo_xy = np.zeros((size_rows,size_cols))

        # Povar eixo de dados
        for i in range(0, size_rows, 1):
            for j in range(0, size_cols, 1):
                dados_eixo_xy[i][j] = (float(dados_curva_totais[i*size_cols + j]))

        return dados_eixo_xy
        
    def get_data_PLT(self, filename, TimeAsIndex = True):
        r"""
        Função responsável por gerar um dataframe a partir de um arquivo PLT

        Pega todas as curvas disponíveis no PLT e converte elas em um DataFrame

        Parameters
        ----------
        filename: str
            Nome do Arquivo com extensão ou Diretório Completo
        TimeAsIndex: bool
            Dá a opção de gerar o DataFrame já utilizando o eixo do tempo como índice. Opção default como verdadeira.

        Returns
        -------
        data: str 
            Variável string com texto contido em filename

        Exemplos
        --------
        >>> data = self.__getTXTtoVariable(filename)
        """
        start_time = time.time()
        # Carregando para variáveis os dados dos arquivos:
        data_file_PLT = self.__get_data_file(filename)

        # Identificando número de curvas
        numero_curvas = int(data_file_PLT[0].rstrip())
        legenda_eixo_tempo = data_file_PLT[1].rstrip()

        # Coletando nome de cada curva
        nome_curvas = self.__get_legend_names(data_file_PLT, legenda_eixo_tempo, numero_curvas)
        
        print("--- %s seconds --- FUNÇÃO: IMPORTAR INFO CURVA" % (time.time() - start_time))
        start_time = time.time()

        # Coletando os dados do eixo x:
        dados_eixo_xy = self.__get_dados_array(data_file_PLT, numero_curvas)

        print("--- %s seconds --- FUNÇÃO: IMPORTAR DADOS CURVA" % (time.time() - start_time))

        # Criando dataframe do arquivo PLT
        df_PLT = pd.DataFrame(dados_eixo_xy, columns=nome_curvas)

        # Verifica se deseja inserir o tempo como index no dataframe
        if TimeAsIndex:
            df_PLT = df_PLT.set_index("Tempo - segundos")
            return df_PLT
        else:
            return df_PLT

    def __DFtoStrPLT(self, df_PLT):
        r"""
        Obtém uma string com todos os dados do dataframe no formato string compatível com o PLT.

        Parameters
        ----------
        df_PLT: Pandas DataFrame
            Pandas DataFrame com todos os dados do PLT

        Returns
        -------
        str_df: str 
            String com dados do PLT devidamenete convertidos no formato exponencial, formato DataFrame
        """
        # Formato exponencial a ser escrito no CSV
        custom_format = lambda x: ' {:0.{prec}E}'.format(x, prec=6 if x >= 0 else 5)
        # custom_format = lambda x: ' {{:.{}E}}'.format(6 if x >= 0 else 5).format(x)
        # Escrita no CSV do DataFrame
        df_PLT.to_csv("temp.txt", sep="#", float_format=custom_format,index=False, header=False)
        # Leitura dos dados do CSV para uma string
        with open('temp.txt', 'r') as file:
            str_df = (file.read())
            str_df = (str_df).replace("#0","# 0.000000E+00")
            str_df = (str_df).replace("#1","# 1.000000E+00")
            str_df = (str_df).replace("#","")
        # Elimina arquivo temporário criado
        os.remove("temp.txt")

        return str_df

    def __AdjustStrPLT(self, str_df):
        r"""
        Obtém uma string com todos os dados do dataframe no formato string compatível com o PLT.

        Parameters
        ----------
        str_df: str 
            String com dados do PLT devidamenete convertidos no formato exponencial, formato DataFrame

        Returns
        -------
        str_df_PLT: str 
            String com dados do PLT devidamenete convertidos no formato exponencial, formato PLT
        """
        # Converte string em list
        data_list = str_df.split('\n')
        data_list = [item.replace('\n', '') for item in data_list]
        # Monta string no formato PLT - 80 caracteres por linha
        for j in range(0, len(data_list)):
            siz_range = len(data_list[j]) + len(data_list[j])//79
            for i in range(0, siz_range,79):
                data_list[j] = data_list[j][:i+78] + "\n" + data_list[j][i+78:]
        # Consolida dados da curva
        str_df_PLT = ("\n".join(data_list)).replace("\n\n", "\n")

        return str_df_PLT

    def __MountPLT(self, numero_curvas, name_curvas, str_df_PLT):
        r"""
        Obtém uma string pronta para ser impressa no formato PLT.

        Parameters
        ----------
        numero_curvas: int 
            Total de curvas presente no DataFrame original
        name_curvas: str 
            String com a legenda de todas as curvas
        str_df_PLT: str 
            Dados de curvas presente no DataFrame original

        Returns
        -------
        str_PLT: str 
            String com dados do PLT pronto para serem impressos no formato PLT
        """
        # Número de Curvas
        str_PLT = " " + str(numero_curvas) + "\n"
        # Legendas
        str_PLT = str_PLT + "\n".join(name_curvas) + "\n"
        # Dados das Curvas
        str_PLT = str_PLT + str_df_PLT + "\n"

        return str_PLT

    def __PlotPLT(self, str_PLT, new_filename):
        r"""
        Obtém uma string pronta para ser impressa no formato PLT.

        Parameters
        ----------
        str_PLT: str 
            String com dados do PLT pronto para serem impressos no formato PLT
        new_filename: str 
            Nome do arquivo ou diretório completo do elemento impresso
        """
        # Inicia arquivo para ser escrito
        PLT_file = open(new_filename, "w")
        # Escreve string no arquivo
        n = PLT_file.write(str_PLT)
        # Fecha Arquivo
        PLT_file.close()  

    def generate_data_PLT(self, df_PLT, new_filename):
        r"""
        Função responsável por gerar um arquivo PLT a partir de um DataFrame

        Pega todas as curvas disponíveis no DataFrame, checa se o vetor de tempo está incluso e
        converte elas para o formato PLT

        Parameters
        ----------
        df_PLT: Pandas DataFrame
            Dataframe com dados de plotagem
        new_filename: str
            Nome do arquivo de saída

        Returns
        -------
        data: str 
            Variável string com texto contido em filename

        Exemplos
        --------
        >>> dados_PLT1.generate_data_PLT(dataframe_PLT1,outputfile1)
        """
        # Checando o index
        Eixo_Tempo = "Tempo - segundos"
        if Eixo_Tempo not in df_PLT:
            df_PLT = df_PLT.reset_index()

        #Obtém número de curvas
        numero_curvas = len(df_PLT.columns)

        # Obtém lista com todos os nomes das colunas do dataframe
        name_curvas = list(df_PLT.columns)
        name_curvas = list(map(str, name_curvas))      

        # Obtém dados no formato exponencial
        str_df = self.__DFtoStrPLT(df_PLT)

        # Adequa string de dados no formato e distribuição PLT
        str_df_PLT = self.__AdjustStrPLT(str_df)

        # Monta String a ser impressa no PLT
        str_PLT = self.__MountPLT(numero_curvas, name_curvas, str_df_PLT)

        # Escreve arquivo plt
        self.__PlotPLT(str_PLT, new_filename)        
    ###================================================================================================================
    ###
    ### MANIPULAÇÃO PLT
    ###
    ###================================================================================================================
    def interpolate2DFs(self, df_PLT1, df_PLT2):
        r"""
        Função responsável por fazer a interpolação linear entre dois PLTs com eixos do tempo diferentes

        Parameters
        ----------
        df_PLT: Pandas DataFrame
            Dataframe com dados da cruva - Arquivo 1 - Eixo X - Tipo 1
        df_PLT2: Pandas DataFrame
            Dataframe com dados da cruva - Arquivo 2 - Eixo X - Tipo 2

        Returns
        -------
        df_PLT: Pandas DataFrame
            Dataframe com dados da cruva - Arquivo 1 - Eixo X - Tipo Único
        df_PLT2: Pandas DataFrame
            Dataframe com dados da cruva - Arquivo 2 - Eixo X - Tipo Único

        Exemplos
        --------
        >>> df_PLT1, df_PLT2 = dadosPLT.interpolate2DFs(df_PLT1, df_PLT2)
        """
        # Checando o index
        Eixo_Tempo = "Tempo - segundos"
        flag_Index1 = False
        flag_Index2 = False
        if Eixo_Tempo in df_PLT1:
            df_PLT1 = df_PLT1.set_index(Eixo_Tempo)
            flag_Index1 = True
        if Eixo_Tempo in df_PLT2:
            df_PLT2 = df_PLT2.set_index(Eixo_Tempo)
            flag_Index2 = True

        # Adiciona sufixo para facilitar merge dos DFs
        df_PLT1 = df_PLT1.add_suffix('_PLT1')
        df_PLT2 = df_PLT2.add_suffix('_PLT2')

        # Merge dos DataFrames
        df_Total = pd.merge(df_PLT1,df_PLT2, left_index=True, right_index=True, how='outer')
        
        # Interpolação padrão
        df_Total = df_Total.interpolate()

        # SEPARO OS DATAFRAMES
        df_PLT1 = df_Total.filter(regex="_PLT1")
        df_PLT2 = df_Total.filter(regex="_PLT2")

        # Readequo os nomes dos DFs
        df_PLT1.columns = df_PLT1.columns.str.rstrip("_PLT1")
        df_PLT2.columns = df_PLT2.columns.str.rstrip("_PLT2")

        # Volta para opção de index
        if flag_Index1:
            df_PLT1 = df_PLT1.reset_index()
        if flag_Index2:
            df_PLT2 = df_PLT2.reset_index()

        return df_PLT1, df_PLT2

    def remove_cte_plt(self, file_plt):
        """"
        Remove curvas constantes
        """
        outputfile_plt = file_plt[:-4] + "_mod.plt"
        print(f"Iniciando manipulação do arquivo {file_plt}:\n")
        print("Importando dados do PLT para dataframe...\n")
        df_plt = self.get_data_PLT(file_plt)
        #
        print("Manipulando dataframe...\n")
        # Find columns with constant values
        constant_columns = df_plt.columns[df_plt.nunique() == 1]
        # Drop the columns with constant values
        df_plt_mod = df_plt.drop(columns=constant_columns)
        #
        column_diff = df_plt_mod.max() - df_plt_mod.min()
        filtered_columns = list(dict.fromkeys(list(column_diff[column_diff >= 0.001].index)))
        df_plt_mod_filt = df_plt_mod[filtered_columns]
        self.df = df_plt_mod_filt.copy()
        #
        # Cria arquivo novo
        print("Exportando dados do dataframe para PLT...\n")
        self.generate_data_PLT(df_plt_mod_filt, outputfile_plt)
