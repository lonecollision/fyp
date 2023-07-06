from multiprocessing import Pool
import numpy as np
import re
import requests
import time

from bs4 import BeautifulSoup
import pandas as pd

def findPoem(doc):
    o_poem = doc.find_all('div', class_="o-poem")[0]
    poem_lines = o_poem.contents
    lines = []
    poem = ""
    for line in poem_lines:
        lines.append(line.text)
    for text in lines:
        if text == ' ' or text == '':
            text = '\r '
        text = "\r " + text
        text  = re.sub(pattern = "(\\r )+",
                    repl    = "\r ",
                    string  = text)
        poem += text

    poem = poem.replace(u'\r ',    u'\n')
    poem = poem.replace(u'\xa0',   u' ')
    poem = poem.replace(u'\u2003', u' ')
    poem = poem.replace(u'\u2009', u' ')
    poem = poem.strip()
    poem = re.sub(pattern = "(\\n){3,}",
              repl    = "\n\n",
              string = poem)
    return poem

def parse(url):
    try:
        page = requests.get(url)
        doc = BeautifulSoup(page.text, "html.parser")
        title = doc.find_all("h1")[0].text.strip()
        author = doc.find_all("a", href = re.compile(".*poets/.*"))[0].text
        poem = findPoem(doc)

        # csv files have a limit of 32,767 characters per cell 
        if len(poem) > 30000 or len(poem) < 100:
            return(None, None, None)
        return(title, author, poem)
    
    except Exception as e:
        print(e)
        return(None, None, None)

def main():
    total_batches     = 11
    batch_size        = 200
    links_per_page    = 20
    total_poems       = batch_size * links_per_page

    # Generates list of file names for batches of urls
    file_names        = [""] * total_batches
    for i in range(total_batches):
        file_names[i] = "poem_urls" + str(i * batch_size + 1) + "-" + str(batch_size * (i + 1)) + ".txt"

    # Load each batch of urls
    for file_name in file_names:
        print(file_name)
        urls          = np.loadtxt(file_name, dtype = "str")
        df            = pd.DataFrame(columns = ["Title", "Poet", "Poem"], index = list(range(urls.size)))

        start_time    = time.time()

        p             = Pool()
        pieces        = p.map(parse, urls)
        p.close()
        p.join()

        end_time      = time.time() - start_time

        batch_name    = "poems" + re.findall(r'\d.*\d', file_name)[0]
        print(f"{batch_name}: Processing {total_poems} poems took {end_time} seconds using multiprocessing")

        for piece, row in zip(pieces, list(range(total_poems))):
            df.iloc[row] = [piece[0], piece[1], piece[2]]
        df            = df.dropna()
        df.to_csv(batch_name + ".csv", encoding = "utf-8-sig")

if __name__ == '__main__':
    main()