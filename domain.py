from datetime import datetime, timedelta
from collections import OrderedDict
from urllib.parse import urlparse
import requests
from traceback import *

RED = "\033[1;31m"
GREEN = "\033[0;32m"
BOLD = "\033[;1m"
RESET = "\033[0;0m"


class Domain:
    def __init__(self, nam_domain: str, time_limit_between_requests: int):
        self.time_last_access = datetime(1970, 1, 1)
        self.nam_domain = nam_domain
        self.time_limit_seconds = time_limit_between_requests

    @property
    def time_since_last_access(self) -> timedelta:
        # Datetime atual (Sempre maior que a data do acesso anterior) - Datetime do ultimo acesso
        diference = (datetime.now() - self.time_last_access)
        return diference

    def accessed_now(self) -> None:
        # Gravação do Datetime atual
        self.time_last_access = datetime.now()

    def is_accessible(self) -> bool:
        try:
            # Caso o nome do dominio nao esteja com o formato de URL (sem protocolo de segurança ('HTTPS'), adicionamos ele abaixo
            url = self.nam_domain
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'https://' + url

            # print(url)

            response = requests.get(url)
            # Se o método status_code da classe requests retornar um codigo diferente de 200, a conexão falhou!
            if (response.status_code == 200) and (self.time_since_last_access.seconds > self.time_limit_seconds):
                print(GREEN + "O dominio está acessivel!" + RESET)
                return True

        except Exception as e:
            print(self.nam_domain)

        print(RED + "Falha ao se conectar!" + RESET)
        return False

    def __hash__(self):
        return hash(self.nam_domain)

    def __eq__(self, domain):
        return self.nam_domain == domain

    def __str__(self):
        return self.nam_domain

    def __repr__(self):
        return str(self)
