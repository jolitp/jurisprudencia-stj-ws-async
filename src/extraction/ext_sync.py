import src.config.constants as C

import math
from bs4 import BeautifulSoup
import playwright.sync_api._generated
from icecream import ic
from rich import print


#region    find 1st element on page
def find_1st_el_on_page(page: playwright.sync_api._generated.Page,
                        element_tag: str = "div",
                        attributes: dict = {}):
    ic()

    html_content = page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find(element_tag, attributes)
#endregion find 1st element on page


#region not found error class
class NotFound404Error(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
    ...
#endregion


#region Tab Data Class
class TabData:
    def __init__(self, id, page):
        self.id = id
        self.page = page
        self.name = None

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
        self.locator = self.get_locator()
        self.doc_num = self.get_doc_num()
        self.page_num = self.get_page_num()
        self.doc_num_last_page = self.get_doc_num_on_last_page()
        self.is_active = self.is_it_active()

        self.dict = {
            "name": self.text,
            "locator": self.locator,
            "doc_num": self.doc_num,
            "page_num": self.page_num,
            "doc_num_last_page": self.doc_num_last_page,
            "is_active": self.is_active,
            "errors": self.errors
        }

    def get_text(self):
        html_content = self.page.content()
        soup = BeautifulSoup(html_content, 'lxml')

        result =  soup.find("div", { "id": self.id}).text
        if "oops" in result:
            self.errors.append(NotFound404Error(
                                "Aba com erro 404",
                                f"texto na aba:\n{result}"))
            result = (None, "404 page")
            print(f"[red]Erro 404 não encontrado em aba {self.name}[/]")

        ic(vars(self))

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
            # ic(locals())
            # ic(vars(self))
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
            # ic(locals())
            # ic(vars(self))
        finally:
            return page_num

    def get_doc_num_on_last_page(self):
        doc_num_on_last_page = None
        try:
            if self.get_doc_num() == 0:
                doc_num_on_last_page = 0
            elif self.get_doc_num() <= C.DOCS_PER_PAGE:
                doc_num_on_last_page = 0
            else:
                doc_num_on_last_page = \
                    math.fmod(self.get_doc_num(), C.DOCS_PER_PAGE)
            return int(doc_num_on_last_page)
        except TypeError:
            print(
f"[red]Número de documentos na última página não pode ser calculado para aba {self.name}[/]")
            doc_num_on_last_page = None
            # ic(locals())
            # ic(vars(self))
            return None

    def get_locator(self):
        return self.page.locator(f"id={self.id}"),

    def is_it_active(self):
        aba_el = find_1st_el_on_page(self.page, "div", attributes={"id": self.id})
        return True if "ativo" in aba_el.get("class") else False
#endregion Tab Data Class


#region get info on tabs
def get_info_on_tabs(page: playwright.sync_api._generated.Page):
    page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)
    ic()

    # IDs
    # id_aba_sumulas = "campoSUMU"
    acordaos_1_data = TabData("campoACOR", page)
    # ic(vars(acordaos_1_data))
    acordaos_2_data = TabData("campoBAEN", page)
    decisoes_monocraticas_data = TabData("campoDTXT", page)

    result = {
        "acordaos_1": acordaos_1_data.dict,
        "acordaos_2": acordaos_2_data.dict,
        "decisoes_monocraticas": decisoes_monocraticas_data.dict,
    }
    return result
#endregion
