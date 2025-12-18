from ..config import constants as C
from ..config.parsing import search_config
from src.extraction import ext_async

import playwright.sync_api._generated

import asyncio

from icecream import ic
from rich import print

def fill_form(
    page: playwright.sync_api._generated.Page,
    ):
    ic()

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

    pesquisa_avancada_xpath = search_config["pesquisa_avancada_xpath"]
    botao_buscar_xpath = search_config["botao_buscar_xpath"]
    criterio_de_pesquisa_xpath = search_config["criterio_de_pesquisa_xpath"]
    data_de_julgamento_inicial_xpath = search_config["data_de_julgamento_inicial_xpath"]
    data_de_julgamento_final_xpath = search_config["data_de_julgamento_final_xpath"]
    # data_de_publicacao_inicial_xpath = search_config["data_de_publicação_inicial_xpath"]
    # data_de_publicacao_final_xpath = search_config["data_de_publicação_final_xpath"]

    page.locator(criterio_de_pesquisa_xpath)\
        .fill(C.SEARCH_TERMS["PESQUISA"])
    page.locator(pesquisa_avancada_xpath)\
        .click()

    page.locator(data_de_julgamento_inicial_xpath)\
        .fill(C.SEARCH_TERMS["DATA_DE_JULGAMENTO_INICIAL"])
    page.locator(data_de_julgamento_final_xpath)\
        .fill(C.SEARCH_TERMS["DATA_DE_JULGAMENTO_FINAL"])

    # page.locator(data_de_publicacao_inicial_xpath)\
    #     .fill(C.PESQUISA["DATA_DE_PUBLICACAO_INICIAL"])
    # page.locator(data_de_publicacao_final_xpath)\
    #     .fill(C.PESQUISA["DATA_DE_PUBLICACAO_FINAL"])

    page.locator(criterio_de_pesquisa_xpath)\
        .click() # fix popup appearing

    page.locator(botao_buscar_xpath).click()

