import streamlit as st
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
import io

# Função para conectar ao Data Lake
def connect_to_datalake(account_name, account_key):
    try:
        # Conectando ao Data Lake usando a URL formatada e a chave de acesso
        service_client = DataLakeServiceClient(account_url=f"https://{account_name}.dfs.core.windows.net", credential=account_key)
        return service_client
    except Exception as e:
        st.error(f"Erro ao conectar ao Azure Data Lake: {e}")
        return None

# Função para listar arquivos e pastas no Data Lake
def list_files_in_directory(service_client, filesystem_name):
    try:
        filesystem_client = service_client.get_file_system_client(filesystem_name)
        paths = filesystem_client.get_paths()  # Listar todos os arquivos e diretórios
        file_list = [path.name for path in paths]
        return file_list
    except Exception as e:
        st.error(f"Erro ao listar arquivos no Data Lake: {e}")
        return []

# Função para ler um arquivo JSON do Data Lake e convertê-lo para um DataFrame
def read_json_as_dataframe(service_client, filesystem_name, file_path):
    try:
        filesystem_client = service_client.get_file_system_client(filesystem_name)
        file_client = filesystem_client.get_file_client(file_path)
        download = file_client.download_file()
        file_content = download.readall()
        
        # Carregar o conteúdo do arquivo JSON em um DataFrame do Pandas
        data = pd.read_json(io.BytesIO(file_content))
        return data
    except Exception as e:
        st.error(f"Erro ao ler arquivo JSON do Data Lake: {e}")
        return None

# Definir a chave de acesso diretamente no código
account_name = "datalakebikestore"  # Nome da conta do Azure Storage
account_key = ""  # Sua chave de acesso

# Conectar ao Azure Data Lake
service_client = connect_to_datalake(account_name, account_key)

if service_client:
    # Definir o nome do seu filesystem (container no Azure Data Lake)
    filesystem_name = "json"  # Nome do seu sistema de arquivos (container)
    
    # Listar todos os arquivos e diretórios dentro do container
    file_list = list_files_in_directory(service_client, filesystem_name)
    
    # Verifique se o arquivo V_OCORRENCIA_AMPLA está listado
    file_name = "V_OCORRENCIA_AMPLA.json"  # Nome do arquivo JSON

    if file_name in file_list:
        # Ler o conteúdo do arquivo como DataFrame
        df = read_json_as_dataframe(service_client, filesystem_name, file_name)
        
        if df is not None:
            # Garantir que a coluna esteja no formato datetime
            df['Data_da_Ocorrencia'] = pd.to_datetime(df['Data_da_Ocorrencia'], errors='coerce')

            # Remover valores inválidos (NaT)
            df = df.dropna(subset=['Data_da_Ocorrencia'])

            # Adicionando estilo ao título
            st.markdown(
                """
                <style>
                .title {
                    background-color: #054f77; /* Cor de fundo */
                    padding: 60px;           /* Espaçamento interno */
                    border-radius: 10px;     /* Bordas arredondadas */
                    text-align: center;      /* Centralizar o texto */
                    color: white;            /* Cor do texto */
                    font-size: 40px;         /* Tamanho da fonte */
                }
                .logo-container {
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                }
                
                </style>
                """, 
                unsafe_allow_html=True
            )

            # Adicionando a imagem do logo
            logo_path = "image-vilar.png"  
            col1, col2 = st.columns([1, 8]) 

            with col1:
                try:
                    st.image(logo_path, width=80)  # Ajuste do tamanho da logo
                except FileNotFoundError:
                    st.error("Logo não encontrado. Verifique o caminho da imagem.")

            # Exibindo o título estilizado
            st.markdown('<div class="title">Relatório de informações da Anac</div>', unsafe_allow_html=True)

            # Filtro para "Operador"
            st.sidebar.title('Filtros')
            if 'Operador_Padronizado' in df.columns:
                filtro_operador = st.sidebar.multiselect(
                    'Operadores',
                    df['Operador_Padronizado'].unique()
                )

                # Aplicando o filtro no DataFrame
                if filtro_operador:
                    df = df[df['Operador_Padronizado'].isin(filtro_operador)]
            else:
                st.sidebar.warning("Coluna 'Operador_Padronizado' não encontrada no dataset.")

            # Filtro de UF
            if 'UF' in df.columns:
                filtro_uf = st.sidebar.multiselect(
                    'Unidade Federativa (UF)',
                    df['UF'].unique()
                )

                # Aplicando o filtro de UF
                if filtro_uf:
                    df = df[df['UF'].isin(filtro_uf)]
            else:
                st.sidebar.warning("Coluna 'UF' não encontrada no dataset.")

            # Filtro por Data da Ocorrência e converter para formato date
            min_date = df['Data_da_Ocorrencia'].min().date() 
            max_date = df['Data_da_Ocorrencia'].max().date()  

            date_range = st.sidebar.date_input(
                'Selecione o intervalo de datas de ocorrência',
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )

            # Aplicando o filtro de Data_da_Ocorrencia
            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['Data_da_Ocorrencia'] >= pd.Timestamp(start_date)) & (df['Data_da_Ocorrencia'] <= pd.Timestamp(end_date))]

            # Dividir em abas
            aba1, aba2 = st.tabs(['Dataset', 'Dashboard'])

            # Configuração da página para exibição paginada
            with aba1:
                st.subheader("Relatório Paginado")
                
                # Configuração para número de registros por página
                rows_per_page = 20
                total_rows = len(df)
                
                if total_rows == 0:
                    st.warning("Nenhum dado disponível após aplicar os filtros.")
                else:
                    # Calcular o número total de páginas
                    total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
                    
                    # Adicionar seletor de página (começando do 1)
                    current_page = st.number_input(
                        "Selecione a Página", min_value=1, max_value=total_pages, step=1, value=1, key="page_selector"
                    )
                    
                    # Determinar início e fim dos registros para a página atual
                    start_idx = (current_page - 1) * rows_per_page
                    end_idx = min(start_idx + rows_per_page, total_rows)  # Garante que não ultrapasse o total
                    
                    # Ajustar índice para começar em 1
                    paginated_df = df.iloc[start_idx:end_idx].reset_index(drop=True)
                    paginated_df.index += start_idx + 1
                    
                    # Exibir informações da página atual
                    st.write(f"Exibindo registros {start_idx + 1} a {end_idx} de {total_rows}")
                    st.dataframe(paginated_df,use_container_width=True)
        else:
            st.write("Não foi possível ler o conteúdo do arquivo.")
    else:
        st.write(f"O arquivo {file_name} NÃO foi encontrado!")
else:
    st.write("Nenhum arquivo encontrado no sistema de arquivos.")