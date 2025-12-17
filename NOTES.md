# Notes

## Outline of what the program needs to do

- [ ] get parameters from CLI
  - [-] subcommands (2 mandatory)
  - [ ] options (flags)
    - [x] debug flag
    - [ ] number of simultaneous browsers to open
- [x] get data from `pesquisa.json` to get search parameters
- [-] validade the date in `pesquisa.json` to see if it makes sense
  - [-] strings are not blank
  - [-] data in correct format
  - [-] initial and final data are in order
- [x] do a surveilance run to get the info needed
  - [x] number of pages
  - [x] number of documents
- [ ] asyncronously get the data into temporary files
  - [ ] visit each page
  - [ ] get all documents into a list
  - [ ] get data on each document
  - [ ] csv with a single document (?)
  - [ ] csv with a single page of documents
  - [ ] images
- [ ] after all documents have been downloaded:
  - [ ] join csv together
  - [ ] save console to html

## Corner cases

- [>] tabs have 404 page inside
- [ ] page has 0 documents
- [ ] pdf link unavailable (?)
- [ ] document is `recurso repetitivo` (?)
- [ ]

## RESEARCH

can python get the current ram available?
how much ram playwright uses?

## Testing

test if playwright finds the correct elements on the page
TODO change those to css selectors?
search_config = {
    "criterio_de_pesquisa_xpath": '//*[@id="pesquisaLivre"]',
    "pesquisa_avancada_xpath": '//*[@id="idMostrarPesquisaAvancada"]',
    "data_de_julgamento_inicial_xpath": '//*[@id="dtde1"]',
    "data_de_julgamento_final_xpath": '//*[@id="dtde2"]',
    "botao_buscar_xpath": 'xpath=/html/body/div[1]/section[2]/div[3]/form[1]/div[2]/div[2]/div[2]/div[1]/div/button',
}

- [ ] sections = doc.find_all("div", attrs={ "class": "paragrafoBRS" })
- [ ] n_doc_el = doc.find("div", { "class": "clsNumDocumento" })
- [ ] section_name_el = section.find("div", attrs={ "class": "docTitulo" })
- [ ] section_value_el = section.find("div", attrs={ "class": "docTexto" })
- [ ] href = attrs = { "data-bs-original-title": "Exibir o inteiro teor do acórdão."}
TODO get the actual pdf link for decisoes monocraticas
- [ ] attrs = { "class": "barraDocRepetitivo" }

test functionality

## asyncio notes

- to sleep use asyncio.sleep()

- task() = if you need to interact with the task before it finishes

- gather() to run a known amoount of coroutines
  - do not use the gather() function if you need error handling, unless
  - you pass `return_exceptions=True` as a parameter
  - if one task fails, the other ones are not cancelled
  - use it if you can live with loss of data from errored coroutines
    - or you don't need the restult for all the tasks

  - coroutines = [...] # list of coroutine objects
  - results = await asyncio.gather(*coroutines, return_exceptions=True)
  - you can pass both coroutines or tasks to gather()
    - pass coroutines themselves if you only need the results
    - pass tasks if you want to monitor or interact with the tasks before they complete

- TaskGroup() = built-in error handling
  - cancels all the other tasks uppon a single task failure
  - async context manager = async with asyncio.TaskGroup() as tg:
  - ... task = tg.create_task(async_function_"call"(a, b))
  - you do not need to await inside the context manager
  - use it if you need the result from all the tasks

- Synchronization options
  - lock() = read from shared resource one at a time
    - lock = asyncio.lock()
    - async with lock:
  - semaphore = allows multiple corroutines to read the same resource
    - throtle the program. Useful for network requests
    - execute only a hadful of coroutines at a time from a bigger pool of coroutines
  - event = set a flag from inside a coroutine
