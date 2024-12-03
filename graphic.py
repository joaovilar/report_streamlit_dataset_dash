import plotly.express as px
import pandas as pd
from utils import df_qt_ocorrencia_uf, format_number, df_qtd_ano, df_pizza, tabela_agrupada_operacao  # Importando os dados do utils

# Ordenando o DataFrame antes de passar para o gráfico (ordem crescente de 'Numero_da_Ocorrencia')
df_qt_ocorrencia_uf = df_qt_ocorrencia_uf.sort_values('Numero_da_Ocorrencia', ascending=False)

# Criando o gráfico de barras para quantidade de ocorrências por UF
grafico_barra_uf = px.bar(
    df_qt_ocorrencia_uf,
    x='UF',  # Coluna de estados (UF)
    y='Numero_da_Ocorrencia',  # Coluna de número de ocorrências
    hover_name='UF',  # Exibirá a UF quando passar o mouse sobre a barra
    title="Quantidade de Ocorrências por UF",
    labels={"Numero_da_Ocorrencia": "Número de Ocorrências", "UF": "Estado (UF)"},
    template="plotly",  # Escolha o template do gráfico
)

# Garantir a ordem correta dos meses
df_qtd_ano['Mês_Ordenado'] = pd.Categorical(
    df_qtd_ano['Mês'], 
    categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ], 
    ordered=True
)

# Agrupando os dados por mês e somando as ocorrências
df_qtd_mensal_agrupado = (
    df_qtd_ano.groupby('Mês_Ordenado', as_index=False)['Numero_da_Ocorrencia']
    .sum()
    .sort_values('Mês_Ordenado')  # Ordenando os meses pela coluna 'Mês_Ordenado'
)

# Criar o gráfico de linhas para a quantidade de ocorrências mensal (totalizado)
grafico_qtd_mensal = px.line(
    df_qtd_mensal_agrupado,  # DataFrame agrupado e ordenado
    x='Mês_Ordenado',
    y='Numero_da_Ocorrencia',
    markers=True,
    title='Quantidade de Ocorrências Mensal (Totalizado)'
)

# Gráfico de pizza para distribuição de ocorrências por classificação
grafico_pizza = px.pie(
    df_pizza,
    names='Classificacao_da_Ocorrência',
    values='Quantidade',
    title='Distribuição de Ocorrências por Classificação',
    color_discrete_sequence=px.colors.sequential.RdBu  # Paleta de cores
)

# Criando o gráfico de barras horizontal para operações
grafico_barra_operacao = px.bar(
    tabela_agrupada_operacao,  # DataFrame da tabela agrupada
    y='Operacao',  # Operação no eixo Y
    x='Quantidade',  # Quantidade no eixo X
    orientation='h',  # Orientação horizontal
    title='Quantidade de Ocorrências por Operação',
    labels={"Operacao": "Operação", "Quantidade": "Número de Ocorrências"},
    template="plotly",  # Template padrão
    color='Quantidade',  # Adicionando cor com base na quantidade
    color_continuous_scale=px.colors.sequential.Viridis  # Escala de cores
)
