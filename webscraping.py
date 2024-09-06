from bs4 import BeautifulSoup
from urllib.request import urlopen

url = "https://www.bbc.com/pidgin/articles/cdd79velen5o"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")
containers = soup.find('main').find_all('div')

text_to_save = ''
for div in containers:
    for paragraphs in div:
        if paragraphs.string != None:
            text_to_save += paragraphs.string
            text_to_save += '\n'
print(text_to_save)
# count = 0
# for text in text_to_save:
#     print(count)
#     print(text)
#     count+= 1
with open('WebScrapingData/pidgin_data.txt', 'a') as f:
    f.write(text_to_save)
    f.write('\n')



