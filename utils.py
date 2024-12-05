from dataset import df
import pandas as pd

def format_number(value, prefix=''):
    return f'{prefix} {value:,}'.replace(',', '.')

# Garantir que a coluna 'Data_da_Ocorrencia' esteja no formato datetime
df['Data_da_Ocorrencia'] = pd.to_datetime(df['Data_da_Ocorrencia'], errors='coerce')

# Agrupando por 'Classificacao_da_Ocorrência' e contando o número de ocorrências
df_qt_ocorrencia = df.groupby('Classificacao_da_Ocorrência')['Numero_da_Ocorrencia'].count().reset_index()

# Ordenando pelo número de ocorrências em ordem crescente
df_qt_ocorrencia = df_qt_ocorrencia.sort_values('Numero_da_Ocorrencia', ascending=True)

# Agrupar por 'UF' e contar o número de ocorrências
df_qt_ocorrencia_uf = df.groupby('UF')['Numero_da_Ocorrencia'].count().reset_index()

# Ordenar pela quantidade de ocorrências em cada UF (ordem crescente)
df_qt_ocorrencia_uf = df_qt_ocorrencia_uf.sort_values('Numero_da_Ocorrencia', ascending=True)

# Dataframe da quantidade de ocorrências por Ano e Mês
df_qtd_ano = df.groupby(df['Data_da_Ocorrencia'].dt.to_period('M'))['Numero_da_Ocorrencia'].count().reset_index()

# Separando 'Ano' e 'Mês' das datas
df_qtd_ano['Ano'] = df_qtd_ano['Data_da_Ocorrencia'].dt.year
df_qtd_ano['Mês_num'] = df_qtd_ano['Data_da_Ocorrencia'].dt.month  # Extraímos o número do mês

# Mapeando o nome do mês a partir do número
df_qtd_ano['Mês'] = df_qtd_ano['Mês_num'].apply(lambda x: pd.Timestamp(f'2021-{x:02d}-01').strftime('%B'))

# Ordenando automaticamente por Ano e Mês sem precisar especificar a ordem manualmente
df_qtd_ano = df_qtd_ano.sort_values(['Ano', 'Mês_num'])


# Criando o DataFrame para o gráfico de pizza
df_pizza = df.groupby('Classificacao_da_Ocorrência')['Numero_da_Ocorrencia'].count().reset_index()
df_pizza = df_pizza.rename(columns={'Numero_da_Ocorrencia': 'Quantidade'})
df_pizza = df_pizza.sort_values('Quantidade', ascending=False)

tabela_agrupada_operacao = (
        df.groupby('Operacao')
        .size()
        .reset_index(name='Quantidade')
        .sort_values(by='Quantidade', ascending=True)
    )


