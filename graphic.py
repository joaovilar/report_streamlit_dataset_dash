import plotly.express as px
import pandas as pd
import streamlit as st

def create_graphics(filtered_df):
    # Verificar se 'Data_da_Ocorrencia' é um tipo de data e garantir que está em formato adequado
    if 'Data_da_Ocorrencia' in filtered_df.columns:
        # Garantir que a coluna 'Data_da_Ocorrencia' é de tipo datetime
        filtered_df['Data_da_Ocorrencia'] = pd.to_datetime(filtered_df['Data_da_Ocorrencia'], errors='coerce')
        
        # Remover ou lidar com valores nulos, se houver
        filtered_df = filtered_df.dropna(subset=['Data_da_Ocorrencia'])

        # Gráfico de barras para quantidade de ocorrências por UF
        grafico_barra_uf = px.bar(
            filtered_df.groupby('UF').size().reset_index(name='Numero_da_Ocorrencia'),
            x='UF',
            y='Numero_da_Ocorrencia',
            title="Quantidade de Ocorrências por UF"
        )
        st.plotly_chart(grafico_barra_uf, use_container_width=True)

        # Gráfico de linhas para quantidade de ocorrências mensal
        # Verificando se 'Data_da_Ocorrencia' está no formato datetime
        df_mensal = filtered_df.groupby(filtered_df['Data_da_Ocorrencia'].dt.to_period('M')).size().reset_index(name='Ocorrências')
        
        # Garantir que a coluna 'Data_da_Ocorrencia' está como string ou datetime após o groupby
        df_mensal['Data_da_Ocorrencia'] = df_mensal['Data_da_Ocorrencia'].astype(str)  # Garantindo compatibilidade com Plotly

        grafico_qtd_mensal = px.line(
            df_mensal,
            x='Data_da_Ocorrencia',
            y='Ocorrências',
            title='Quantidade de Ocorrências Mensal (Totalizado)'
        )
        st.plotly_chart(grafico_qtd_mensal, use_container_width=True)

        # Gráfico de pizza para distribuição por classificação
        grafico_pizza = px.pie(
            filtered_df.groupby('Classificacao_da_Ocorrência').size().reset_index(name='Quantidade'),
            names='Classificacao_da_Ocorrência',
            values='Quantidade',
            title='Distribuição de Ocorrências por Classificação'
        )
        st.plotly_chart(grafico_pizza, use_container_width=True)

        # Gráfico de barras horizontal para operações
        grafico_barra_operacao = px.bar(
            filtered_df.groupby('Operacao').size().reset_index(name='Quantidade'),
            y='Operacao',
            x='Quantidade',
            orientation='h',
            title='Quantidade de Ocorrências por Operação'
        )
        st.plotly_chart(grafico_barra_operacao, use_container_width=True)

# Exemplo de como o código pode ser usado (substitua 'filtered_df' pelo seu DataFrame real)
if __name__ == "__main__":
    # Supondo que você já tenha o DataFrame 'filtered_df' disponível com os dados processados
    create_graphics(filtered_df)
