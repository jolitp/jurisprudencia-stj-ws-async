import math
import src.config.constants as C

from src.extraction import ext_sync, ext_async
from src.navigation import nav_sync
from ..config import constants as C
from ..config.parsing import search_config

import asyncio
import time
import playwright.async_api._generated

from icecream import ic
from rich import print
from rich.console import Console


#region visit pages
async def visit_pages(context, item):
    page = await context.new_page()

    await page.goto(C.URL)

    start_time = time.perf_counter()
    await fill_form(page)
    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    ic(item)
    console = Console()
    await wait_for_page_to_change_document_number(page, item["current_page_number"])
    await paginate(page, item)

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    docs = await ext_async.pegar_documentos(page)
    ic(len(docs))

    data = []
    for doc in docs:
        result = ext_sync.pegar_dados_do_documento(doc, tab = item["tab"])
        data.append(result)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # await tab_info = ext_sync.get_info_on_tabs(page)
    return {
        "tab": item["tab"],
        "page": item["current_page_number"],
        "data": data,
        "elapsed_time": elapsed_time
    }
    ...
#endregion


#region fill form
async def fill_form(
    page: playwright.async_api._generated.Page,
    ):
    ic()

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
    ic()

    # check_if_tabs_have_documents(page)

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
    ic()

    extepcted_initial_current_page_number = item["current_page_number"]
    # extepcted_initial_num_docs_on_page = item["num_docs_on_page"]
    extepcted_initial_start_doc_number = item["start_doc_number"]
    extepcted_initial_end_doc_number = item["end_doc_number"]
    extepcted_initial_tab  = item["tab"]

    await page.evaluate(f"navegaForm('{extepcted_initial_start_doc_number}');")

    # ic(locals())

    from rich.console import Console
    from rich.table import Table

    # table = Table(title=f"compare (page {extepcted_initial_current_page_number})")

    # table.add_column("var", justify="left",  style="cyan", no_wrap=True)
    # table.add_column("Expected", justify="middle", style="cyan", no_wrap=True)
    # table.add_column("Actual",   justify="right", style="cyan", no_wrap=True)


    count = 0
    while True:
        await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)
        await asyncio.sleep(1)
        count += 1

        docs_el = await ext_async.pegar_documentos(page)
        actual_start_doc_on_page = docs_el[0]
        actual_start_doc_number: str = actual_start_doc_on_page\
            .find("div", { "class": "clsNumDocumento" }).text.strip()
        actual_start_doc_number_split = actual_start_doc_number.split(' ')
        actual_start_doc_number: int = int(actual_start_doc_number_split[1])

        # table.add_row("start doc number", str(actual_start_doc_number), str(extepcted_initial_start_doc_number))

        # actual_end_doc_on_page = docs_el[-1]
        # actual_end_doc_number: str = actual_end_doc_on_page\
        #     .find("div", { "class": "clsNumDocumento" }).text.strip()
        # actual_end_doc_number_split = actual_end_doc_number.split(' ')
        # actual_end_doc_number: int = int(actual_end_doc_number_split[1])

        # table.add_row("end doc number", str(actual_end_doc_number), str(extepcted_initial_end_doc_number))
        # table.add_row("-"*20, "-"*20, "-"*20)

        match_start = actual_start_doc_number == extepcted_initial_start_doc_number
        # match_end = actual_end_doc_number == extepcted_initial_end_doc_number

        ic(match_start)
        # ic(match_end)

        # console = Console()
        # console.print(table)

        if match_start:
            print("Fim da paginação")
            break

        # if count == 30:
        #     break

    # ic(locals())


#endregion Paginate




# #region get number of pages to traverse
# async def get_number_of_pages_to_traverse(
#         page: playwright.sync_api._generated.Page,
#     ):
#     ic()

#     await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

#     el_attrs = { "class": "clsNumDocumento" }
#     await page.locator(".clsNumDocumento").first.wait_for(state="visible")
#     n_doc_el = ext_async.find_1st_el_on_page(page, attributes=el_attrs)
#     ic(n_doc_el)
#     # n_doc_el = page.locator(".clsNumDocumento").first
#     # n_doc_el.wait_for(timeout=C.TIMEOUT)
#     n_docs = int(ext_async.last_word_from_text(n_doc_el))
#     ic(n_docs)
#     n_de_paginas = math.ceil(n_docs / C.DOCS_PER_PAGE)

#     print("get_number_of_pages_to_traverse", locals())

#     return n_de_paginas
# #endregion