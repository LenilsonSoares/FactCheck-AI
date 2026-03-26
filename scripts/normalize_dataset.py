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
        df['veredito_orig'] = df['veredito'].astype(str)
        s = df['veredito'].astype(str).str.lower().str.strip()

        positive_tokens = [
            "true", "verdade", "verificado", "comprovado", "confirmado", "correto", "verdadeiro", "sim", "yes", "1", "true"
        ]
        negative_tokens = [
            "false", "falso", "mentira", "errado", "enganoso", "enganador", "distorcido", "fora de contexto", "fake", "fraude", "não", "nao", "no", "0", "engano", "faux", "errado", "não_é_bem_assim", "não é bem assim", "não_é_bem_assim"
        ]

        def map_label(v: str):
            if pd.isna(v):
                return None
            vv = str(v).lower().strip()
            for tok in positive_tokens:
                if tok in vv:
                    return 'VERDADEIRO'
            for tok in negative_tokens:
                if tok in vv:
                    return 'FALSO'
            # try numeric
            try:
                nv = float(vv)
                return 'VERDADEIRO' if nv > 0.5 else 'FALSO'
            except Exception:
                return None

        df['veredito_norm'] = df['veredito_orig'].apply(map_label)
        kept = df['veredito_norm'].notna().sum()
        total = len(df)
        print(f"Rótulos mapeados: {kept}/{total} (serão mantidas apenas entradas mapeadas)")
        # manter apenas linhas mapeadas (reduz ruido)
        df = df[df['veredito_norm'].notna()].copy()
        # escrever o veredito normalizado em coluna 'veredito'
        df['veredito'] = df['veredito_norm']
        df = df.drop(columns=['veredito_orig', 'veredito_norm'])

    df.to_csv(DST, index=False, encoding='utf-8')
    print(f"Dataset normalizado salvo em: {DST} ({len(df)} linhas)")


if __name__ == '__main__':
    normalize()
