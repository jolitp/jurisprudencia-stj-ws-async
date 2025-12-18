import json
import datetime

DEBUG: bool = False
# DEBUG: bool = True # toggle
TIMEOUT: int = 120_000 # 120 sec
URL: str = 'https://processo.stj.jus.br/SCON/'
DOCS_PER_PAGE = 50

#pesquisa modelo 2 (minha) (from json)

SEARCH_TERMS = None
with open('pesquisa.json', 'r') as file:
    SEARCH_TERMS = json.load(file)

PROXIES = None
path = "proxies/free-br-proxies-from-proxyscrape.txt"
# path = "proxies/free-world-proxies-from-proxyscape.txt"
with open(path, 'r') as file:
    PROXIES = file.readlines()

DT_NOW = datetime.datetime.now()
DIRS = {
    "save_root": "__execucoes__",
    "current_execution": DT_NOW.strftime("%Y_%m_%d_-_%H_%M_%S"),
    "debug": "debug",
    "screenshots": "screenshots"
}