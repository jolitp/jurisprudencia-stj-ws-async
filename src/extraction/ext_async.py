
import src.config.constants as C

import math
from rich import print
from icecream import ic
from bs4 import BeautifulSoup
import playwright.async_api._generated
import bs4
import asyncio

#region    find 1st element on page
async def find_1st_el_on_page(page: playwright.async_api._generated.Page,
                        element_tag: str = "div",
                        attributes: dict = {}):
    ic(locals())

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find(element_tag, attributes)
#endregion find 1st element on page


def last_word_from_text(element: bs4.element.Tag):
    ic(locals())

    return element.get_text().strip().split(" ")[-1]


#region get total number of documents
async def get_total_number_of_documents(
        page: playwright.async_api._generated.Page,
    ):
    ic(locals())

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    el_attrs = { "class": "clsNumDocumento" }
    await page.locator(".clsNumDocumento").first.wait_for(state="visible")
    n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
    ic(n_doc_el)
    # n_doc_el = page.locator(".clsNumDocumento").first
    # n_doc_el.wait_for(timeout=C.TIMEOUT)
    n_docs = int(last_word_from_text(n_doc_el))
    ic(n_docs)

    return n_docs
#endregion


#region    find all elements on page
async def find_all_elements_on_page(page: playwright.async_api._generated.Page,
                                    element_tag: str = "div",
                                    element_attributes: dict = {}):
    ic(locals())

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    element_found = soup.find_all(element_tag, element_attributes)
    if not element_found:
        asyncio.sleep(1)
        element_found = soup.find_all(element_tag, element_attributes)
    page.screenshot(path="")
    ic(element_found)
    return element_found
#endregion find all elements on page


#region    pegar documentos
async def pegar_documentos(page: playwright.async_api._generated.Page):
    ic(locals())

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    el_attrs = {"class": "documento"}
    documentos = await find_all_elements_on_page(page, element_attributes=el_attrs)
    return documentos
#endregion pegar documentos


#region get number of pages to traverse
async def get_number_of_pages_to_traverse(
        page: playwright.async_api._generated.Page,
    ):
    ic(locals())

    try:
        await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

        el_attrs = { "class": "clsNumDocumento" }
        await page.locator(".clsNumDocumento").first.wait_for(state="visible")
        n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
    except TimeoutError:
        print("Could not find document element, trying a second time")
        # print("get_number_of_pages_to_traverse", locals())

        try:
            await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

            el_attrs = { "class": "clsNumDocumento" }
            await page.locator(".clsNumDocumento").first.wait_for(state="visible")
            n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
        except TimeoutError:
            print("Could not find document element for the second time. Aborting.")

            # print(TimeoutError.errors)
            exit()
            ...

    # ic(n_doc_el)
    # n_doc_el = page.locator(".clsNumDocumento").first
    # n_doc_el.wait_for(timeout=C.TIMEOUT)
    n_docs = int(last_word_from_text(n_doc_el))
    # ic(n_docs)
    n_de_paginas = math.ceil(n_docs / C.DOCS_PER_PAGE)

    return n_de_paginas
#endregion


#region get nubmer of docs in last page
async def get_number_of_docs_in_last_page(
        page: playwright.async_api._generated.Page,
    ):
    ic(locals())

    n_de_paginas = await get_number_of_pages_to_traverse(page)
    el_attrs = { "class": "clsNumDocumento" }
    n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
    n_docs = int(last_word_from_text(n_doc_el))

    if n_de_paginas == 1:
        n_docs_until_last_page = n_docs
    else:
        n_docs_until_last_page = (n_de_paginas -1) * C.DOCS_PER_PAGE
    n_docs_ultima_pagina = n_docs - n_docs_until_last_page

    # print("get_number_of_docs_in_last_page",  locals())

    return n_docs_ultima_pagina
#endregion