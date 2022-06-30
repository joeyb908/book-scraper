from bs4 import BeautifulSoup
import lxml
import requests
import pprint
from flask import Flask

# pp = pprint.PrettyPrinter(indent=4, compact=True)
# BASE_URL = 'https://www.royalroad.com/'
# URL = 'https://www.royalroad.com/fiction/21220/mother-of-learning'
# response = requests.get(url=URL)
# webpage = response.text
# soup = BeautifulSoup(webpage, 'lxml')
# # pp.pprint(soup)
#
# chapter_list = []
# chapters = soup.findAll(class_='chapter-row')
# for chapter in chapters:
#     head, sep, tail = chapter.get_text().strip().partition('\n')
#     link = chapter.find(href=True)
#     appended_link = f'{BASE_URL}{link["href"]}'
#     chapter_list.append([head, appended_link])
#     # pp.pprint(link['href'])
#     # pp.pprint(head)
#
# pp.pprint(chapter_list)

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route("/", methods=['GET'])
def home():
    return "<p>Hello, World!</p>"



