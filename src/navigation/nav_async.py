import math
import src.config.constants as C

# from src.extraction import ext_sync
from src.extraction import ext_async
from src.extraction import ext_sync
from src.navigation import nav_sync
from src.config import constants as C
from src.config.parsing import search_config
from src.models import models
from src.utils import browser_utils as bu

import asyncio
import time
import playwright.async_api._generated

from icecream import ic
from rich import print
from rich.console import Console


#region change to  tab
async def change_to_tab(
        page: playwright.async_api._generated.Page,
        item,
    ):
    ic(locals())
    page_number = item.current_page_number

    print(f"Mudando para a aba {item.tab}")
    await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)

    tabs_before = await ext_async.get_info_on_tabs(page)
    tab_id = item.tab

    element_id = tabs_before[tab_id].element_id
    await page.locator(f"#{element_id}").click()

    await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)

    count = 0
    console = Console()
    with console.status(f""" Mudando de aba
[yellow]Aba {tab_id}[/] - [yellow]Página {page_number}[/]."""):
        while True:
            await asyncio.sleep(1)
            start_time = time.perf_counter()
            count += 1
            tabs_after = await ext_async.get_info_on_tabs(page)

            end_time = time.perf_counter()
            count += end_time - start_time
            ic(tabs_after[tab_id].is_active)
            if tabs_after[tab_id].is_active:
                break
        # while True:
    # with console.status(
    print(f"Na aba {item.tab} agora. Em {count} segundos.")
#endregion change to tab


#region visit pages
@bu.request_concurrency_limit_decorator()
async def visit_pages(
        browser,
        item,
    ):
    ic(locals())
    current_tab = item.tab
    current_page = item.current_page_number
    if C.SHOW_WINDOWS:
        print("Abrindo janela do navegador.")
    else:
        print("Abrindo janela do navegador em plano de fundo.")
    print(f"Executando aba [blue]{current_tab}[/] página [blue]{current_page}[/]")

    context = await browser.new_context(
        viewport={"width": 960, "height": 1080},
        user_agent=bu.random_user_agent(),
        geolocation=bu.random_geolocation(),
        permissions=["geolocation"]
    )
    page = await context.new_page()

    await page.goto(C.URL)

    start_time = time.perf_counter()
    await fill_form(page, item)
    await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)

    await change_to_tab(page, item)
    await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)


    await wait_for_page_to_change_document_number(page, item)
    await paginate(page, item)
    await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)

    docs = await ext_async.get_docs(page)

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
    print(f"Fim da execução da aba [blue]{current_tab}[/] página [blue]{current_page}[/]")
    print("fechando página")
    # await page.close()
    await browser.close()
    return result
#endregion


#region fill form
async def fill_form(
    page: playwright.async_api._generated.Page,
    item
    ):
    ic(locals())

    nav_sync.announce_fill_form()

    if item:
        tab = item.tab
        page_number = item.current_page_number
        message = f""" Preenchendo formulário de pesquisa
[yellow]Aba {tab}[/] - [yellow]Página {page_number}[/]."""
    else:
        message = "Preenchendo formulário de pesquisa"

    console = Console()
    with console.status(message):

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
    item,
    ):
    ic(locals())
    page_number = item.current_page_number
    tab = item.tab

    await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)

    # await page.locator("#qtdDocsPagina").wait_for_element_state("visible")
    handle = await page.query_selector("id=qtdDocsPagina")
    await handle.wait_for_element_state("visible")
    await page.locator("#qtdDocsPagina").select_option(str(C.DOCS_PER_PAGE))

    count = 0
    console = Console()
    m1 = f"[cyan]Docs/Pág[/] de [cyan]10[/] para [cyan]{C.DOCS_PER_PAGE}[/]"
    message = f""" Mudando o número de {m1}.
[yellow]Aba {tab}[/] - [yellow]Página {page_number}[/]."""
    with console.status(message):
        while True:
            await asyncio.sleep(1)
            start_time = time.perf_counter()
            count += 1

            await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)
            n_docs_ult_pag = await ext_async.get_number_of_docs_in_last_page(page)
            n_docs_pag_atual = len(await ext_async.get_docs(page))

            end_time = time.perf_counter()
            count += end_time - start_time
            if n_docs_pag_atual == C.DOCS_PER_PAGE\
            or n_docs_pag_atual == n_docs_ult_pag\
            or n_docs_ult_pag == 0:
                break
            ...
        ...
    ...
    print(f"Com {C.DOCS_PER_PAGE} agora. em {count} segundos.")
#endregion


#region    Paginate
async def paginate(
        page: playwright.sync_api._generated.Page,
        item: dict
    ):
    ic(locals())
    tab = item.tab
    page_number = item.current_page_number
    print(f"Mudando para a página {page_number}")
    extepcted_initial_start_doc_number = item.start_doc_number

    await page.evaluate(f"navegaForm('{extepcted_initial_start_doc_number}');")

    count = 0
    console = Console()
    message = f""" Mudando para documento número {extepcted_initial_start_doc_number}.
[yellow]Aba {tab}[/] - [yellow]Página {page_number}[/]."""
    with console.status(message):
        while True:
            await asyncio.sleep(1)
            count += 1

            await page.wait_for_load_state("domcontentloaded", timeout=C.TIMEOUT)
            docs_el = await ext_async.get_docs(page)
            if docs_el:
                actual_start_doc_on_page = docs_el[0]
            else:
                print(f"""Ao mudar para documento número {extepcted_initial_start_doc_number}
Não foram encontrados documentos na página.
Esperando a página carregar os documentos.""")
                continue
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
    ...
    print(f"página número {page_number} agora. Em {count} segundos.")
#endregion Paginate
