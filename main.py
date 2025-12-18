import src.config.constants as C
from src.loading import load_async
from src.navigation import nav_sync
from src.extraction import ext_sync
from src.navigation import nav_async
import asyncio
import time
import datetime
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

DT_NOW = datetime.datetime.now()


#region main command
@app.command()
def main(
    debug: bool = False
):
    ic.disable()
    if debug:
        ic.enable()
    ic()

    # do a preliminary run to get info on number of documents of each tab
    tab_info = {}
    with sync_playwright() as pw:
        proxy_server = random.choice(C.PROXIES)
        # ic(proxy_server)
        browser = pw.firefox.launch(
            headless=False, # toggle
            # proxy = {
            #     "server": proxy_server
            # }
        )
        context = browser.new_context(viewport={"width": 960, "height": 1080})
        page = context.new_page()

        print(f"Navegando para a URL: {C.URL}")
        page.goto(C.URL)

        nav_sync.fill_form(page)
        tab_info = ext_sync.get_info_on_tabs(page)

        tabs = ["acordaos_1", "acordaos_2", 'decisoes_monocraticas']
        for tab in tabs:
            errors = tab_info[tab]["errors"]
            if errors:
                print(f"[red]Erros na aba {tab}[/]")

        browser.close()
    pipeline = create_pipeline(tab_info)

    asyncio.run(main_pipelined(pipeline))
#endregion main command


#region main pipelined
async def main_pipelined(pipeline):
    async with async_playwright() as pw:
        # proxy_server = random.choice(C.PROXIES)
        # ic(proxy_server)
        browser = await pw.firefox.launch(
            headless=False,
            # proxy = {
            #     "server": proxy_server
            # }
        )
        context = await browser.new_context(
            viewport={"width": 960, "height": 1080}
        )
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for item in pipeline:
                task = tg.create_task(
                    nav_async.visit_pages(context, item)
                )
                tasks.append(task)

        results = [task.result() for task in tasks]

        ic(results)
        ic(len(results))

        aggregated_results = []
        for result in results:
            data = result['data']
            for d in data:
                aggregated_results.append(d)
            # aggregated_results.append(data)
            # ic(len(data))
            # elapsed_time = result['elapsed_time']

        # ic(aggregated_results[0][0].keys())
        # ic(len(aggregated_results))

        await browser.close()

    header = aggregated_results[0].keys()
    await load_async.save_to_csv(
        aggregated_results,
        header,
        # tab,
        script_start_datetime=DT_NOW
    )


    ...
#endregion main pipelined


#region create pipeline
def create_pipeline(tab_info):

    number_of_pages = tab_info["acordaos_1"]["page_num"]
    pipeline = []
    for current_page_number in range(0, number_of_pages):
        start_doc_number = (current_page_number * C.DOCS_PER_PAGE) + 1
        if current_page_number == number_of_pages:
            doc_num_last_page = tab_info["acordaos_1"]["doc_num_last_page"]
            end_doc_number = start_doc_number + doc_num_last_page
            # num_docs_on_page = end_doc_number - start_doc_number
        else:
            end_doc_number = start_doc_number + C.DOCS_PER_PAGE - 1
            # num_docs_on_page = end_doc_number - start_doc_number

        data = {
            "tab": "acordaos_1", # CHANGEME
            "current_page_number": current_page_number + 1,
            "start_doc_number": start_doc_number,
            "end_doc_number": end_doc_number,
            # "num_docs_on_page": num_docs_on_page
        }
        pipeline.append(data)
    return pipeline
    ...
#endregion create pipeline


#region
if __name__ == "__main__":
    app()
#endregion
