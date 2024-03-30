## THIS SCRIPT IS VALID ##

import os
import requests as rq
import re
from bs4 import BeautifulSoup, Comment

def find_pages_count(soup):
    comment_text = "Last page link"
    comment = soup.find(text=lambda text: isinstance(text, Comment) and comment_text in text)
    if comment:
        next_element = comment.find_next("li")
        last_page_url = next_element.find("a")["href"]
        pages_count = last_page_url[last_page_url.index("=") + 1: last_page_url.index("&")]
        pages_count = int(pages_count)

        return pages_count
    else:
        return 1


# current solution: call main without argument
# it will read its queries itself
def main(RecordClass):
    records = []
    script_name = os.path.basename(__file__)
    queries_file_name = os.path.splitext(script_name)[0]

    search_result = ""
    NL = '\n'
    delimiter = '\t'
    base_url = "https://trhknih.cz"
    



    with open(f'queries/{queries_file_name}.txt') as FILE:
    
        for LINE in FILE:
            if LINE.strip():
                url = f"{base_url}/hledat?q={LINE}&type=issue"
                response = rq.get(url)
                if response.status_code >= 200 and response.status_code < 300:
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')
                    pages = find_pages_count(soup)

                    for pagenum in range(1, pages+1):
                        url = f"{base_url}/hledat?q={LINE}&type=issue&page={pagenum}"
                        html = rq.get(url).text
                        soup = BeautifulSoup(html, 'html.parser')

                        span6_list = soup.find_all("div", attrs={"class": "span6"})
                        for span6 in span6_list:
                            span_price = span6.find("span", attrs={"class": "ask-count"})
                            if span_price:
                                record = RecordClass()
                                record.link = f"{base_url}{span6.find("a")["href"]}"
                                record.book = span6.find("a").text
                                record.price = span6.find("span").text
                                record.year, record.publisher = span6.find_all("em")[0].text, span6.find_all("em")[1].text

                                innerHTML = span6.decode_contents()
                                text_after_kc = innerHTML[innerHTML.index("Kč"):]
                                text_after_br = text_after_kc[text_after_kc.index("<br/>") + 5:]
                                text_before_second_br = text_after_br[:text_after_br.index("<br/>")]
                                record.author = text_before_second_br.strip()

                                """
                                author = span6.text
                                for item in [record.book, record.price, record.year]:
                                    author = author.replace(item, '')
                                first_following_escape_idx = author.index('\t')
                                author = author[:first_following_escape_idx]
                                record.author = author.strip()
                                """

                                records.append(record)
    return records