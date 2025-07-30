import central_das_emendas_teste as cde

def test_load_csv():
    df = cde.load_csv(cache_dir=".tests_cache")

    # 1. O dataframe deve conter algo
    assert not df.empty, "O DataFrame está vazio."

    # 2. Algumas colunas básicas devem estar presentes
    colunas_esperadas = {
        "codigo_emenda",
        "tipo_emenda",
        "cod_autor",
        "valor_empenhado",
    }

    assert colunas_esperadas.issubset(df.columns), \
        f"Colunas faltando: {colunas_esperadas - set(df.columns)}"
