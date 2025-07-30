# central_das_emendas_teste/data_loader.py
from pathlib import Path
import gdown
import pandas as pd

_FILE_ID = "1Oquyuq9hHifoOgKcMDT13Srzjs2CZBvo"
_URL = f"https://drive.google.com/uc?export=download&id={_FILE_ID}"
_CSV_NAME = "central_emendas_raw.csv"

def _download(cache_dir: Path | str = "~/.cache/central_emendas") -> Path:
    cache_dir = Path(cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    csv_path = cache_dir / _CSV_NAME

    if csv_path.exists():
        return csv_path

    gdown.download(_URL, str(csv_path), quiet=False)
    return csv_path

def load_csv(cache_dir: Path | str = "~/.cache/central_emendas"):
    """
    Faz download (se necessário) e devolve o arquivo como DataFrame.

    Parâmetros
    ----------
    cache_dir : str | Path, opcional
        Diretório onde o CSV é armazenado em cache para evitar
        múltiplos downloads.

    Retorna
    -------
    pandas.DataFrame
        Dados da 'Central das Emendas' com separador ';'.

    Observações
    -----------
    O CSV original usa ponto-e-vírgula (`sep=';'`) como delimitador.
    Esta função já faz essa leitura corretamente.
    """
    csv_file = _download(cache_dir)
    return pd.read_csv(csv_file, sep=';')
