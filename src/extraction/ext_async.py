
import src.config.constants as C
from src.models import models

import math
from rich import print
from icecream import ic
from bs4 import BeautifulSoup
import playwright.async_api._generated
import bs4
import asyncio
from src.models import models


#region not found error class
class NotFound404Error(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
    ...
#endregion


#region Tab Data Class
class TabProcessor:
    def __init__(self,
                id: str,
                # page: playwright.sync_api._generated.Page,
                html_content: str
                ):
        self.id = id
        # self.page = page
        self.name = None
        self.html_content = html_content
        self.errors = []

        if "campoACOR" in id:
            self.name = "Acórdãos 1"
        elif "campoBAEN" in id:
            self.name = "Acórdãos 2"
        elif "campoDTXT" in id:
            self.name = "Decisões Monocráticas"
        else:
            raise ValueError(
                """Tab IDs do not match.
                Review scraping logic.
                The webside may have changed""")

        self.errors = []
        self.text = self.get_text()
        self.doc_num = self.get_doc_num()
        self.page_num = self.get_page_num()
        self.doc_num_last_page = self.get_doc_num_on_last_page()
        # self.is_active = self.is_it_active()
        # self.locator = self.get_locator()

    async def get_data(self, page):
        locator = await self.get_locator(page)
        is_active = await self.is_it_active(page)

        return models.TabData(
            name = self.text,
            locator = locator,
            doc_num = self.doc_num,
            page_num = self.page_num,
            doc_num_last_page = self.doc_num_last_page,
            is_active = is_active,
            errors = self.errors
        )

    def get_text(self):
        # html_content = self.page.content()
        soup = BeautifulSoup(self.html_content, 'lxml')

        result =  soup.find("div", { "id": self.id}).text
        if "oops" in result:
            self.errors.append(NotFound404Error(
                                "Aba com erro 404",
                                f"texto na aba:\n{result}"))
            result = None
            print(f"[red]Erro 404 não encontrado em aba {self.name}[/]")
        return result

    def get_doc_num(self):
        try:
            tab_doc_num = None
            tab_doc_num = self.text.replace(f"{self.name} (", "")\
                                .replace(")", "")\
                                .replace(".", "")
            tab_doc_num = int(tab_doc_num)
        except ValueError:
            print(
f"[red]Não foi possível retirar o número de documentos da aba {self.name}[/]")
        finally:
            return tab_doc_num

    def get_page_num(self):
        try:
            page_num = None
            if self.get_doc_num() == 0:
                page_num = 0
            elif self.get_doc_num() <= C.DOCS_PER_PAGE:
                page_num = 1
            else:
                page_num = \
                    math.ceil(self.get_doc_num() / C.DOCS_PER_PAGE)
        except ValueError:
            print(f"[red]Número de documentos não encontrado na aba {self.name}[/]")
        finally:
            return page_num

    def get_doc_num_on_last_page(self):
        doc_num_on_last_page = None
        try:
            if self.doc_num == 0:
                doc_num_on_last_page = 0
            elif self.doc_num <= C.DOCS_PER_PAGE:
                doc_num_on_last_page = self.doc_num
            else:
                doc_num_on_last_page = math.fmod(self.doc_num, C.DOCS_PER_PAGE)
            return int(doc_num_on_last_page)
        except TypeError:
            print(
f"[red]Número de documentos na última página não pode ser calculado para aba {self.name}[/]")
            doc_num_on_last_page = None
            return None

    async def get_locator(self, page):
        locator = page.locator(f"id={self.id}")
        return locator

    async def is_it_active(self, page):
        aba_el = await find_1st_el_on_page(page, "div", attributes={"id": self.id})
        is_active = True if "ativo" in aba_el.get("class") else False
        return is_active
#endregion Tab Data Class


#region get info on tabs
async def get_info_on_tabs(
        page: playwright.async_api._generated.Page
    ) -> dict[ str, models.TabData ]:
    ic(locals())

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    html_content = await page.content()

    # IDs
    # id_aba_sumulas = "campoSUMU"
    acordaos_1_data = TabProcessor("campoACOR", html_content)
    acordaos_1_data.locator = await acordaos_1_data.get_locator(page)
    acordaos_2_data = TabProcessor("campoBAEN", html_content)
    acordaos_2_data.locator = await acordaos_2_data.get_locator(page)
    decisoes_monocraticas_data = TabProcessor("campoDTXT", html_content)
    decisoes_monocraticas_data.locator = await decisoes_monocraticas_data.get_locator(page)

    acordaos_1_data = await acordaos_1_data.get_data(page)
    acordaos_2_data = await acordaos_2_data.get_data(page)
    decisoes_monocraticas_data = await decisoes_monocraticas_data.get_data(page)

    result = {
        "acordaos_1": acordaos_1_data,
        "acordaos_2": acordaos_2_data,
        "decisoes_monocraticas": decisoes_monocraticas_data,
    }
    return result
#endregion


#region    find 1st element on page
async def find_1st_el_on_page(
        page: playwright.async_api._generated.Page,
        element_tag: str = "div",
        attributes: dict = {}
    ):
    ic(locals())

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find(element_tag, attributes)
#endregion find 1st element on page


#region last word from text
def last_word_from_text(
        element: bs4.element.Tag
    ):
    ic(locals())

    return element.get_text().strip().split(" ")[-1]
#endregion


#region get total number of documents
async def get_total_number_of_documents(
        page: playwright.async_api._generated.Page,
    ):
    ic(locals())

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    el_attrs = { "class": "clsNumDocumento" }
    await page.locator(".clsNumDocumento").first.wait_for(state="visible")
    n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)
    n_docs = int(last_word_from_text(n_doc_el))

    return n_docs
#endregion


#region    find all elements on page
async def find_all_elements_on_page(
        page: playwright.async_api._generated.Page,
        element_tag: str = "div",
        element_attributes: dict = {}
    ):
    ic(locals())

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    element_found = soup.find_all(element_tag, element_attributes)
    if not element_found:
        await asyncio.sleep(1)
        element_found = soup.find_all(element_tag, element_attributes)

    return element_found
#endregion find all elements on page


#region    pegar documentos
async def pegar_documentos(
        page: playwright.async_api._generated.Page
    ):
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

    await page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

    el_attrs = { "class": "clsNumDocumento" }
    await page.locator(".clsNumDocumento").first.wait_for(state="visible")
    n_doc_el = await find_1st_el_on_page(page, attributes=el_attrs)

    n_docs = int(last_word_from_text(n_doc_el))
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

    return n_docs_ultima_pagina
#endregion