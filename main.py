import src.config.constants as C
from src.loading import load_sync
from src.extraction import ext_sync
from src.navigation import nav_sync
from src.navigation import nav_async
from src.models import models
from src.utils import browser_utils as bu

import asyncio
import random
import typer
import random
from playwright.sync_api import sync_playwright
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
def get_tab_info():
    ic(locals())
    # do a preliminary run to get info on number of documents of each tab
    tab_info = {}
    with sync_playwright() as pw:
        browser = pw.firefox.launch(
            headless=False, # toggle
        )
        context = browser.new_context(
            viewport={"width": 960, "height": 1080},
            user_agent=bu.random_user_agent(),
            geolocation=bu.random_geolocation(),
            permissions=["geolocation"]
        )
        page = context.new_page()

        print(f"Navegando para a URL: {C.URL}")
        page.goto(C.URL, timeout = 0)

        nav_sync.fill_form(page)
        tab_info = ext_sync.get_info_on_tabs(page)

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

    tabs_info = get_tab_info()
    ic(tabs_info)
    pipeline = create_pipeline(tabs_info)
    ic(pipeline)
    exit()
    aggregated_results = asyncio.run(main_pipelined(pipeline))
    header = aggregated_results[0].keys()
    load_sync.save_to_csv(aggregated_results, header)
#endregion main command


#region main pipelined
async def main_pipelined(pipeline):
    ic(locals())

    async with async_playwright() as pw:
        browser = await pw.firefox.launch(
            headless=False,
        )
        context = await browser.new_context(
            viewport={"width": 960, "height": 1080}
        )
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for item in pipeline:
                task = tg.create_task(nav_async.visit_pages(context, item))
                tasks.append(task)

        results = [task.result() for task in tasks]

        aggregated_results = []
        for result in results:
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

    pipeline = []
    for key, value in tabs_info.items():
        number_of_pages = tabs_info[key].page_num

        for current_page_number in range(0, number_of_pages):
        #region
            start_doc_number = (current_page_number * C.DOCS_PER_PAGE) + 1
            if current_page_number == number_of_pages:
                doc_num_last_page = tabs_info[key].doc_num_last_page
                end_doc_number = start_doc_number + doc_num_last_page
            else:
                end_doc_number = start_doc_number + C.DOCS_PER_PAGE - 1

            data = models.Pipeline(
                tab = key,
                current_page_number = current_page_number + 1,
                start_doc_number = start_doc_number,
                end_doc_number = end_doc_number,
            )
            pipeline.append(data)
        #endregion

    return pipeline
#endregion create pipeline


#region
if __name__ == "__main__":
    load_sync.create_directories()
    app()
#endregion
