from pathlib import Path

import pandas as pd

try:
    from ftfy import fix_text as ftfy_fix_text
except Exception:
    ftfy_fix_text = None


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
DST_DIR = BASE_DIR / "data" / "processed"
DST = DST_DIR / "dataset_eleicoes.csv"

EXPECTED_COLUMNS = ["texto", "fonte", "source_url", "veredito", "data", "image_url", "tags"]


def _find_source_file() -> Path:
    candidates = sorted(RAW_DIR.glob("elei*.csv"))
    if candidates:
        return candidates[0]
    raise FileNotFoundError(f"Nenhum CSV bruto encontrado em {RAW_DIR}")


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
        return txt.count("Ãƒ") + txt.count("Ã‚") + txt.count("ï¿½")

    candidates = [value]
    for enc in ("latin-1", "cp1252"):
        try:
            candidates.append(value.encode(enc).decode("utf-8"))
        except Exception:
            pass

    manual_replacements = {
        "ÃƒÂ¡": "á", "ÃƒÃ ": "à", "ÃƒÃ¢": "â", "ÃƒÃ£": "ã",
        "ÃƒÂ©": "é", "ÃƒÃª": "ê",
        "ÃƒÃ­": "í",
        "ÃƒÂ³": "ó", "ÃƒÃ´": "ô", "ÃƒÃµ": "õ",
        "ÃƒÂº": "ú",
        "ÃƒÂ§": "ç",
        "Ã¢â‚¬Å“": '"', "Ã¢â‚¬": '"', "Ã¢â‚¬Ëœ": "'", "Ã¢â‚¬â„¢": "'",
        "Ã¢â‚¬â€œ": "-", "Ã¢â‚¬â€": "-",
    }
    repaired = value
    for old, new in manual_replacements.items():
        repaired = repaired.replace(old, new)
    candidates.append(repaired)

    return min(candidates, key=score).strip()


def _ground_truth_rows() -> list[dict[str, str]]:
    tse = "https://www.tse.jus.br"
    planalto = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
    rows = [
        ("O Tribunal Superior Eleitoral organiza as eleicoes no Brasil.", "TSE", tse),
        ("A Justica Eleitoral brasileira e responsavel pela administracao das eleicoes.", "TSE", tse),
        ("O voto no Brasil e secreto.", "Constituicao Federal", planalto),
        ("O voto e obrigatorio para brasileiros alfabetizados entre 18 e 70 anos.", "Constituicao Federal", planalto),
        ("O voto e facultativo para jovens de 16 e 17 anos.", "Constituicao Federal", planalto),
        ("O voto e facultativo para pessoas com mais de 70 anos.", "Constituicao Federal", planalto),
        ("O voto e facultativo para pessoas analfabetas.", "Constituicao Federal", planalto),
        ("As urnas eletronicas sao usadas no Brasil desde 1996.", "TSE", tse),
        ("O boletim de urna e emitido ao fim da votacao na secao eleitoral.", "TSE", tse),
        ("O TSE divulga resultados oficiais das eleicoes brasileiras.", "TSE", tse),
        ("A eleicao presidencial brasileira ocorre a cada quatro anos.", "Constituicao Federal", planalto),
        ("O mandato presidencial no Brasil tem duracao de quatro anos.", "Constituicao Federal", planalto),
        ("Pode haver segundo turno para presidente quando nenhum candidato alcanca maioria absoluta.", "Constituicao Federal", planalto),
        ("Pode haver segundo turno para governador quando nenhum candidato alcanca maioria absoluta.", "Constituicao Federal", planalto),
        ("Pode haver segundo turno para prefeito em municipios com mais de duzentos mil eleitores.", "Constituicao Federal", planalto),
        ("Partidos politicos precisam de registro para disputar eleicoes.", "TSE", tse),
        ("Candidaturas sao registradas na Justica Eleitoral.", "TSE", tse),
        ("Eleitores podem justificar ausencia quando nao votam.", "TSE", tse),
        ("Mesarios trabalham nas secoes eleitorais durante a votacao.", "TSE", tse),
        ("A propaganda eleitoral e regulada pela legislacao eleitoral.", "TSE", tse),
        ("A biometria e usada pela Justica Eleitoral para identificar eleitores cadastrados.", "TSE", tse),
        ("Votos brancos e nulos nao sao contabilizados para candidatos.", "TSE", tse),
        ("Deputados federais sao eleitos pelo sistema proporcional.", "TSE", tse),
        ("Vereadores sao eleitos pelo sistema proporcional.", "TSE", tse),
        ("Senadores sao eleitos pelo sistema majoritario.", "TSE", tse),
        ("Governadores sao eleitos pelo sistema majoritario.", "TSE", tse),
        ("Presidentes sao eleitos pelo sistema majoritario.", "TSE", tse),
        ("Prefeitos sao eleitos pelo sistema majoritario.", "TSE", tse),
        ("O eleitor deve apresentar documento oficial para votar.", "TSE", tse),
        ("A urna eletronica registra votos de forma digital.", "TSE", tse),
        ("A apuracao oficial das eleicoes e feita pela Justica Eleitoral.", "TSE", tse),
        ("As eleicoes municipais escolhem prefeitos e vereadores.", "TSE", tse),
        ("As eleicoes gerais escolhem presidente, governadores, senadores e deputados.", "TSE", tse),
        ("O primeiro turno das eleicoes ocorre no primeiro domingo de outubro.", "Constituicao Federal", planalto),
        ("O segundo turno das eleicoes ocorre no ultimo domingo de outubro quando necessario.", "Constituicao Federal", planalto),
        ("A posse do presidente eleito ocorre em primeiro de janeiro.", "Constituicao Federal", planalto),
        ("A idade minima para votar no Brasil e dezesseis anos.", "Constituicao Federal", planalto),
        ("A idade minima para disputar a Presidencia da Republica e trinta e cinco anos.", "Constituicao Federal", planalto),
        ("A idade minima para disputar o Senado Federal e trinta e cinco anos.", "Constituicao Federal", planalto),
        ("A idade minima para disputar o cargo de deputado federal e vinte e um anos.", "Constituicao Federal", planalto),
        ("A idade minima para disputar o cargo de prefeito e vinte e um anos.", "Constituicao Federal", planalto),
        ("A idade minima para disputar o cargo de vereador e dezoito anos.", "Constituicao Federal", planalto),
        ("O alistamento eleitoral e obrigatorio para maiores de dezoito anos alfabetizados.", "Constituicao Federal", planalto),
        ("O alistamento eleitoral e facultativo para maiores de setenta anos.", "Constituicao Federal", planalto),
        ("A Justica Eleitoral possui zonas eleitorais e secoes eleitorais.", "TSE", tse),
        ("A urna eletronica brasileira permite voto para diferentes cargos na mesma eleicao.", "TSE", tse),
        ("O eleitor pode consultar seu local de votacao nos canais da Justica Eleitoral.", "TSE", tse),
        ("A diplomacao confirma que candidatos eleitos estao aptos a tomar posse.", "TSE", tse),
        ("A prestacao de contas de campanha e fiscalizada pela Justica Eleitoral.", "TSE", tse),
        ("Doacoes eleitorais seguem regras definidas pela legislacao eleitoral.", "TSE", tse),
        ("Pesquisas eleitorais precisam ser registradas na Justica Eleitoral.", "TSE", tse),
        ("A urna eletronica nao e conectada diretamente a internet durante a votacao.", "TSE", tse),
    ]
    return [
        {
            "texto": text,
            "fonte": source,
            "source_url": url,
            "veredito": "VERDADEIRO",
            "data": "",
            "image_url": "",
            "tags": "['ground_truth', 'eleicoes']",
        }
        for text, source, url in rows
    ]


