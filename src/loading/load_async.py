import src.config.constants as C
import os
import pandas as pd
from rich import print


async def save_to_csv(
    data: list[dict],
    header: list,
    script_start_datetime=None):
    dir_str = "__execucoes__/no_date"
    if script_start_datetime:
        formatted_datetime = script_start_datetime.strftime("%Y_%m_%d_-_%H_%M_%S")
        search_terms = C.SEARCH_TERMS["PESQUISA"]
        dir_str = f"__execucoes__/{formatted_datetime}/{search_terms}"

    csv_filename = "output.csv"
    os.makedirs(dir_str, exist_ok=True)

    print(f"Salvando {csv_filename} em {dir_str}")
    df = pd.DataFrame(data, columns=header)
    df.sort_values(by=['Índice'])
    df.to_csv(f'{dir_str}/{csv_filename}', index=False)
