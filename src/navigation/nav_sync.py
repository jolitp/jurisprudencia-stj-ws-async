from ..config import constants as C
from rich import print

#region annouce fill form
def announce_fill_form():
    print("Preenchendo [blue]formulário[/] da página de pesquisa com os seguints campos:")
    print(f"  [blue]conteudo[/]: {C.SEARCH_TERMS["PESQUISA"]}")
    print(f"  [blue]data de julgamento inicial[/]: {C.SEARCH_TERMS["DATA_DE_JULGAMENTO_INICIAL"]}")
    print(f"  [blue]data de julgamento final[/]: {C.SEARCH_TERMS["DATA_DE_JULGAMENTO_FINAL"]}")
    # print(f"  [blue]data de publicação inicial[/]: {C.PESQUISA["DATA_DE_PUBLICACAO_INICIAL"]}")
    # print(f"  [blue]data de publicação final[/]: {C.PESQUISA["DATA_DE_PUBLICACAO_FINAL"]}")
    print()
    print(f"[red]Outros campos serão implementados futuramente.[/]")
    print()
    print(f"Serão coletadas informações de:")
    if C.SEARCH_TERMS["ACORDAOS_1"]:
        print("Acórdãos 1")
    if C.SEARCH_TERMS["ACORDAOS_2"]:
        print("Acórdãos 2")
    if C.SEARCH_TERMS["DECISOES_MONOCRATICAS"]:
        print("Decisões Monocráticas")
#endregion annouce fill form

