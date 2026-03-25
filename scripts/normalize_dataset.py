import os
import pandas as pd

SRC = os.path.join('data', 'raw', 'eleições.csv')
DST_DIR = os.path.join('data', 'processed')
DST = os.path.join(DST_DIR, 'dataset_eleicoes.csv')


def normalize():
    os.makedirs(DST_DIR, exist_ok=True)
    if not os.path.exists(SRC):
        print(f"Arquivo de origem não encontrado: {SRC}")
        return

    # tenta ler com diferentes encodings se necessário
    df = pd.read_csv(SRC)

    # renomeia colunas conhecidas para o padrão esperado pelo pipeline
    mapping = {
        'Claim': 'texto',
        'Claim ': 'texto',
        'Source Name': 'fonte',
        'Source URL': 'source_url',
        'Verdict': 'veredito',
        'Review Publication Date': 'data',
        'Image URL': 'image_url',
        'Tags': 'tags'
    }

    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})

    # garantir colunas básicas
    if 'texto' not in df.columns:
        # tenta usar a primeira coluna textual
        for c in df.columns:
            if df[c].dtype == object:
                df = df.rename(columns={c: 'texto'})
                break

    if 'veredito' not in df.columns:
        # tentar inferir de colunas comuns
        for c in ['Verdict', 'verdict', 'rating', 'Rating']:
            if c in df.columns:
                df = df.rename(columns={c: 'veredito'})
                break

    # normalize valores de veredito para minúsculas (ajuste no treinamento)
    if 'veredito' in df.columns:
        df['veredito'] = df['veredito'].astype(str).str.strip()

    df.to_csv(DST, index=False, encoding='utf-8')
    print(f"Dataset normalizado salvo em: {DST} ({len(df)} linhas)")


if __name__ == '__main__':
    normalize()
