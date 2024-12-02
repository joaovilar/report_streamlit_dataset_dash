import plotly.express as px
from utils import df_qt_ocorrencia_uf, format_number, df_qtd_ano  # Importando os dados do utils
import pandas as pd

# Ordenando o DataFrame antes de passar para o gráfico (ordem crescente de 'Numero_da_Ocorrencia')
df_qt_ocorrencia_uf = df_qt_ocorrencia_uf.sort_values('Numero_da_Ocorrencia', ascending=False)

# Criando o gráfico de barras
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

# Criar o gráfico de linhas com os dados agrupados
grafico_qtd_mensal = px.line(
    df_qtd_mensal_agrupado,  # DataFrame agrupado e ordenado
    x='Mês_Ordenado',
    y='Numero_da_Ocorrencia',
    markers=True,
    title='Quantidade de Ocorrências Mensal (Totalizado)'
)
