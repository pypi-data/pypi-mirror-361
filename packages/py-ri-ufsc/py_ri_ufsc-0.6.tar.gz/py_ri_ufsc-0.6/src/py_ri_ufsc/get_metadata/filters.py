import pandas as pd
from . .common.for_strings import format_text

def clean_empty_rows(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Remove linhas com valores ausentes (NaN ou string vazia) nas colunas especificadas.
    """
    # Garante que os índices não estão duplicados
    df = df.copy()

    for col in columns:
        if col in df.columns:
            df = df.loc[df[col].notna() &(df[col] != '')].copy()
    
    df.reset_index(drop=True, inplace=True)
    return df


def filter_types(df: pd.DataFrame, types: list[str], exclude_empty_values: bool = True) -> pd.DataFrame:
    """
    Filtra o DataFrame com base na coluna 'type', mantendo apenas os registros cujo valor está na lista 'types'.
    Se 'include_empty' for True, também inclui linhas onde 'type' é string vazia "".
    """
    df = df.copy()
    # if not exclude_empty_values: # Comentando porque já foi tratado anteriormente
    #     df['type'].replace({'':'NÃO IDENTIFICADO'},inplace=True)
    # df = clean_empty_rows(df=df, columns=['type'])  # Assumindo que limpa NaN substituindo por ""
    
    if not exclude_empty_values:
        mask = df['type'].isin(types) | (df['type'] == 'NÃO ESPECIFICADO')
    else:
        mask = df['type'].isin(types)
    return df[mask]

def filter_dates(df: pd.DataFrame, date_1: int, date_2: int,exclude_empty_values : bool = True) -> pd.DataFrame:
    df = df.copy()
    
    if not exclude_empty_values:
        df_empty_values = df[(df['year']=='') | (df['year'].isna()) | (df['year'].isnull())]
        df_empty_values.loc[:, 'year'] = 'NÃO IDENTIFICADO'
        df = df.drop(df_empty_values.index)
    # Tenta converter para inteiro e remove valores inválidos
    df['year'] = pd.to_numeric(df['year'], errors='coerce')    
    df = clean_empty_rows(df=df,columns=['year'])  # Remove linhas que não puderam ser convertidas
    df['year'] = df['year'].astype(int)

    # Aplica filtro numérico
    filtered_df = df[(df['year'] >= date_1) & (df['year'] <= date_2)]

    if exclude_empty_values:
        return filtered_df
    else:
        return pd.concat([filtered_df,df_empty_values])

def filter_title_by_words(df: pd.DataFrame,
                          words: list[str],
                          match_all: bool = False,
                          exclude_empty_values: bool = True) -> pd.DataFrame:
    import re
    
    df = df.copy()

    # Isola os títulos vazios se for manter
    if not exclude_empty_values:
        df_empty_values = df[(df['title'] == '') | (df['title'].isna()) | (df['title'].isnull())].copy()
        df_empty_values.loc[:, 'title'] = 'NÃO IDENTIFICADO'
        df = df.drop(df_empty_values.index) # Remove do df principal para não aplicar filtro neles
    else:
        # Remove linhas com título vazio
        df = clean_empty_rows(df=df, columns=['title'])

    # Normaliza e escapa as palavras para regex
    words_formatted = [re.escape(format_text(word, special_treatment=True).strip()) for word in words]
    pattern = '|'.join(words_formatted)

    # Define a máscara de filtro
    if match_all:
        mask = df['title'].apply(
            lambda t: all(
                re.search(w, format_text(t, special_treatment=True), flags=re.IGNORECASE)
                for w in words_formatted
            )
        )
    else:
        mask = df['title'].apply(
            lambda t: re.search(pattern, format_text(t, special_treatment=True), flags=re.IGNORECASE) is not None
        )

    filtered = df[mask]

    if exclude_empty_values:
        return filtered
    else:
        # Retorna filtrados + os títulos originalmente vazios (agora com 'NÃO IDENTIFICADO')
        return pd.concat([filtered, df_empty_values])


def filter_subjects(df: pd.DataFrame,
                    subjects: list[str],
                    match_all: bool = False,
                    exclude_empty_values : bool = True) -> pd.DataFrame:
    df = df.copy()

    if not exclude_empty_values:
        df_empty_values = df[(df['subjects']=='') | (df['subjects'].isna()) | (df['subjects'].isnull())]
        df_empty_values.loc[:, 'subjects'] = 'NÃO IDENTIFICADO'
        df = df.drop(df_empty_values.index)
    else:
        # Remove linhas sem subjects
        df = clean_empty_rows(df=df,columns=['subjects'])

    # Normaliza os assuntos de entrada
    subjects_formatted = [format_text(s, special_treatment=True).strip() for s in subjects]

    # Função para verificar se algum assunto está presente
    def subject_match(row_subjects):
        row_subjects_split = row_subjects.split(';')
        row_subjects_formatted = [format_text(s.strip(), special_treatment=True) for s in row_subjects_split if s.strip()]
        if match_all:
            return all(any(word in subject for subject in row_subjects_formatted) for word in subjects_formatted)
        else:
            return any(any(word in subject for subject in row_subjects_formatted) for word in subjects_formatted)

    mask = df['subjects'].apply(subject_match)
    if exclude_empty_values:
        return df[mask]
    else:
        return pd.concat([df[mask],df_empty_values])

# Pega buscando "Igor Caetano" para authors = "Igor C Souza"
# Match all = True tem q conter todos os autores
def filter_authors(df: pd.DataFrame,
                   author_names: list[str],
                   match_all: bool = False,
                   exclude_empty_values : bool = True) -> pd.DataFrame:
    df = df.copy()

    if not exclude_empty_values:
        df_empty_values = df[(df['authors']=='') | (df['authors'].isna()) | (df['authors'].isnull())]
        df_empty_values.loc[:, 'authors'] = 'NÃO IDENTIFICADO'
        df = df.drop(df_empty_values.index)
    else:
        df = clean_empty_rows(df=df,columns=['authors'])

    # Normaliza e quebra os nomes buscados
    def extract_name_parts(name: str):
        words = [format_text(w.strip(), special_treatment=True) for w in name.split() if w.strip()]
        if not words:
            return None
        first = words[0]
        last = words[-1]
        last_initial = last[0] if last else ""
        return {"first": first, "last": last, "last_initial": last_initial}

    names_parts = [extract_name_parts(name) for name in author_names if name.strip()]

    def author_match(authors_raw):
        authors_list = authors_raw.split(';')
        authors_processed = [
            [format_text(part.strip(), special_treatment=True) for part in author.replace(',', ' ').split()]
            for author in authors_list
        ]

        matches = []
        for name in names_parts:
            if name is None:
                continue
            first, last, last_initial = name["first"], name["last"], name["last_initial"]

            matched = False
            for author_parts in authors_processed:
                has_first = first in author_parts
                has_last = (
                    last in author_parts or
                    f"{last_initial}." in author_parts or
                    last_initial in author_parts
                )
                if has_first and has_last:
                    matched = True
                    break

            matches.append(matched)

        return all(matches) if match_all else any(matches)

    mask = df['authors'].apply(author_match)
    if exclude_empty_values:
        return df[mask]
    else:
        return pd.concat([df[mask],df_empty_values])

# Pega buscando "Igor Caetano" para advisors = "Igor C Souza"
# Match all = True tem q conter todos os autores
def filter_advisors(df: pd.DataFrame,
                    advisor_names: list[str],
                    match_all: bool = False,
                    exclude_empty_values : bool = True) -> pd.DataFrame:
    df = df.copy()

    if not exclude_empty_values:
        df_empty_values = df[(df['advisors']=='') | (df['advisors'].isna()) | (df['advisors'].isnull())]
        df_empty_values.loc[:, 'advisors'] = 'NÃO IDENTIFICADO'
        df = df.drop(df_empty_values.index)
    else:
        df = clean_empty_rows(df=df,columns=['advisors'])

    # Normaliza e quebra os nomes buscados
    def extract_name_parts(name: str):
        words = [format_text(w.strip(), special_treatment=True) for w in name.split() if w.strip()]
        if not words:
            return None
        first = words[0]
        last = words[-1]
        last_initial = last[0] if last else ""
        return {"first": first, "last": last, "last_initial": last_initial}

    names_parts = [extract_name_parts(name) for name in advisor_names if name.strip()]

    def advisor_match(advisors_raw):
        advisors_list = advisors_raw.split(';')
        advisors_processed = [
            [format_text(part.strip(), special_treatment=True) for part in advisor.replace(',', ' ').split()]
            for advisor in advisors_list
        ]

        matches = []
        for name in names_parts:
            if name is None:
                continue
            first, last, last_initial = name["first"], name["last"], name["last_initial"]

            matched = False
            for advisor_parts in advisors_processed:
                has_first = first in advisor_parts
                has_last = (
                    last in advisor_parts or
                    f"{last_initial}." in advisor_parts or
                    last_initial in advisor_parts
                )
                if has_first and has_last:
                    matched = True
                    break

            matches.append(matched)

        return all(matches) if match_all else any(matches)

    mask = df['advisors'].apply(advisor_match)
    if exclude_empty_values:
        return df[mask]
    else:
        return pd.concat([df[mask],df_empty_values])

def filter_gender(df: pd.DataFrame,
                  genders: list[str],
                  just_contain: bool = True,
                  exclude_empty_values : bool = False) -> pd.DataFrame:
    df = df.copy()
    if not exclude_empty_values:
        df_empty_values = df[(df['gender_name']=='') | (df['gender_name'].isna()) | (df['gender_name'].isnull())]
        df_empty_values.loc[:, 'gender_name'] = 'NÃO IDENTIFICADO'
        df = df.drop(df_empty_values.index)
    else:
        df = clean_empty_rows(df=df,columns=['gender_name'])

    if just_contain:
        def match_any(g):
            if exclude_empty_values:
                return any(gender in g.split(',') for gender in genders)
            else:
                return any(gender in g.split(',') for gender in genders+[''])
        mask = df['gender_name'].apply(match_any)
    else:
        mask = df['gender_name'].isin(genders)

    if exclude_empty_values:
        return df[mask]
    else:
        return pd.concat([df[mask],df_empty_values])

def filter_language(df: pd.DataFrame,
                    languages: list[str],
                    exclude_empty_values : bool = False) -> pd.DataFrame:
    df = df.copy()

    # if exclude_empty_values:
    #     df = clean_empty_rows(df, columns=['language'])
    if not exclude_empty_values:
        mask = df['language'].isin(languages) | (df['language'] == "") | (df['language'].isna()) | (df['language'].isnull())
    else:
        mask = df['language'].isin(languages)
    # df = df[mask]
    if exclude_empty_values:
        return df[mask]
    else:
        df = df[mask]
        df['language'] = df['language'].replace({'': 'NÃO IDENTIFICADO'})
        return df

def filter_course(df: pd.DataFrame,
                  courses: list[str],
                  exclude_empty_values : bool = False) -> pd.DataFrame:
    df = df.copy()
    # if exclude_empty_values:
    #     df = clean_empty_rows(df=df,columns=['course'])
    if not exclude_empty_values:
        mask = df['course'].isin(courses) | (df['course'] == "") | (df['course'].isna()) | (df['course'].isnull())
    else:
        mask = df['course'].isin(courses)
    if exclude_empty_values:
        return df[mask]
    else:
        df = df[mask]
        df['course'] = df['course'].replace({'': 'NÃO IDENTIFICADO'})
        return df

def filter_type_course(df: pd.DataFrame, type_courses: list[str], exclude_empty_values: bool = False) -> pd.DataFrame:
    df = df.copy()
    # if exclude_empty_values:
    #     df = clean_empty_rows(df=df,columns=['type_course'])
    if not exclude_empty_values:
        mask = df['type_course'].isin(type_courses) | (df['type_course'] == "") | (df['type_course'].isna()) | (df['type_course'].isnull())
    else:
        mask = df['type_course'].isin(type_courses)
    if exclude_empty_values:
        return df[mask]
    else:
        df = df[mask]
        df['type_course'] = df['type_course'].replace({'': 'NÃO IDENTIFICADO'})
        return df

def filter_centro(df: pd.DataFrame, centros: list[str], exclude_empty_values: bool = False) -> pd.DataFrame:
    df = df.copy()
    # if exclude_empty_values:
    #     df = clean_empty_rows(df=df,columns=['centro'])
    if not exclude_empty_values:
        mask = df['centro'].isin(centros) | (df['centro'] == "") | (df['centro'].isna()) | (df['centro'].isnull())
    else:
        mask = df['centro'].isin(centros)
    if exclude_empty_values:
        return df[mask]
    else:
        df = df[mask]
        df['centro'] = df['centro'].replace({'': 'NÃO IDENTIFICADO'})
        return df

def filter_campus(df: pd.DataFrame, campuses: list[str], exclude_empty_values: bool = False) -> pd.DataFrame:
    df = df.copy()
    # if exclude_empty_values:
    #     df = clean_empty_rows(df=df,columns=['campus'])
    if not exclude_empty_values:
        mask = df['campus'].isin(campuses) | (df['campus'] == "") | (df['campus'].isna()) | (df['campus'].isnull())
    else:
        mask = df['campus'].isin(campuses)
    if exclude_empty_values:
        return df[mask]
    else:
        df = df[mask]
        df['campus'] = df['campus'].replace({'': 'NÃO IDENTIFICADO'})
        return df
