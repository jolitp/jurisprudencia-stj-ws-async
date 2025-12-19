import math
import src.config.constants as C
from src.loading import load_sync
from src.extraction import ext_async
# from src.extraction import ext_sync
# from src.navigation import nav_sync
from src.navigation import nav_async
from src.models import models
from src.utils import browser_utils as bu

import asyncio
import random
import typer
import random
# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
# from rich.traceback import install # using typer's rich, configure there
from rich import print
from icecream import ic

# import logging
# def warn(s):
#     logging.warning("%s", s)
# def toString(obj):
#    if isinstance(obj, str)
#        return '[!string %r with length %i!]' % (obj, len(obj))
#    return repr(obj)
ic.configureOutput(
    prefix='>\n> debug print (icecream)\n> ',
    # outputFunction=warn,
    # argToStringFunction=toString,
    includeContext=True,
    # contextAbsPath=True
)
from icecream import install as icecream_install
icecream_install()

app = typer.Typer(pretty_exceptions_show_locals=False)


#region get tab info
async def get_tab_info():
    ic(locals())
    # do a preliminary run to get info on number of documents of each tab
    tab_info = {}
    async with async_playwright() as pw:
        browser = await pw.firefox.launch(
            headless=False, # toggle
        )
        context = await browser.new_context(
            viewport={"width": 960, "height": 1080},
            user_agent=bu.random_user_agent(),
            geolocation=bu.random_geolocation(),
            permissions=["geolocation"]
        )
        page = await context.new_page()

        print(f"Navegando para a URL: {C.URL}")
        await page.goto(C.URL, timeout = 0)

        await nav_async.fill_form(page)
        tab_info = await ext_async.get_info_on_tabs(page)
        ic(tab_info)

        tabs = ["acordaos_1", "acordaos_2", 'decisoes_monocraticas']
        for tab in tabs:
            errors = tab_info[tab].errors
            if errors:
                print(f"[red]Erros na aba {tab}[/]")

        browser.close()
        print(f"Fechando navegador.")
    return tab_info
#endregion get tab info


#region main command
@app.command()
def main(
    debug: bool = False
):
    ic(locals())

    ic.disable()
    if debug:
        ic.enable()

    tabs_info = asyncio.run(get_tab_info())
    ic(tabs_info)
    pipeline = create_pipeline(tabs_info)
    ic(pipeline)

    if pipeline:
        aggregated_results = asyncio.run(main_pipelined(pipeline, tabs_info))
        header = aggregated_results[0].keys()
        load_sync.save_to_csv(aggregated_results, header)
    else:
        print("[red]não há nenhum documento em nenhuma das abas.[/]")
#endregion main command


#region main pipelined
async def main_pipelined(
        pipeline: list[dict],
        tabs_info: dict
    ):
    ic(locals())

    async with async_playwright() as pw:
        browser = await pw.firefox.launch(
            headless=False,
        )
        context = await browser.new_context(
            viewport={"width": 960, "height": 1080}
        )

        semaphore = asyncio.Semaphore(10)
        tasks = []
        async with asyncio.TaskGroup() as tg:
            async with semaphore:
                for item in pipeline:
                    task = tg.create_task(
                        nav_async.visit_pages(context, item, tabs_info)
                    )
                    tasks.append(task)

        results = [task.result() for task in tasks]
        ic(len(results))

        aggregated_results = []
        for result in results:
            if result:
                data = result.data
                for d in data:
                    aggregated_results.append(d)

        await browser.close()
    return aggregated_results
#endregion main pipelined


#region create pipeline
def create_pipeline(
    tabs_info: dict[str, models.TabData],
    ):
    ic(locals())

    should_get_from_tab = {
        "acordaos_1": C.SEARCH_TERMS["ACORDAOS_1"],
        "acordaos_2": C.SEARCH_TERMS["ACORDAOS_2"],
        "decisoes_monocraticas": C.SEARCH_TERMS["DECISOES_MONOCRATICAS"],
    }

    pipeline = []
    for key, _ in tabs_info.items():
        if not should_get_from_tab[key]:
            continue
        number_of_pages = tabs_info[key].page_num

        if number_of_pages == 0:
            continue

        try:
            for current_page_number in range(0, number_of_pages):
            #region
                start_doc_number = (current_page_number * C.DOCS_PER_PAGE) + 1
                if current_page_number == number_of_pages:
                    doc_num_last_page = tabs_info[key].doc_num_last_page
                    end_doc_number = start_doc_number + doc_num_last_page
                else:
                    end_doc_number = start_doc_number + C.DOCS_PER_PAGE - 1
                if number_of_pages == 1:
                    doc_num_last_page = tabs_info[key].doc_num_last_page
                    end_doc_number = start_doc_number + doc_num_last_page - 1

                data = models.Pipeline(
                    tab = key,
                    current_page_number = current_page_number + 1,
                    start_doc_number = start_doc_number,
                    end_doc_number = end_doc_number,
                )
                pipeline.append(data)
            #endregion
        except TypeError as e:
            print(
"[red]Não foi possível completar a execução. Número de páginas não foi encontrado[/]")
            ic(locals())
            ic(repr(e))

    ic(locals())
    return pipeline
#endregion create pipeline


#region
if __name__ == "__main__":
    load_sync.create_directories()
    app()
#endregion
