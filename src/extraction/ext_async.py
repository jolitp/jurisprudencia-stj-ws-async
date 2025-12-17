
import src.config.constants as C

import math
from rich import print
from icecream import ic
from bs4 import BeautifulSoup
import playwright.async_api._generated
import bs4

#region    find 1st element on page
async def find_1st_el_on_page(page: playwright.async_api._generated.Page,
                        element_tag: str = "div",
                        attributes: dict = {}):
    ic()

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find(element_tag, attributes)
#endregion find 1st element on page


def last_word_from_text(element: bs4.element.Tag):
    ic()

    return element.get_text().strip().split(" ")[-1]


# #region get total number of documents
# async def get_total_number_of_documents(
#         page: playwright.async_api._generated.Page,
#     ):
#     ic()

#     await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

#     el_attrs = { "class": "clsNumDocumento" }
#     await page.locator(".clsNumDocumento").first.wait_for(state="visible")
#     n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
#     ic(n_doc_el)
#     # n_doc_el = page.locator(".clsNumDocumento").first
#     # n_doc_el.wait_for(timeout=C.TIMEOUT)
#     n_docs = int(last_word_from_text(n_doc_el))
#     ic(n_docs)

#     return n_docs
# #endregion


#region    find all elements on page
async def find_all_elements_on_page(page: playwright.async_api._generated.Page,
                                    element_tag: str = "div",
                                    element_attributes: dict = {}):
    ic()

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find_all(element_tag, element_attributes)
#endregion find all elements on page


#region    pegar documentos
async def pegar_documentos(page: playwright.async_api._generated.Page):
    """
    Encontra (usando BeautifulSoup) todos os documentos contidos na página atual.

    Args:
        page: page do playwright
    """
    ic()

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    el_attrs = {"class": "documento"}
    documentos = await find_all_elements_on_page(page, element_attributes=el_attrs)
    return documentos
    # return documento
#endregion pegar documentos


#region    pegar dados do documento (new)
def pegar_dados_do_documento(doc: bs4.element.Tag,
                            aba: str = "undefined"):
    """
    Coleta os dados relevantes de um documento específico.

    Args:
        doc: Elemento contendo apenas 1 (um) documento.
    """
    ic()

    sections = doc.find_all("div", attrs={ "class": "paragrafoBRS" })

    sections_dict = {}

    # get numero do documento (index)
    n_doc_el = doc.find("div", { "class": "clsNumDocumento" })
    numero_documento = n_doc_el.text.split()[1]
    sections_dict["Índice"] = numero_documento

    # get aba
    sections_dict["Aba"] = aba

    for section in sections:
        section_name_el = section.find("div",
                                        attrs={ "class": "docTitulo" },
                                        recursive=False
                                    )
        section_name = list(section_name_el.stripped_strings)
        if type(section_name) is list:
            section_name = section_name[0]
            if "\n" in section_name or "  " in section_name:
                section_name = " ".join(section_name.split())
        if "Relator" in section_name:
            section_name = "Relator/Relatora"

        section_value_el = section.find("div", attrs={ "class": "docTexto" })
        section_value = list(section_value_el.stripped_strings)
        if type(section_value) is list:
            section_value = " ".join(section_value)
            if "\n" in section_value or "  " in section_value:
                section_value = " ".join(section_value.split())
        elif type(section_value) is str:
            if "\n" in section_value or "  " in section_value:
                section_value = " ".join(section_value.split())

        sections_dict[str(section_name)] = section_value
        ...

    # get pdf link
    href = ""
    # ic(aba)
    # ic("Acórdãos" in aba)
    # ic("Decisões Monocráticas" in aba)
    if "Acórdãos" in aba:
        attrs = { "data-bs-original-title": "Exibir o inteiro teor do acórdão."}
        pdf_dl_btn = doc.find("a", attrs=attrs)
        url_base = "https://processo.stj.jus.br"

        # BUG ainda dá eleemento não encontrado em acórãos
        href = url_base + pdf_dl_btn.get("href")\
                                    .replace("javascript:inteiro_teor('", "")\
                                    .replace("')", "")
        ...
    elif "Decisões Monocráticas" in aba:
        # NOTE em decisoes democraticas abre uma nova janela e o link é este:
        # processo.stj.jus.br/processo/pesquisa/?num_registro=202502557087
# <a href="javascript:processo('https://processo.stj.jus.br/processo/pesquisa/?num_registro=202502557087');"
#    data-bs-toggle="tooltip"
#    data-bs-placement="bottom"
#    title=""
#    data-bs-original-title="Consulta Processual"
#    aria-label="Consulta Processual">
#       <img src="/recursos/imagens/iconeProcesso.png">
# </a>
        attrs = { "data-bs-original-title": "Consulta Processual"}
        pdf_dl_btn = doc.find("a", attrs=attrs)
        url_base = "https://processo.stj.jus.br"
        href = url_base + pdf_dl_btn.get("href")\
            .replace("javascript:processo('", "")\
            .replace("')", "")
    sections_dict["PDF Link"] = href

    # get recurso repetitivo link (tema)
    attrs = { "class": "barraDocRepetitivo" }
    recurso_repetitivo_el = doc.find("div", attrs=attrs)
    sections_dict["Link Recurso Repetitivo"] = ""
    if recurso_repetitivo_el is not None:
        recurso_repetitivo_link_el = recurso_repetitivo_el.find("a")
        sections_dict["Link Recurso Repetitivo"] = recurso_repetitivo_link_el.get("href")
        ...

    return sections_dict
#endregion pegar dados do documento (new)


#region get number of pages to traverse
async def get_number_of_pages_to_traverse(
        page: playwright.async_api._generated.Page,
    ):
    ic()

    page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    el_attrs = { "class": "clsNumDocumento" }
    page.locator(".clsNumDocumento").first.wait_for(state="visible")
    n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
    ic(n_doc_el)
    # n_doc_el = page.locator(".clsNumDocumento").first
    # n_doc_el.wait_for(timeout=C.TIMEOUT)
    n_docs = int(last_word_from_text(n_doc_el))
    ic(n_docs)
    n_de_paginas = math.ceil(n_docs / C.DOCS_PER_PAGE)

    print("get_number_of_pages_to_traverse", locals())

    return n_de_paginas
#endregion


#region get nubmer of docs in last page
async def get_number_of_docs_in_last_page(
        page: playwright.async_api._generated.Page,
    ):
    ic()

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