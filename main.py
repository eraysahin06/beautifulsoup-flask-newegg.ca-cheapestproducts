from flask import Flask, render_template, request
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


def scrape_newegg(search_query):
    base_url = "https://www.newegg.ca"
    search_url = f"{base_url}/p/pl?d={search_query}&N=4131"
    search_page = requests.get(search_url).text
    search_doc = BeautifulSoup(search_page, "html.parser")

    pagination_element = search_doc.find(class_="list-tool-pagination-text").strong
    total_pages = int(str(pagination_element).split("/")[-2].split(">")[-1][:-1])

    found_items = []

    for current_page in range(1, total_pages + 1):
        page_url = f"{base_url}/p/pl?d={search_query}&N=4131&page={current_page}"
        page_content = requests.get(page_url).text
        page_doc = BeautifulSoup(page_content, "html.parser")

        item_grid = page_doc.find(
            class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"
        )
        matched_items = item_grid.find_all(string=re.compile(search_query))

        for matched_item in matched_items:
            parent_element = matched_item.parent
            if parent_element.name != "a":
                continue

            item_link = parent_element["href"]
            item_container = matched_item.find_parent(class_="item-container")
            try:
                item_price = (
                    item_container.find(class_="price-current").find("strong").string
                )
                found_items.append(
                    {
                        "name": matched_item,
                        "price": int(item_price.replace(",", "")),
                        "link": item_link,
                    }
                )
            except:
                pass

    sorted_found_items = sorted(found_items, key=lambda x: x["price"])
    return sorted_found_items


@app.route("/", methods=["GET", "POST"])
def index():
    search_results = []

    if request.method == "POST":
        search_query = request.form.get("search_query")
        search_results = scrape_newegg(search_query)

    return render_template("index.html", search_results=search_results)


if __name__ == "__main__":
    app.run(debug=True)
