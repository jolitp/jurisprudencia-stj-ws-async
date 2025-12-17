import src.config.constants as C

import math
from bs4 import BeautifulSoup
import playwright.sync_api._generated
from icecream import ic


#region    find 1st element on page
def find_1st_el_on_page(page: playwright.sync_api._generated.Page,
                        element_tag: str = "div",
                        attributes: dict = {}):
    ic()

    html_content = page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find(element_tag, attributes)
#endregion find 1st element on page


#region Tab Data Class
class TabData:
    def __init__(self, id, page):
        self.id = id
        self.page = page
        self.start = None

        if "campoACOR" in id:
            self.start = "Acórdãos 1"
        elif "campoBAEN" in id:
            self.start = "Acórdãos 2"
        elif "campoDTXT" in id:
            self.start = "Decisões Monocráticas"
        else:
            raise ValueError("Tab IDs do not match")

        self.dict = {
            "name": self.get_text(),
            "locator": self.get_locator(),
            "doc_num": self.get_doc_num(),
            "page_num": self.get_page_num(),
            "doc_num_last_page": self.get_doc_num_on_last_page(),
            "is_active": self.is_it_active(),
        }


    def get_text(self):
        html_content = self.page.content()
        soup = BeautifulSoup(html_content, 'lxml')

        return soup.find("div", { "id": self.id}).text

    def get_doc_num(self):
        tab_doc_num = self.get_text().replace(f"{self.start} (", "")\
                            .replace(")", "")\
                            .replace(".", "")
        return int(tab_doc_num)

    def get_page_num(self):
        if self.get_doc_num() == 0:
            page_num = 0
        elif self.get_doc_num() <= C.DOCS_PER_PAGE:
            page_num = 1
        else:
            page_num = \
                math.ceil(self.get_doc_num() / C.DOCS_PER_PAGE)
        return page_num

    def get_doc_num_on_last_page(self):
        if self.get_doc_num() == 0:
            doc_num_on_last_page = 0
        elif self.get_doc_num() <= C.DOCS_PER_PAGE:
            doc_num_on_last_page = 0
        else:
            doc_num_on_last_page = \
                math.fmod(self.get_doc_num(), C.DOCS_PER_PAGE)
        return int(doc_num_on_last_page)

    def get_locator(self):
        return self.page.locator(f"id={self.id}"),

    def is_it_active(self):
        aba_el = find_1st_el_on_page(self.page, "div", attributes={"id": self.id})
        return True if "ativo" in aba_el.get("class") else False
#endregion


#region get info on tabs
def get_info_on_tabs(page: playwright.sync_api._generated.Page):
    page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)
    ic()

    # IDs
    # id_aba_sumulas = "campoSUMU"
    acordaos_1_data = TabData("campoACOR", page)
    acordaos_2_data = TabData("campoBAEN", page)
    decisoes_monocraticas_data = TabData("campoDTXT", page)

    result = {
        "acordaos_1": acordaos_1_data.dict,
        "acordaos_2": acordaos_2_data.dict,
        "decisoes_monocraticas": decisoes_monocraticas_data.dict,
    }
    return result
#endregion
