import src.config.constants as C
import os
import pandas as pd
from rich import print
from icecream import ic


#region get path
def get_path():
    search_terms = C.SEARCH_TERMS["PESQUISA"]
    root = C.DIRS["save_root"]
    current_dir = C.DIRS["current_execution"]
    dir_path = f"{root}/{ current_dir } - { search_terms }"
    return dir_path
    ...
#endregion get path


#region create directories
def create_directories():
    # TODO use pathlib
    dir_path = get_path()
    debug_path = C.DIRS["debug"]
    screenshots_path = f"{dir_path}/{debug_path}/{C.DIRS["screenshots"]}"
    ic(screenshots_path)
    os.makedirs(screenshots_path, exist_ok=True)

    return dir_path
#endregion create directories


#region save to csv
def save_to_csv(
    data: list[dict],
    header: list,
    ):
    dir_str = get_path()
    csv_filename = "dados.csv"

    print(f"Salvando [blue]{csv_filename}[/] em [blue]{dir_str}[/]")
    df = pd.DataFrame(data, columns=header)
    df.sort_values(by=['Índice'])
    try:
        df.to_csv(f'{dir_str}/{csv_filename}', index=False)
    except Exception as e:
        print("[red]Erro ao criar o arquivo CSV.")
        ic(repr(e))
        ...
#endregion save to csv
