import os
import pandas as pd

try:
    from ftfy import fix_text as ftfy_fix_text
except Exception:
    ftfy_fix_text = None

SRC = os.path.join('data', 'raw', 'eleições.csv')
DST_DIR = os.path.join('data', 'processed')
DST = os.path.join(DST_DIR, 'dataset_eleicoes.csv')


def _fix_mojibake(value):
    if not isinstance(value, str):
        return value

    if ftfy_fix_text is not None:
        try:
            fixed = ftfy_fix_text(value)
            if fixed:
                value = fixed
        except Exception:
            pass

    def score(txt: str) -> int:
        # Quanto menor, melhor (menos sinais de corrupção).
        return txt.count("Ã") + txt.count("Â") + txt.count("�")

    candidates = [value]

    for enc in ("latin-1", "cp1252"):
        try:
            candidates.append(value.encode(enc).decode("utf-8"))
        except Exception:
            pass

    for enc in ("latin-1", "cp1252"):
        try:
            candidates.append(value.encode(enc).decode("utf-8").encode(enc).decode("utf-8"))
        except Exception:
            pass

    manual_replacements = {
        "Ã¡": "á", "Ãà": "à", "Ãâ": "â", "Ãã": "ã", "Ãä": "ä",
        "ÃÁ": "Á", "ÃÀ": "À", "ÃÂ": "Â", "ÃÃ": "Ã", "ÃÄ": "Ä",
        "Ã©": "é", "Ãê": "ê", "ÃÉ": "É", "ÃÊ": "Ê",
        "Ãí": "í", "ÃÍ": "Í",
        "Ã³": "ó", "Ãô": "ô", "Ãõ": "õ", "ÃÓ": "Ó", "ÃÔ": "Ô", "ÃÕ": "Õ",
        "Ãº": "ú", "ÃÚ": "Ú",
        "Ã§": "ç", "Ã‡": "Ç",
        "Âº": "º", "Âª": "ª",
        "â€œ": '"', "â€": '"', "â€˜": "'", "â€™": "'", "â€“": "-", "â€”": "-",
    }
    repaired = value
    for old, new in manual_replacements.items():
        repaired = repaired.replace(old, new)
    candidates.append(repaired)

    best = min(candidates, key=score)
    return best.strip()


def normalize():
    os.makedirs(DST_DIR, exist_ok=True)
    if not os.path.exists(SRC):
        print(f"Arquivo de origem não encontrado: {SRC}")
        return

    # Detecta delimitador do arquivo bruto (pipe no dataset do professor).
    with open(SRC, "r", encoding="utf-8", errors="ignore") as f:
        header_line = f.readline()
    delimiter = "|" if "|" in header_line else ","

    try:
        df = pd.read_csv(SRC, sep=delimiter, encoding="utf-8", engine="python", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(SRC, sep=delimiter, encoding="latin-1", engine="python", on_bad_lines="skip")

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

    # Corrige texto com encoding quebrado em todas as colunas textuais.
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            df[col] = df[col].apply(_fix_mojibake)

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

    # Enriquecimento mínimo para reduzir viés de classe negativa.
    if 'texto' in df.columns and 'veredito' in df.columns:
        true_rows = [
            {
                'texto': 'O Tribunal Superior Eleitoral (TSE) e responsavel pela organizacao das eleicoes no Brasil.',
                'veredito': 'VERDADEIRO',
                'fonte': 'TSE',
                'source_url': 'https://www.tse.jus.br',
            },
            {
                'texto': 'Lula foi eleito presidente do Brasil em outubro de 2022.',
                'veredito': 'VERDADEIRO',
                'fonte': 'Governo Federal',
                'source_url': 'https://www.gov.br/pt-br/presidencia',
            },
            {
                'texto': 'O voto e obrigatorio para cidadaos alfabetizados entre 18 e 70 anos no Brasil.',
                'veredito': 'VERDADEIRO',
                'fonte': 'TSE',
                'source_url': 'https://www.tse.jus.br/eleitor/justificativa-eleitoral',
            },
            {
                'texto': 'As urnas eletronicas sao usadas no Brasil desde 1996.',
                'veredito': 'VERDADEIRO',
                'fonte': 'TSE',
                'source_url': 'https://www.tse.jus.br/comunicacao/noticias',
            },
            {
                'texto': 'Bolsonaro foi presidente do Brasil antes de Lula.',
                'veredito': 'VERDADEIRO',
                'fonte': 'Governo Federal',
                'source_url': 'https://www.gov.br/pt-br/presidencia',
            },
            {
                'texto': 'O segundo turno das eleicoes no Brasil ocorre em outubro.',
                'veredito': 'VERDADEIRO',
                'fonte': 'TSE',
                'source_url': 'https://www.tse.jus.br/eleicoes/calendario-eleitoral',
            },
        ]

        existing_texts = set(df['texto'].astype(str).str.strip().str.lower())
        to_add = []
        for row in true_rows:
            key = row['texto'].strip().lower()
            if key in existing_texts:
                continue
            row_full = {c: '' for c in df.columns}
            row_full.update({k: v for k, v in row.items() if k in row_full})
            to_add.append(row_full)

        if to_add:
            df = pd.concat([df, pd.DataFrame(to_add)], ignore_index=True)

    # normalize valores de veredito para minúsculas (ajuste no treinamento)
    if 'veredito' in df.columns:
        df['veredito_orig'] = df['veredito'].astype(str)
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
