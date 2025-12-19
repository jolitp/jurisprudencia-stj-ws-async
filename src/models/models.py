from pydantic import BaseModel
import typing
from playwright.sync_api._generated import Locator


class Pipeline(BaseModel):
    tab: str
    current_page_number: int
    start_doc_number: int
    end_doc_number: int


class PageData(BaseModel):
    tab: str
    page_number: int
    data: list
    elapsed_time: float


class TabData(BaseModel):
    element_id: str
    name: str | None
    text: str | None
    locator: typing.Any
    doc_num: int | None
    page_num: int | None
    doc_num_last_page: int | None
    is_active: bool | None
    errors: list | None
