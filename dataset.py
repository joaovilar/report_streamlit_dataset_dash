import json
import pandas as pd

with open('dados/V_OCORRENCIA_AMPLA.json', encoding='utf-8') as file:
    data = json.load(file)

df = pd.DataFrame(data)

print(df)
