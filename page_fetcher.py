from typing import Optional

from bs4 import BeautifulSoup
from threading import Thread
import requests
from urllib.parse import urlparse, urljoin, ParseResult

from crawler.scheduler import Scheduler


class PageFetcher(Thread):
    def __init__(self, obj_scheduler: Scheduler):
        super().__init__()
        self.obj_scheduler = obj_scheduler

    def request_url(self, obj_url: ParseResult) -> Optional[bytes] or None:
        """
        :param obj_url: Instância da classe ParseResult com a URL a ser requisitada.
        :return: Conteúdo em binário da URL passada como parâmetro, ou None se o conteúdo não for HTML
        """

        # Faz conexão informando o coletor a ser utilizado
        headerRequest = {"User-Agent": self.obj_scheduler.usr_agent}
        r = requests.get(obj_url.geturl(), headers=headerRequest)
        typeDocument = r.headers['content-type']

        # Caso a conexão seja bem sucedida e o tipo do documento seja html, retorna o conteudo da página em binário
        # Se o método status_code da classe requests retornar um codigo diferente de 200, a conexão falhou!
        if (r.status_code == 200) and ('html' in typeDocument):
            print(
                f"Pagina html {obj_url.geturl()} foi requisitada com sucesso!")
            return r.content
        else:
            return None

    def discover_links(self, obj_url: ParseResult, depth: int, bin_str_content: bytes):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """

        mainDomain = obj_url.netloc
        soup = BeautifulSoup(bin_str_content, features="lxml")

        for link in soup.select("a[href]"):
            link.clear()
            obj_new_url = urlparse(link.attrs['href'])
            # Removo o fragment da pagina, pois é utilizado como ancora para uma determinada referencia dentro da propria pagina!
            obj_new_url = obj_new_url._replace(fragment='')

            # [OTIMIZACAO] ao inves de adicionar os separadores 'na mão', com a funcao _replace  é possivel formartar a url corretamente
            if (not obj_new_url.netloc):
                obj_new_url = obj_new_url._replace(scheme=obj_url.scheme)
                obj_new_url = obj_new_url._replace(netloc=obj_url.netloc)

            # Caso, dentro da pagina, seja encontrado um novo link para outro endereço, a profundidade é zerada
            if (mainDomain != obj_new_url.netloc):
                new_depth = 0
            else:
                new_depth = depth + 1

            yield obj_new_url, new_depth

    def crawl_new_url(self):
        """
        Coleta uma nova URL, obtendo-a do escalonador
        """

        # Solicitar ao escalonador uma nova URL
        # can_add_page  -->  add_new_page --> get_next_url --> can_fetch_page
        bool_allowed_url = False
        objUrl, depth = None, None

        while not bool_allowed_url:
            # Busca a proxima tupla (url, profundidade) a ser coletada
            packedUrl = self.obj_scheduler.get_next_url()

            if packedUrl:
                # Caso a retorne alguma tupla válida é armazenada no objUrl e depth
                objUrl, depth = packedUrl

            # verifica se a pagina pode ser coletada (se está dentro das regras do robots.txt da pagina)
            bool_allowed_url = self.obj_scheduler.can_fetch_page(objUrl)

        # Fazer a requisição e obter o resultado (em binário)
        try:
            pageContent = self.request_url(objUrl)
        except:
            pageContent = None

        # Caso a URL seja um HTML válido, imprima esta URL e extraia os seus links
        if pageContent:
            # incrementa 1 uma pagina coletada na variavel page_count
            self.obj_scheduler.count_fetched_page()
            # Descobre os links contidos na página
            discoveredLinks = self.discover_links(objUrl, depth, pageContent)

            # os novos links encontrado são adicionada no nosso dicionario de url, caso ja nao tenha sido descorbertos antes, para serem coletados no futuro
            for d_obj_url, d_depth in discoveredLinks:
                self.obj_scheduler.add_new_page(d_obj_url, d_depth)

    def run(self):
        """
        Executa coleta enquanto houver páginas a serem coletadas
        """

        while not self.obj_scheduler.has_finished_crawl():
            self.crawl_new_url()
        
        print("Coleta finalizada!")
