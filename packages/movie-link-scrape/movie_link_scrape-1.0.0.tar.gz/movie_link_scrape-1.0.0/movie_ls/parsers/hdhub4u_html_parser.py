# version 1.0.0

from bs4 import BeautifulSoup

class HdHub4uHtmlParser:
    @staticmethod
    def parse_media_links(html_content) -> list[dict[str, str]]:
        select_filter = 'ul.recent-movies li'
        soup = BeautifulSoup(html_content, "html.parser")
        movie_list = soup.select(select_filter)
        links = []
        for movie in movie_list:
            img_url = movie.find('img')['src']
            a_url = movie.find('a', href=True)['href']
            p_text = movie.find('p').text.strip()
            data = {
                "img_url": img_url,
                "page_url": a_url,
                "caption": p_text
            }
            links.append(data)
        return links

    @staticmethod
    def parse_download_links(html_content) -> list[dict[str, str]]:
        soup = BeautifulSoup(html_content, "html.parser")
        headings = soup.find_all(['h3', 'h4'], attrs={'data-ved': '2ahUKEwi0gOTl-ozlAhWfILcAHVY0DbIQyxMoADAvegQIERAJ'})
        links = []
        for heading in headings:
            a_tag = heading.find('a')
            if a_tag and a_tag.get('href'):
                links.append({a_tag.text.strip(): a_tag['href']})
        return links