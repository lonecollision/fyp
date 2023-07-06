import time

import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

links_per_page = 20
batch_size = 1
total_pages = 718

def urlPreprocess(path):
    urls  = np.loadtxt(path, dtype = "str")
    index = np.argwhere(np.core.defchararray.find(urls, "-audio-only") != -1)
    urls  = np.delete(urls, index)
    np.savetxt("poet_poem_urls_without_audio.txt", urls, fmt = "%s")
    
def urlExtract():
    urls           = np.array(["*" * 192] * (total_pages * links_per_page))
    driver         = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
    page           = "https://poets.org/poems"
    driver.get(page)
    #driver.implicitly_wait(45)
    time.sleep(5)
    
    for i in range(1, total_pages + 1):
        try:
            count = 0
            poem_count = 0
            time.sleep(10)
            poems = driver.find_element(by = By.TAG_NAME, value = "table")
            tbody = poems.find_element(by  = By.TAG_NAME, value = "tbody")
            tr    = tbody.find_elements(by = By.TAG_NAME, value = "tr")
            for row in tr:
                td   = row.find_element(by = By.TAG_NAME, value = "td")
                a    = td.find_element(by = By.TAG_NAME, value = "a")
                link = a.get_attribute("href")
                urls[(i - 1)*links_per_page + count] = link
                count += 1
                poem_count += 1
            print(str(poem_count) + " poems on page " + str(i))
            next_link = driver.find_element(By.CSS_SELECTOR, "a[title=\"Go to next page\"]")
            driver.execute_script("arguments[0].click();", next_link)
        except Exception as e:
            print(e)
    np.savetxt("poet_poem_urls.txt", urls, fmt = "%s")

def main():
    urlExtract()
    urlPreprocess("poet_poem_urls.txt")

if __name__ == '__main__':
    main()