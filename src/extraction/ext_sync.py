import src.config.constants as C
from src.models import models

import math
from bs4 import BeautifulSoup
import playwright.sync_api._generated
from icecream import ic
from rich import print
import bs4


#region    find 1st element on page
def find_1st_el_on_page(
        page: playwright.sync_api._generated.Page,
        element_tag: str = "div",
        attributes: dict = {}
    ):
    ic(locals())

    html_content = page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.find(element_tag, attributes)
#endregion find 1st element on page


# TODO cleanup
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
