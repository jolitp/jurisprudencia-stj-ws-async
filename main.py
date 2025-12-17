import src.config.constants as C

from src.navigation import nav
from src.extraction import ext

import asyncio
import time
import datetime
import typer
from icecream import ic

from rich import print
# import playwright
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# from rich.traceback import install
# import pretty_errors
from rich.console import Console

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

    # do a preliminary run

    tab_info = {}
    with sync_playwright() as pw:
        browser = pw.firefox.launch(
            headless=False, # toggle
        )
        context = browser.new_context(viewport={"width": 960, "height": 1080})
        page = context.new_page()

        print(f"Navegando para a URL: {C.URL}")
        page.goto(C.URL)

        nav.fill_form(page)
        tab_info = ext.get_info_on_tabs(page)
        # ic(tab_info)

        time.sleep(2)

    ic(tab_info)

    with async_playwright() as pw:
        # spawn many (3-5) instances of the browser
        ...


if __name__ == "__main__":
    app()
