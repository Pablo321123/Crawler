import time
from urllib.parse import urlparse
from crawler.scheduler import Scheduler
from crawler.page_fetcher import PageFetcher

# Scheduler
userAgents = 'shelbyBot (shelbybot1.wordpress.com)'
page_limit = 50000  # Limite de 50000 paginas
depth_limit = 6  # Até 6 de profundidade por pagina
countPageFetcher = 200

# Seeds
list_UrlSeeds = [urlparse('https://best.aliexpress.com/'),
                 urlparse('https://shopee.com.br'),
                 urlparse('https://br.shein.com'),
                 urlparse('https://ge.globo.com'),
                 urlparse('https://www.sbt.com.br'),
                 urlparse('https://www.apple.com/br'),
                 urlparse('https://www.tecmundo.com.br'),
                 urlparse('https://github.com'),
                 urlparse('https://www.microsoft.com/pt-br'),
                 urlparse('https://www.amazon.com.br/?tag=desktopbr-20')
                 ]

objScheduler = Scheduler(userAgents, page_limit, depth_limit, list_UrlSeeds)

startTime = time.time()

list_obj_fetcher = []
for i in range(countPageFetcher):
    list_obj_fetcher.append(PageFetcher(objScheduler))
    # Sempre o PageFetcher recém criado será executado, o indice -1 garante que conseguiremos acessar sempre o ultimo da lista
    list_obj_fetcher[-1].start()

for thread in list_obj_fetcher:
    thread.join()
    
endTime = time.time()

#Resultados
print(f"Paginas encontradas: {objScheduler.page_count}")
print(f"URL encontradas: {len(objScheduler.set_discovered_urls)}")
print(f"Tempo gasto: {round(endTime - startTime,2)} segundos")
print(f"Thread utilidas: {countPageFetcher}")