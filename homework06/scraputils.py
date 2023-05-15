import requests  # type: ignore
from bs4 import BeautifulSoup


def extract_news(parser):
    """Extract news from a given web page"""
    news_list = []

    tbl_list = parser.table.findAll("table")[1].select("tr[class=athing]")
    title = [tbl_list[i].find("span", {"class": "titleline"}).find("a").text for i in range(len(tbl_list))]
    urls = [
        tbl_list[i].find("span", {"class": "titleline"}).find("a").attrs.get("href", "Not found")
        for i in range(len(tbl_list))
    ]
    tbl_list = parser.table.findAll("table", limit=2)[1].select("td[class=subtext]")
    comments = []
    for i in range(len(tbl_list)):
        com = tbl_list[i].findAll("a", href=True)[-1].text
        commentary = 0 if com == "discuss" else int(com[: com.find("c") - 1])
        comments.append(commentary)

    points = [tbl_list[i].findAll("span", {"class": "score"})[0].text for i in range(len(tbl_list))]
    for i in range(len(points)):
        string = points[i]
        points[i] = int(string[: string.find("p") - 1])
    authors = [tbl_list[i].findAll("a", {"class": "hnuser"})[0].text for i in range(len(tbl_list))]
    for i in range(len(tbl_list)):
        new = dict(author=authors[i], comments=comments[i], points=points[i], title=title[i], url=urls[i])
        news_list.append(new)
    return news_list


def extract_next_page(parser):
    """Extract next page URL"""
    return parser.table.find("a", {"class": "morelink"}).get("href", "Not found")


def get_news(url, n_pages=1):
    """Collect news from a given web page"""
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.table is None:
            break
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news


if __name__ == "__main__":
    url = "https://news.ycombinator.com/newest"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    print(extract_news(soup))
    print("\n\n\n")
    print(extract_next_page(soup))
    print("\n\n\n")
    print(get_news("https://news.ycombinator.com/newest", n_pages=2)[:4])
