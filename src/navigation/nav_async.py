import src.config.constants as C
from src.extraction import ext_sync
from src.navigation import nav_sync


async def visit_pages(context, item):
    page = await context.new_page()

    await page.goto(C.URL)

    # await nav_sync.fill_form(page)
    # await tab_info = ext_sync.get_info_on_tabs(page)
    return item
    ...