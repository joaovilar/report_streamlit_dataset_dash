from dataset import df
import pandas as pd

def format_number(value, prefix=''):
    # Se o valor for menor que mil, formata com 2 casas decimais
    if value < 1000:
        return f'{prefix} {value:,.2f}'.replace(',', '.')
    
    # Para valores acima de mil, divide e formata conforme a unidade
    for unit in ['', 'mil', 'milhão', 'bilhão']:
        if value < 1000:
            return f'{prefix} {value:,.2f} {unit}'.replace(',', '.')
        value /= 1000
    
    return f'{prefix} {value:,.2f} bilhões'.replace(',', '.')

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




