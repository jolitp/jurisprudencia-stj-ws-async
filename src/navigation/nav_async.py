import math
import src.config.constants as C

from src.extraction import ext_sync, ext_async
from src.navigation import nav_sync
from src.config import constants as C
from src.config.parsing import search_config
from src.models import models

from pydantic import BaseModel
import asyncio
import time
import playwright.async_api._generated

from icecream import ic
from rich import print
from rich.console import Console


#region visit pages
async def visit_pages(context, item):
    ic(locals())

    page = await context.new_page()

    await page.goto(C.URL)

    start_time = time.perf_counter()
    await fill_form(page)
    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    await wait_for_page_to_change_document_number(page, item.current_page_number)
    await paginate(page, item)
    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    docs = await ext_async.pegar_documentos(page)

    data = []
    for doc in docs:
        result = ext_sync.pegar_dados_do_documento(doc, tab = item.tab)
        data.append(result)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    result = models.PageData(
        tab = item.tab,
        page_number = item.current_page_number,
        data = data,
        elapsed_time = elapsed_time
    )
    return result
    ...
#endregion


#region fill form
async def fill_form(
    page: playwright.async_api._generated.Page,
    ):
    ic(locals())

    pesquisa_avancada_xpath = search_config["pesquisa_avancada_xpath"]
    botao_buscar_xpath = search_config["botao_buscar_xpath"]
    criterio_de_pesquisa_xpath = search_config["criterio_de_pesquisa_xpath"]
    data_de_julgamento_inicial_xpath = search_config["data_de_julgamento_inicial_xpath"]
    data_de_julgamento_final_xpath = search_config["data_de_julgamento_final_xpath"]
    # data_de_publicacao_inicial_xpath = search_config["data_de_publicação_inicial_xpath"]
    # data_de_publicacao_final_xpath = search_config["data_de_publicação_final_xpath"]

    await page.locator(criterio_de_pesquisa_xpath)\
        .fill(C.SEARCH_TERMS["PESQUISA"])
    await page.locator(pesquisa_avancada_xpath)\
        .click()

    await page.locator(data_de_julgamento_inicial_xpath)\
        .fill(C.SEARCH_TERMS["DATA_DE_JULGAMENTO_INICIAL"])
    await page.locator(data_de_julgamento_final_xpath)\
        .fill(C.SEARCH_TERMS["DATA_DE_JULGAMENTO_FINAL"])

    # page.locator(data_de_publicacao_inicial_xpath)\
    #     .fill(C.PESQUISA["DATA_DE_PUBLICACAO_INICIAL"])
    # page.locator(data_de_publicacao_final_xpath)\
    #     .fill(C.PESQUISA["DATA_DE_PUBLICACAO_FINAL"])

    await page.locator(criterio_de_pesquisa_xpath)\
        .click() # fix popup appearing

    await page.locator(botao_buscar_xpath).click()
#endregion


#region wait for page to change document number
async def wait_for_page_to_change_document_number(
    page: playwright.async_api._generated.Page,
    page_nubmer,
    ):
    ic(locals())

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    await page.locator("#qtdDocsPagina").select_option(str(C.DOCS_PER_PAGE))

    count = 0
    console = Console()
    with console.status(
f"[yellow]Página {page_nubmer}[/]. Mudando o número de [cyan]Docs/Pág[/] de [cyan]10[/] para [cyan]50[/]."):
        while True:
            # TODO check against the remaining number of documents in the last page
            time.sleep(1)
            count += 1

            await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)
            n_docs_ult_pag = await ext_async.get_number_of_docs_in_last_page(page)
            n_docs_pag_atual = len(await ext_async.pegar_documentos(page))

            if n_docs_pag_atual == C.DOCS_PER_PAGE\
            or n_docs_pag_atual == n_docs_ult_pag\
            or n_docs_ult_pag == 0:
                break
            ...
        ...
    ...
#endregion


#region    Paginate
async def paginate(
    page: playwright.sync_api._generated.Page,
    item: dict
    ):
    ic(locals())

    extepcted_initial_start_doc_number = item.start_doc_number

    await page.evaluate(f"navegaForm('{extepcted_initial_start_doc_number}');")

    while True:
        await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)
        await asyncio.sleep(1)

        docs_el = await ext_async.pegar_documentos(page)
        actual_start_doc_on_page = docs_el[0]
        actual_start_doc_number: str = actual_start_doc_on_page\
            .find("div", { "class": "clsNumDocumento" }).text.strip()
        actual_start_doc_number_split = actual_start_doc_number.split(' ')
        actual_start_doc_number: int = int(actual_start_doc_number_split[1])

        match_start = actual_start_doc_number == extepcted_initial_start_doc_number

        ic(match_start)
        if match_start:
            print("Fim da paginação")
            break
        ...
    ...
#endregion Paginate
