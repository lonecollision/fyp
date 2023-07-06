from multiprocessing import Pool
import re
import requests
import time

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def poemPreprocess(doc):
    poem_body = doc.find('div', class_ = "field--body").contents
    lines = []
    poem = ""
    for p in poem_body:
        for line in p:
            if not isinstance(line, str):
                lines.append(line.text)
            else:
                lines.append(line)
    for line in lines:       
        poem += line + '\n'
    poem  = re.sub(pattern = "(\\xa0 )", repl = " ", string  = poem)
    poem  = re.sub(pattern = "(\\xa0)", repl  = " ", string  = poem)
    poem  = poem.replace(u'\n\n', u'\n')
    poem = re.sub(pattern = "(\\n\\n ){3,}", repl = "\n\n\n", string = poem)
    poem = poem.strip()

    return poem

def parse(url):
    try:
        page = requests.get(url)

        doc = BeautifulSoup(page.text, "html.parser")

        title = doc.find('div', class_ = "poem__title").contents[1].text.strip()

        author = doc.find('div', itemprop = "author").contents[1].find('span', class_ = "field--title").text.strip()

        poem = poemPreprocess(doc)

        themes = []
        themes_body = doc.find_all('a', href = re.compile(r"/poems\?field_poem_themes_target_id=[0-9]+.*"))
        for theme in themes_body:
            themes.append(theme.text.strip())
        
        occasions = []
        occasions_body = doc.find_all('a', href = re.compile(r"/poems\?field_occasion_target_id=[0-9]+.*"))
        for occasion in occasions_body:
            occasions.append(occasion.text.strip())

        forms = []
        forms_body = doc.find_all('a', href = re.compile(r"/poems\?field_form_target_id=[0-9]+.*"))
        for form in forms_body:
            forms.append(form.text.strip())
        
        if len(poem) > 30000 or len(poem) < 100:
            return(None, None, None, None, None, None)
        
        return(title, author, poem, occasions, themes, forms)
    
    except Exception as e:
        print(e)
        return(None, None, None, None, None, None)

def main():
    links_per_page = 20
    total_pages = 718
    total_poems = total_pages * links_per_page

    path = "poet_poem_urls_without_audio.txt"
    urls = np.loadtxt(path, dtype = "str")
    df = pd.DataFrame(columns = ["Title", "Poet", "Poem", "Occasions", "Themes", "Forms"], index = list(range(urls.size)))

    start_time    = time.time()

    p             = Pool()
    pieces        = p.map(parse, urls)
    p.close()
    p.join()

    end_time      = time.time() - start_time
    print(f"Processing {urls.size} poems took {end_time} seconds using multiprocessing")

    for piece, row in zip(pieces, list(range(total_poems))):
        df.iloc[row] = [piece[0], piece[1], piece[2], piece[3], piece[4], piece[5]]
    df            = df.dropna()
    df.to_csv("data.csv", encoding = "utf-8-sig")

if __name__ == '__main__':
    main()