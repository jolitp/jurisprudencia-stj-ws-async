import src.config.constants as C

import math
from bs4 import BeautifulSoup
import playwright.sync_api._generated
from icecream import ic
from rich import print
import bs4


#region    find 1st element on page
def find_1st_el_on_page(page: playwright.sync_api._generated.Page,
                        element_tag: str = "div",
                        attributes: dict = {}):
    ic(locals())

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
def get_info_on_tabs(
    page: playwright.sync_api._generated.Page
    ):
    ic(locals())

    page.wait_for_load_state("networkidle", timeout=C.TIMEOUT)

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


#region    pegar dados do documento (new)
def pegar_dados_do_documento(
    doc: bs4.element.Tag,
    tab: str = "undefined"
   ):
    ic(locals())

    sections = doc.find_all("div", attrs={ "class": "paragrafoBRS" })

    sections_dict = {}

    # get numero do documento (index)
    n_doc_el = doc.find("div", { "class": "clsNumDocumento" })
    numero_documento = n_doc_el.text.split()[1]
    sections_dict["Índice"] = numero_documento

    # get aba
    sections_dict["Aba"] = tab

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
    if "Acórdãos" in tab:
        attrs = { "data-bs-original-title": "Exibir o inteiro teor do acórdão."}
        pdf_dl_btn = doc.find("a", attrs=attrs)
        url_base = "https://processo.stj.jus.br"

        # BUG ainda dá eleemento não encontrado em acórãos
        href = url_base + pdf_dl_btn.get("href")\
                                    .replace("javascript:inteiro_teor('", "")\
                                    .replace("')", "")
        ...
    elif "Decisões Monocráticas" in tab:
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
