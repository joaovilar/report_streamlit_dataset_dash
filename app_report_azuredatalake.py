import streamlit as st
from utils import format_number
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
import io
from graphic import create_graphics  # Ajustei para consolidar os gráficos em uma função
from css import css
import plotly.express as px

# Configuração de layout
st.set_page_config(page_title="Report", layout="wide")

# Adicionando a imagem de logo
logo_path = "image-vilar.png"
st.image(logo_path, width=80, caption="Tecnologia")

# Função para conectar ao Data Lake
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

# Função para listar arquivos e pastas no Data Lake
@st.cache_data
def list_files_in_directory(_service_client, filesystem_name):
    try:
        filesystem_client = _service_client.get_file_system_client(filesystem_name)
        paths = filesystem_client.get_paths()
        return [path.name for path in paths]
    except Exception as e:
        st.error(f"Erro ao listar arquivos no Data Lake: {e}")
        return []

# Função para ler e processar arquivo JSON do Data Lake
@st.cache_data
def read_and_process_json(_service_client, filesystem_name, file_path):
    try:
        filesystem_client = _service_client.get_file_system_client(filesystem_name)
        file_client = filesystem_client.get_file_client(file_path)
        download = file_client.download_file()
        file_content = download.readall()
        
        data = pd.read_json(io.BytesIO(file_content), convert_dates=False)
        data['Data_da_Ocorrencia'] = pd.to_datetime(data['Data_da_Ocorrencia'], errors='coerce')
        return data.dropna(subset=['Data_da_Ocorrencia'])
    except Exception as e:
        st.error(f"Erro ao ler e processar o arquivo JSON: {e}")
        return None

# Configurações de conexão
account_name = "datalakebikestore"
account_key = "gdrO0Er/Ec8TslO1M7d9ENURLu4p9wov4GL7WrsCWP/Iwxca9I0amu1m1QIOTS57JcMeoZD4rrNA+AStGvOJJw=="  # Mover para variável de ambiente

service_client = connect_to_datalake(account_name, account_key)

if service_client:
    filesystem_name = "json"
    file_list = list_files_in_directory(service_client, filesystem_name)
    file_name = "V_OCORRENCIA_AMPLA.json"

    if file_name in file_list:
        df = read_and_process_json(service_client, filesystem_name, file_name)
        if df is not None:
            st.markdown(css, unsafe_allow_html=True)
            st.markdown('<div class="title">Relatório de Informações da ANAC</div>', unsafe_allow_html=True)

            # Sidebar para os filtros
            st.sidebar.header("Filtros")

            # Filtro de Operador Padronizado
            filtro_operador = st.sidebar.multiselect('Operadores', df['Operador_Padronizado'].unique())

            # Filtro de UF
            filtro_uf = st.sidebar.multiselect('Unidade Federativa (UF)', df['UF'].unique())

            # Filtro de Nome do Fabricante
            filtro_fabricante = st.sidebar.multiselect('Nome do Fabricante', df['Nome_do_Fabricante'].unique())

            # Filtro de intervalo de datas
            min_date, max_date = df['Data_da_Ocorrencia'].min().date(), df['Data_da_Ocorrencia'].max().date()
            date_range = st.sidebar.date_input(
                'Selecione o intervalo de datas de ocorrência',
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )

            # Filtros aplicados ao DataFrame
            filtered_df = df[
                (df['Operador_Padronizado'].isin(filtro_operador) if filtro_operador else True) &
                (df['UF'].isin(filtro_uf) if filtro_uf else True) &
                (df['Nome_do_Fabricante'].isin(filtro_fabricante) if filtro_fabricante else True) &
                (df['Data_da_Ocorrencia'].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])))
            ]

            # Dividir em abas
            aba1, aba2 = st.tabs(['Dataset', 'Dashboard'])

            # Exibição paginada no Dataset
            with aba1:
                st.markdown("<h2>Relatório Páginado</h2>", unsafe_allow_html=True)
                total_rows = len(filtered_df)
                rows_per_page = 20
                total_pages = -(-total_rows // rows_per_page)  # Arredondamento para cima
                current_page = st.number_input(
                    "Selecione a Página", min_value=1, max_value=total_pages, step=1, value=1
                )
                start_idx = (current_page - 1) * rows_per_page
                end_idx = min(start_idx + rows_per_page, total_rows)

                if total_rows:
                    st.write(f"Exibindo registros {start_idx + 1} a {end_idx} de {total_rows}")

                    # Sidebar para selecionar colunas a exibir
                    selected_columns = st.sidebar.multiselect(
                        'Selecione as colunas para exibir', df.columns.tolist(), default=df.columns.tolist()
                    )

                    # Exibir o DataFrame com as colunas selecionadas
                    st.dataframe(filtered_df[selected_columns].iloc[start_idx:end_idx].reset_index(drop=True), 
                                 use_container_width=True, height=600)

                else:
                    st.warning("Nenhum dado disponível após aplicar os filtros.")

            # Aba para Dashboard
            with aba2:
                st.markdown("<h2>Dashboard</h2>", unsafe_allow_html=True)
                st.metric("Quantidade de Ocorrências", format_number(len(filtered_df), prefix=""))
               
                # Chamando a função create_graphics para os outros gráficos
                create_graphics(filtered_df)

        else:
            st.error("Não foi possível processar os dados do arquivo.")
    else:
        st.error(f"O arquivo {file_name} não foi encontrado no Data Lake.")
else:
    st.error("Erro ao conectar ao Azure Data Lake.")
