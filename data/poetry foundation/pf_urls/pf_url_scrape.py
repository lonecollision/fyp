from multiprocessing import Pool
import re
import time

from bs4 import BeautifulSoup
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

links_per_page = 20
batch_size = 200

def urlExtract(batch_number):
    page_start = batch_number * batch_size + 1
    # If there are 200 pages per batch, each batch has batch_size * links_per_page poems
    urls           = np.array(["*" * 192] * (batch_size * links_per_page))
    driver         = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
    for i in range(0, batch_size):
        print("Page " + str(i + page_start))
        page          = "https://www.poetryfoundation.org/poems/browse#page=" + str(i + page_start) + "&sort_by=recently_added"
        driver.get(page)
        driver.implicitly_wait(45)
        time.sleep(10)
        html_source   = driver.page_source
        doc           = BeautifulSoup(html_source, "html.parser")
        links         = doc.find_all("a", href = re.compile(".*/poems/[0-9]+/.*"))
        count         = 0
        for link in links:
            url       = link.get("href")
            urls[(i)*links_per_page + count]  = url
            if count  == links_per_page - 1:
                break
            else:
                count += 1
    np.savetxt("poem_urls" + str(page_start) + "-" + str(page_start + batch_size - 1) + ".txt", urls, fmt = "%s")

def main():
    p = Pool(processes = 1)
    batch_iterable = list(range(0, 11))
    p.map(urlExtract, batch_iterable)
    p.terminate()

if __name__ == '__main__':
    main()