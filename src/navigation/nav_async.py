import math
import src.config.constants as C


from src.extraction import ext_sync, ext_async
from src.navigation import nav_sync
from ..config import constants as C
from ..config.parsing import search_config

import time
import playwright.async_api._generated

from icecream import ic
from rich import print


#region visit pages
async def visit_pages(context, item, console):
    page = await context.new_page()

    await page.goto(C.URL)

    start_time = time.perf_counter()
    await fill_form(page)
    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    # TODO mudar para 50 docs/pag
    await wait_for_page_to_change_document_number(page, console)

    # TODO paginar por javascript

    docs = await ext_async.pegar_documentos(page)
    ic(len(docs))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # await tab_info = ext_sync.get_info_on_tabs(page)
    return elapsed_time
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
        .fill(C.PESQUISA["PESQUISA"])
    await page.locator(pesquisa_avancada_xpath)\
        .click()

    await page.locator(data_de_julgamento_inicial_xpath)\
        .fill(C.PESQUISA["DATA_DE_JULGAMENTO_INICIAL"])
    await page.locator(data_de_julgamento_final_xpath)\
        .fill(C.PESQUISA["DATA_DE_JULGAMENTO_FINAL"])

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
    console
    ):
    ic()

    # check_if_tabs_have_documents(page)

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    await page.locator("#qtdDocsPagina").select_option("50")

    with console.status(
        "Mudando o número de [cyan]Docs/Pág[/] de [cyan]10[/] para [cyan]50[/]"):

        while True:
            # TODO check against the remaining number of documents in the last page
            time.sleep(1)
            ic("inside loop")

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


# #region get number of pages to traverse
# def get_number_of_pages_to_traverse(
#         page: playwright.sync_api._generated.Page,
#     ):
#     ic()

#     page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

#     el_attrs = { "class": "clsNumDocumento" }
#     page.locator(".clsNumDocumento").first.wait_for(state="visible")
#     n_doc_el = ext_sync.find_1st_el_on_page(page, attributes=el_attrs)
#     ic(n_doc_el)
#     # n_doc_el = page.locator(".clsNumDocumento").first
#     # n_doc_el.wait_for(timeout=C.TIMEOUT)
#     n_docs = int(ext_async.last_word_from_text(n_doc_el))
#     ic(n_docs)
#     n_de_paginas = math.ceil(n_docs / C.DOCS_PER_PAGE)

#     print("get_number_of_pages_to_traverse", locals())

#     return n_de_paginas
# #endregion