import pandas as pd
p='data/dataset_eleicoes.csv'
try:
    df=pd.read_csv(p)
    print('cols:', df.columns.tolist())
    print('dtypes:', {c:str(df[c].dtype) for c in df.columns[:10]})
    print('first keys:', list(df.iloc[0].to_dict().keys())[:10])
except Exception as e:
    print('err', e)
