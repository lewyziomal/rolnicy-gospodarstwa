import requests
from bs4 import BeautifulSoup


def get_coordinates(location: str) -> list[float]:
    url = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    lat = float(soup.select('.latitude')[0].text.replace(',', '.'))
    lon = float(soup.select('.longitude')[0].text.replace(',', '.'))
    return [lat, lon]
