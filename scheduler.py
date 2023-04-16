from datetime import time
from urllib import robotparser
from urllib.parse import ParseResult
from crawler.util_methods import *

from util.threads import synchronized
import time as ti
from collections import OrderedDict
from .domain import Domain

RED = "\033[1;31m"
GREEN = "\033[0;32m"
CYAN = "\033[1;36m"
RESET = "\033[0;0m"


class Scheduler:
    # tempo (em segundos) entre as requisições
    TIME_LIMIT_BETWEEN_REQUESTS = 20

    def __init__(self, usr_agent: str, page_limit: int, depth_limit: int, arr_urls_seeds: ParseResult):
        """
        :param usr_agent: Nome do `User agent`. Usualmente, é o nome do navegador, em nosso caso,  será o nome do coletor (usualmente, terminado em `bot`)
        :param page_limit: Número de páginas a serem coletadas
        :param depth_limit: Profundidade máxima a ser coletada
        :param arr_urls_seeds: ?

        Demais atributos:
        - `page_count`: Quantidade de página já coletada
        - `dic_url_per_domain`: Fila de URLs por domínio (explicado anteriormente)
        - `set_discovered_urls`: Conjunto de URLs descobertas, ou seja, que foi extraída em algum HTML e já adicionadas na fila - mesmo se já ela foi retirada da fila. A URL armazenada deve ser uma string.
        - `dic_robots_per_domain`: Dicionário armazenando, para cada domínio, o objeto representando as regras obtidas no `robots.txt`
        """

        self.usr_agent = usr_agent
        self.page_limit = page_limit
        self.depth_limit = depth_limit
        self.page_count = 0

        self.dic_url_per_domain = OrderedDict()
        self.set_discovered_urls = set()
        self.dic_robots_per_domain = {}
        
        seedPages = [(obj_url, 0) for obj_url in arr_urls_seeds]
        
        for page in seedPages:
            self.add_new_page(*page) #'*' -> serve para descompactar as tuplas criadas em seedPage e envialas como parametros separados      
        

    @synchronized
    def count_fetched_page(self) -> None:
        """
        Contabiliza o número de paginas já coletadas
        """
        self.page_count += 1
        
        print(GREEN + self.page_count + CYAN + " Páginas alcançadas")

    def has_finished_crawl(self) -> bool:
        """
        :return: True se finalizou a coleta. False caso contrário.
        """
        return self.page_count >= self.page_limit or not self.dic_url_per_domain

    @synchronized
    def can_add_page(self, obj_url: ParseResult, depth: int) -> bool:
        """
        :return: True caso a profundidade for menor que a maxima e a url não foi descoberta ainda. False caso contrário.
        """

        if (depth > self.depth_limit) or (obj_url.geturl in self.set_discovered_urls):
            print(RED + "A url: " + obj_url.geturl() +
                  " não pode ser adicionada!" + RESET)
            return False

        self.set_discovered_urls.add(obj_url.geturl())
        print(CYAN + "A url: " + obj_url.geturl() +
              " pode ser adicionada!" + RESET)
        return True

    @synchronized
    def add_new_page(self, obj_url: ParseResult, depth: int) -> bool:
        """
        Adiciona uma nova página
        :param obj_url: Objeto da classe ParseResult com a URL a ser adicionada
        :param depth: Profundidade na qual foi coletada essa URL
        :return: True caso a página foi adicionada. False caso contrário
        """
        # https://docs.python.org/3/library/urllib.parse.html
    
        if self.can_add_page(obj_url, depth):
            addDomain = Domain(obj_url.netloc, 10)

            # Verifica se já existe uma chave com o objeto Domain (Url, time_Limit)
            if addDomain in self.dic_url_per_domain:
                # Caso a url exista na lista de dicionarios, ele irar adicionar uma pagina de profundidade
                if (obj_url.geturl() in self.dic_url_per_domain):
                    self.dic_url_per_domain[addDomain].append(
                        (obj_url, depth))
            else:
                # Caso não exista esta chave do Domain, ele cria uma
                self.dic_url_per_domain[addDomain] = [
                    (obj_url, depth)]

            print(GREEN + "Pagina adicionada com sucesso!" + RESET)
            return True

        print(RED + "Nao foi possivel adicionar esta pagina!" + RESET)
        return False

    @ synchronized
    def get_next_url(self) -> tuple:
        """
        Obtém uma nova URL por meio da fila. Essa URL é removida da fila.
        Logo após, caso o servidor não tenha mais URLs, o mesmo também é removido.
        """

        servers_list = self.dic_url_per_domain  # lsita de servidores

        if not servers_list:
            print(CYAN + "Fila de servidores vazias, aguardando 25 segs..." + RESET)
            ti.sleep(25)
            return None, None

        else:
            for key, value in servers_list.items():
                if key.is_accessible():  # Encontra o primeiro servidor acessivel
                    break
            tupla_d = value[0][0]  # objeto ParseResult (url)
            tupla_n = value[0][1]  # profundidade

            # Acessa a lista de tuplas na chave objeto_domain_1
            tuplas = servers_list[key]
            # Percorre a lista e remove a tupla que você deseja remover
            for i, t in enumerate(tuplas):
                if t in value:
                    del tuplas[i]
                    self.dic_url_per_domain[key] = tuplas
                    break

            if not servers_list[key]:
                print(f"{CYAN} Servidor: {key} removido {RESET}")
                self.dic_url_per_domain.pop(key)

            print(GREEN + f"Servidor {key} acessado!" + RESET)
            return tupla_d, tupla_n

    def can_fetch_page(self, obj_url: ParseResult) -> bool:
        """
        Verifica, por meio do robots.txt, se uma determinada URL pode ser coletada
        """
        text = ''
        is_allowed_url = False

        try:
            # instancia da classe RobotFileParser
            rp = robotparser.RobotFileParser()
            nam_domain = obj_url.netloc

            # Ler o arquivo robots.txt do dominio
            robotUrl = addRobotToUrl(obj_url)
            rp.set_url(robotUrl)
            rp.read()

            #verifica se ja foi realizada uma requisicao no dominio
            if nam_domain in self.dic_robots_per_domain:
                text = f"{RED}[FALHA]{RESET} Já foi realizada a requisição do domínio {obj_url.netloc} uma vez!"
                is_allowed_url = False
            else:
                #caso não tenha feito, eh adicionado o dominio no dicionario
                self.dic_robots_per_domain[nam_domain] = '1'

                if rp.can_fetch("*", obj_url.geturl()):
                    text = f"{GREEN}A url {obj_url.geturl()} pode ser coletada!{RESET}"
                    is_allowed_url = True
                else:
                    text = f"{RED}A url {obj_url.geturl()} não pode ser coletada!{RESET}"
                    is_allowed_url = False
            
            print(text)
            return is_allowed_url

        except Exception as e:
            print(
                RED + f"Falha ao ler o arquivo robots.txt do dominio {obj_url.netloc}" + RESET)
            return False
