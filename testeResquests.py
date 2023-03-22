import requests

header = {"User-Agent": "*"}

r = requests.get("https://shopee.com.br", headers=header)
print(r.status_code)

typeDocument = r.headers['content-type']
print(typeDocument)

if ('html' in typeDocument) and r.status_code == 200:
    print('Está pagina é uma pagina HTML')
    #print(r.content)
    print(r.content.decode())