def _map_label(value: str):
    if pd.isna(value):
        return None

    text = str(value).lower().strip()
    negative_tokens = [
        "false", "falso", "falsa", "mentira", "errado", "enganoso", "enganador",
        "distorcido", "fora de contexto", "fake", "fraude", "nao", "não", "no",
        "0", "engano", "faux", "insustentavel", "insustentável",
    ]
    positive_tokens = [
        "true", "verdade", "verificado", "comprovado", "confirmado", "correto",
        "verdadeiro", "sim", "yes", "1", "contextualizando",
    ]

    if any(token in text for token in negative_tokens):
        return "FALSO"
    if any(token in text for token in positive_tokens):
        return "VERDADEIRO"

    try:
        numeric = float(text)
        return "VERDADEIRO" if numeric > 0.5 else "FALSO"
    except Exception:
        return None


def _is_conflict_marker(value: str) -> bool:
    text = value.strip()
    return text == "=======" or text.startswith("<<<<<<<") or text.startswith(">>>>>>>")


def normalize() -> None:
    DST_DIR.mkdir(parents=True, exist_ok=True)
    source_file = _find_source_file()

    with source_file.open("r", encoding="utf-8", errors="ignore") as file:
        header_line = file.readline()
    delimiter = "|" if "|" in header_line else ","

    try:
        df = pd.read_csv(source_file, sep=delimiter, encoding="utf-8", engine="python", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(source_file, sep=delimiter, encoding="latin-1", engine="python", on_bad_lines="skip")

    mapping = {
        "Claim": "texto",
        "Claim ": "texto",
        "Source Name": "fonte",
        "Source URL": "source_url",
        "Verdict": "veredito",
        "Review Publication Date": "data",
        "Image URL": "image_url",
        "Tags": "tags",
    }
    df = df.rename(columns={key: value for key, value in mapping.items() if key in df.columns})

    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            df[col] = df[col].apply(_fix_mojibake)

    if "texto" not in df.columns:
        text_col = next((col for col in df.columns if df[col].dtype == object), df.columns[0])
        df = df.rename(columns={text_col: "texto"})
    if "veredito" not in df.columns:
        label_col = next((col for col in ["Verdict", "verdict", "rating", "Rating"] if col in df.columns), None)
        if label_col:
            df = df.rename(columns={label_col: "veredito"})

    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[EXPECTED_COLUMNS]

    text_values = df["texto"].fillna("").astype(str).str.strip()
    df = df[text_values.ne("") & ~text_values.apply(_is_conflict_marker)].copy()
    df["veredito"] = df["veredito"].apply(_map_label)
    df = df[df["veredito"].notna()].copy()

    ground_truth = pd.DataFrame(_ground_truth_rows(), columns=EXPECTED_COLUMNS)
    df = pd.concat([df, ground_truth], ignore_index=True)
    df = df.drop_duplicates(subset=["texto", "fonte", "source_url"], keep="first")
    df = df.sort_values(["veredito", "fonte", "texto"], kind="stable").reset_index(drop=True)

    df.to_csv(DST, index=False, encoding="utf-8")
    print(f"Dataset normalizado salvo em: {DST} ({len(df)} linhas)")
    print(df["veredito"].value_counts().to_string())


if __name__ == "__main__":
    normalize()
