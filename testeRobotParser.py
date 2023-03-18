from io import BytesIO
import time
import requests
import urllib.robotparser
from urllib.parse import ParseResult, urljoin, urlparse
from urllib import robotparser
from util_methods import *


# def can_fetch_robot(rp: robotparser.RobotFileParser, obj_url: ParseResult):
#     robotUrl = addRobotToUrl(obj_url)
#     rp.set_url(robotUrl) #robotUrl passa a ter o valor https://www.terra.com/index.html neste exemplo
#     rp.read()
#     print(obj_url.geturl())
#     return rp.can_fetch("*", obj_url.geturl())


# rp = robotparser.RobotFileParser()
# print(can_fetch_robot(rp, urlparse("https://www.twitch.tv/directory")))


# #Exemplo documentacao python
# rp = urllib.robotparser.RobotFileParser()
# rp.set_url("http://www.terra.com/robots.txt")
# rp.read()
# # rrate = rp.request_rate("*")
# # print(rrate.requests)
# # print(rrate.seconds)
# rp.crawl_delay("*")
# print(rp.can_fetch("*", "https://www.terra.com.br/index.html"))
# print(rp.can_fetch("*", "https://www.terra.com/index.html"))


rp = urllib.robotparser.RobotFileParser()
rp.user_agent = "*"

# Obtém a URL base do site para usar como prefixo em urls relativas
base_url = urljoin("http://www.terra.com.br", "/")

# Faz uma requisição ao arquivo robots.txt
robots_url = urljoin(base_url, "robots.txt")
response = requests.get(robots_url)

# Se a requisição falhou ou o status code não é 200, assume que o crawling é permitido
if response.status_code != 200:
    print("falhou")

# Cria um objeto BytesIO com o conteúdo do arquivo robots.txt
robots_bytes = BytesIO(response.content)

rp.set_url(robots_url) #robotUrl passa a ter o valor https://www.terra.com/index.html neste exemplo
rp.read()
print(rp.can_fetch("*", "https://www.terra.com.br/index.html"))


