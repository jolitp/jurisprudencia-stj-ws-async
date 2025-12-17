import json

DEBUG: bool = False
# DEBUG: bool = True # toggle
TIMEOUT: int = 120_000 # 120 sec
URL: str = 'https://processo.stj.jus.br/SCON/'
DOCS_PER_PAGE = 50

#pesquisa modelo 2 (minha) (from json)

PESQUISA = None
with open('pesquisa.json', 'r') as file:
    PESQUISA = json.load(file)