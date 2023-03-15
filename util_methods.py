from urllib.parse import ParseResult, urlparse


def addSchemeToUrl(obj_url: ParseResult) -> str:
    url = obj_url.geturl()
    if not obj_url.scheme:
        url = 'https://' + url
    return url


def addRobotToUrl(url: ParseResult) -> str:
    robotUrl = addSchemeToUrl(urlparse(url.netloc))
    return robotUrl + '/robots.txt'
