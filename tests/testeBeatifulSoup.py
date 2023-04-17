from bs4 import BeautifulSoup
import requests

url = "https://www.netshoes.com.br/"

headerRequest = {"User-Agent": "*"}
r = requests.get(url, headers=headerRequest)
typeDocument = r.headers['content-type']

content = None

if (r.status_code == 200) and ('html' in typeDocument):
    content = r.content
else:
    content = None

if content is not None:
    soup = BeautifulSoup(content, features="lxml")

    for link in soup.select("a[href]"):
        # Limpa o conteúdo de uma tag, neste caso, ele manterá somente o a[href] que pedimos
        link.clear()
        # Para pegar o link da tag (href), basta acessar o dicionario 'attr' do objeto 'link' e passar a tag desejada, neste caso queremos o ['href']
        href_link = link.attrs['href']
        # print(link)
        print(href_link)
        obj_new_url = None
        new_depth = None
