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

from rich import print
# import playwright
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# from rich.traceback import install
# import pretty_errors
from rich.console import Console

from icecream import ic

DT_NOW = datetime.datetime.now()

# import logging
# def warn(s):
#     logging.warning("%s", s)

# TODO try to make it use rich print
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

console = Console()
# ic.configureOutput(includeContext=True)

# app = typer.Typer(pretty_exceptions_enable=False)
app = typer.Typer(pretty_exceptions_show_locals=False)


# import pretty_errors

DT_NOW = datetime.datetime.now()


#region main
@app.command()
def main(
    debug: bool = False
):
    # print("debug: ", debug)
    ic.disable()
    if debug:
        ic.enable()
    ic()
    # C.PESQUISA["ACORDAOS_1"]
    # C.PESQUISA["ACORDAOS_2"]
    # C.PESQUISA["DECISOES_MONOCRATICAS"]

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

        # time.sleep(5)
        browser.close()
    # just go through tab 1 for now

    # make a segmentation plan
    # - in an array put information about:
    #   - tab
    #   - page number
    #   - document nubmer at the start of page
    #   - document nubmer at the end of page
    #   - number of documents on page

    # TODO move it somewhere else
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
    ic(pipeline)

    asyncio.run(main_pipelined(pipeline))

    # TODO move to async function
    # async with async_playwright() as pw:
        # spawn many (3-5) instances of the browser [?]
        # OR spawn many tabs in the same browser
        # OR multiple contex

        # I would recommend to use multiple browser contexts (browser.new_page()) does create a context for you internally.
        # ...



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
                    nav_async.visit_pages(context, item, console)
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

if __name__ == "__main__":
    app()
