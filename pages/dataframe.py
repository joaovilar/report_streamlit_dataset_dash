import streamlit as st
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
import io

# Configuração da página
st.set_page_config(
    page_title="Exploração de Dataset", 
    layout="wide",)


st.title("Exploração de Dataset")

# Função para conectar ao Azure Data Lake
@st.cache_data
def connect_to_datalake(account_name, account_key):
    try:
        service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=account_key
        )
        return service_client
    except Exception as e:
        st.error(f"Erro ao conectar ao Azure Data Lake: {e}")
        return None

# Função para ler e processar o arquivo JSON do Data Lake
@st.cache_data
def read_and_process_json(_service_client, filesystem_name, file_path):
    try:
        filesystem_client = _service_client.get_file_system_client(filesystem_name)
        file_client = filesystem_client.get_file_client(file_path)
        download = file_client.download_file()
        file_content = download.readall()
        data = pd.read_json(io.BytesIO(file_content), convert_dates=False)
        return data
    except Exception as e:
        st.error(f"Erro ao ler e processar o arquivo JSON: {e}")
        return None

# Configuração do Azure Data Lake
account_name = "datalakebikestore"
account_key = "gdrO0Er/Ec8TslO1M7d9ENURLu4p9wov4GL7WrsCWP/Iwxca9I0amu1m1QIOTS57JcMeoZD4rrNA+AStGvOJJw=="
filesystem_name = "json"
file_name = "V_OCORRENCIA_AMPLA.json"

# Conectar ao Data Lake e carregar o dataset
service_client = connect_to_datalake(account_name, account_key)
if service_client:
    df = read_and_process_json(service_client, filesystem_name, file_name)
else:
    st.error("Erro ao conectar ou carregar os dados.")

# Exploração do dataset
if df is not None:
    st.sidebar.title("Configurações de Exploração")
    coluna_selecionada = st.sidebar.selectbox(
        "Selecione uma coluna para explorar:",
        options=["(Todas as colunas)"] + list(df.columns)
    )

    # Exibe DataFrame completo ou coluna específica
    st.subheader("Dataset Carregado")
    if coluna_selecionada == "(Todas as colunas)":
        st.dataframe(df)
    else:
        st.dataframe(df[[coluna_selecionada]])

    # Exibe História dos Dados para a coluna selecionada
    st.subheader("História dos Dados")
    if coluna_selecionada != "(Todas as colunas)":
        coluna = df[coluna_selecionada]
        nulos = coluna.isnull().sum()
        duplicados = coluna.duplicated().sum()
        valores_unicos = coluna.nunique()
        tipo_dado = coluna.dtype

        st.write(
            f"A coluna **'{coluna_selecionada}'** possui {nulos} valores nulos, "
            f"{duplicados} valores duplicados e contém {valores_unicos} valores únicos. "
            f"Os dados estão armazenados no tipo **{tipo_dado}**."
        )
    else:
        st.write("Selecione uma coluna para visualizar sua história.")

    # Exibe Informações Exploratórias
    st.subheader("Informações Exploratórias")
    if coluna_selecionada == "(Todas as colunas)":
        # Informações gerais para todo o DataFrame
        st.write("### Quantidade de valores nulos por coluna:")
        st.write(df.isnull().sum())

        st.write("### Quantidade de valores duplicados por coluna:")
        st.write(df.apply(lambda col: col.duplicated().sum()))

        st.write("### Tipo de dado por coluna:")
        st.write(df.dtypes)

        st.write("### Contagem de valores únicos por coluna:")
        st.write(df.nunique())
    else:
        # Informações detalhadas para a coluna selecionada
        st.write("### Quantidade de valores nulos:")
        st.write(df[coluna_selecionada].isnull().sum())

        st.write("### Quantidade de valores duplicados:")
        st.write(df[coluna_selecionada].duplicated().sum())

        st.write("### Tipo de dado:")
        st.write(df[coluna_selecionada].dtype)

        st.write("### Contagem de valores únicos:")
        st.write(df[coluna_selecionada].nunique())

    # Exibe Informações Estatísticas Descritivas
    st.subheader("Informações Estatísticas Descritivas")
    if coluna_selecionada == "(Todas as colunas)":
        st.write(df.describe())
        st.write("### Moda:")
        st.write(df.mode().iloc[0])  # Exibe a moda para todas as colunas
        st.write("### Mediana:")
        st.write(df.median(numeric_only=True))  # Exibe a mediana para colunas numéricas
    else:
        if pd.api.types.is_numeric_dtype(df[coluna_selecionada]):
            coluna_numerica = pd.to_numeric(df[coluna_selecionada], errors='coerce')
            st.write(coluna_numerica.describe())
            st.write("### Moda:")
            st.write(coluna_numerica.mode().iloc[0])  # Exibe a moda da coluna
            st.write("### Mediana:")
            st.write(coluna_numerica.median())  # Exibe a mediana da coluna
        else:
            st.warning(f"A coluna '{coluna_selecionada}' não contém valores numéricos.")
else:
    st.error("Não foi possível carregar o dataset.")
