import src.config.constants as C
import os
import pandas as pd
from rich import print
from icecream import ic


#region create directories
def create_directories():
    # TODO use pathlib
    search_terms = C.SEARCH_TERMS["PESQUISA"]
    root = C.DIRS["save_root"]
    current_dir = C.DIRS["current_execution"]
    dir_path = f"{root}/{ current_dir } - { search_terms }"
    debug_path = C.DIRS["debug"]
    screenshots_path = f"{dir_path}/{debug_path}/{C.DIRS["screenshots"]}"
    try:
        os.makedirs(screenshots_path, exist_ok=True)
    except Exception as e:
        print("[red]Erro ao criar diretórios.")
        ic(repr(e))
        ...
    ic(locals())
    return dir_path
#endregion


#region save to csv
def save_to_csv(
    data: list[dict],
    header: list,
    script_start_datetime=None
    ):
    dir_str = create_directories(script_start_datetime)
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
