import src.config.constants as C
from src.loading import load_sync
from src.extraction import ext_sync
from src.navigation import nav_sync
from src.navigation import nav_async
from src.utils import browser_utils as bu
import asyncio
import time
import datetime
import random
import typer
import random
from typing import NamedTuple
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
# from rich.traceback import install # using typer's rich, configure there
from rich import print
from rich.console import Console
from icecream import ic

# import logging
# def warn(s):
#     logging.warning("%s", s)
# def toString(obj):
#    if isinstance(obj, str):
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
        proxy_server = random.choice(C.PROXIES)
        ic(proxy_server)
        browser = pw.firefox.launch(
            headless=False, # toggle
            # proxy = {
            #     "server": proxy_server
            # }
        )
        context = browser.new_context(
            viewport={"width": 960, "height": 1080},
            # is_mobile=True,
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
            errors = tab_info[tab]["errors"]
            if errors:
                print(f"[red]Erros na aba {tab}[/]")

        browser.close()
        print(f"Fechando navegador.")
    return tab_info
    ...
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

    asyncio.run(main_pipelined(pipeline))
#endregion main command


#region main pipelined
async def main_pipelined(pipeline):
    ic(locals())
    async with async_playwright() as pw:
        # proxy_server = random.choice(C.PROXIES)
        # ic(proxy_server)
        browser = await pw.firefox.launch(
            headless=False,
            # proxy = {
            #     "server": proxy_server # giving error:
# Error: Page.goto: NS_ERROR_UNKNOWN_HOST
# Call log:
#   - navigating to "https://processo.stj.jus.br/SCON/", waiting until "load"
            # }
        )
        context = await browser.new_context(
            viewport={"width": 960, "height": 1080}
        )
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for item in pipeline:
                ic(item)
                # exit()
                task = tg.create_task(nav_async.visit_pages(context, item))
                tasks.append(task)

        results = [task.result() for task in tasks]

        ic(results)
        ic(len(results))

        aggregated_results = []
        for result in results:
            data = result['data']
            for d in data:
                aggregated_results.append(d)

        await browser.close()

    header = aggregated_results[0].keys()
    await load_sync.save_to_csv(aggregated_results, header)
#endregion main pipelined


#region create pipeline
def create_pipeline(
    tabs_info# = dict[str, dict[str, None]]
    ):
    ic(locals())

    ic(type(tabs_info))
    ic(tabs_info.keys())
    ic(type(tabs_info["acordaos_1"]))

    single_tab_pipeline = []
    # for tab in tabs_info:
    tab = "acordaos_2"
    # tabs = [ ... for tab in tabs_info ]
    number_of_pages = tabs_info[tab]["page_num"]
    for current_page_number in range(0, number_of_pages):
        start_doc_number = (current_page_number * C.DOCS_PER_PAGE) + 1
        if current_page_number == number_of_pages:
            doc_num_last_page = tabs_info[tab]["doc_num_last_page"]
            end_doc_number = start_doc_number + doc_num_last_page
        else:
            end_doc_number = start_doc_number + C.DOCS_PER_PAGE - 1

        data = {
            "tab": tab,
            "current_page_number": current_page_number + 1,
            "start_doc_number": start_doc_number,
            "end_doc_number": end_doc_number,
            # "num_docs_on_page": num_docs_on_page
        }
        single_tab_pipeline.append(data)
    # for current_page_number in range(0, number_of_pages):

    return single_tab_pipeline
    ...
#endregion create pipeline


#region
if __name__ == "__main__":
    load_sync.create_directories()
    app()
#endregion
