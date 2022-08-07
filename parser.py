from fake_useragent import UserAgent
import requests, re
from bs4 import BeautifulSoup
from config import login, password
from table import Table

class Parser():
    def __init__(self, csv_file, update_bar):
        self.path=csv_file
        self.domain="https://www.xn--80ablb4ac7ci4e.xn--p1ai"
        self.login_url="https://www.xn--80ablb4ac7ci4e.xn--p1ai/client_account/session"
        self.set_bar=update_bar

    def authorization(self, url, mail, password):
        with requests.session() as session:
            session.post(url,f"utf8=%E2%9C%93&authenticity_token=5DIseCTvwfNBTECjJiOLemrpbVTwbQSthJjtJmfwfYZ3Oi1LdfctrpDsbFWcJxFZ3NrV8aIez6zEaXbmwrnsDg%3D%3D&email={mail}&password={password}&commit=")
        return session

    def parse(self, session, urls, load=False):
        if type(urls)!=list:
            urls=[urls]

        reqs = []
        for link in urls:
            reqs.append(session.get(link, headers={"User-Agent":UserAgent().firefox}))
            if load:
                self.set_bar("Loading...", round(len(reqs)/len(urls)*100, 1))
                
        soups=[BeautifulSoup(res.text, "html.parser") for res in reqs]
        return soups

    def get_item_card(self, item):
        name, sku= item.find("div",class_="product-title on-page").text.strip().split(" артикул ")

        all_categories = list(map(lambda obj: obj.text.strip(), item.find("ul", "breadcrumb").find_all("li")))
        categories = all_categories[1]+" > "+all_categories[-2]
        
        price=int("".join(re.findall("\d", item.find("div", class_="price").text)))

        try: description=item.find("div", class_="product-description").text.strip()
        except AttributeError: description = "-"

        try:
            images_list = list(dict.fromkeys([img.get("href") for img in item.find("div", class_="gallery-main-wrapper").find_all("a")]))
            images = "; ".join(images_list)
        except AttributeError: images = "-"

        dictionary = {"SKU": sku, "NAME": name, "CATEGORIES": categories, "PRICE": price, "DESCRIPTION": description, "IMAGES": images}

        try:
            table = {tr.find("td").text: tr.find("span", class_="property-value").text for tr in item.find("div", id="product-characteristics").find_all("tr")}
            dictionary.update(table)
        except AttributeError: pass

        return dictionary

    def main(self):
        session=self.authorization(self.login_url, login, password)

        ### Parse all categories from catalog page ###
        catalog=self.parse(session, self.domain)[0]
        all_categories_links=[self.domain+a.get("href") for a in catalog.find_all("a", class_="category-title-inner")]
        categories=self.parse(session, all_categories_links)

        ### Parse all pages from every category ###
        all_pages_links=[]
        for category in categories:
            pagination=category.find("ul", class_="pagination").find_all("li", class_="pagination-item")[-2].find("a")
            link=pagination.get("href").split("?page")[0]
            page_count=int(pagination.text.strip())
            for page in range(page_count):
                all_pages_links.append(self.domain+link+"?page="+str(page+1))

        ### Parse all items links from every page ###
        all_items_links=[]
        all_pages=self.parse(session, all_pages_links)
        for page in all_pages:
            page_items_links=[self.domain+title.find("a", class_="product-link").get("href") for title in page.find_all("div", class_="product-title")]
            all_items_links.extend(page_items_links)

        ### Parse every item card ###
        items=self.parse(session, all_items_links, load=True)
        items_cards=[]
        for item in items:
            items_cards.append(self.get_item_card(item))
        
        ### Write to file ###
        Table(self.path, items_cards)
        self.set_bar("Ready",100)
