from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os.path
import glob
from time import sleep

# This script scrapes law.com's dictionary for words and their synonyms

dict = {}
current_index = 0
max_index = 3000
current_retry = 0
max_retries = 20

def extract_word():
    try:
        return browser.find_element(By.CLASS_NAME, 'definedword').text
    except NoSuchElementException:
        return None

def extract_synonyms():
    try:
        elem = browser.find_elements(By.XPATH, '//span[@class="text seeAlso"]/a')
        res = []
        for tag in elem:
            res.append(tag.text)
        return res
    except NoSuchElementException:
        return None

def scrape(i):
    try:
        url = f"{base_url}{i}"
        print(f"Searching {url}")
        browser.get(url)

        if "Legal" not in browser.title:
            print(f"Sleeping {browser.title}")
            sleep(5) # Let it load
        
        # sleep(1) # Prevent rate-limiting

        word = extract_word()
        synonyms = extract_synonyms()
        if word:
            print(f"Found word: {word}, synonyms: {synonyms}")
            dict[word] = synonyms
    except Exception as e:
        raise e

def write_thesaurus():
    for i in range(1, 100):
        filename = f"thesaurus {i}.txt"
        if os.path.isfile(filename):
            print(f"{filename} already exists")
            continue
        with open(f"thesaurus {i}.txt", "w") as f:
            print(f"Writing {filename}")
            f.write(str(dict))
            break

if __name__ == '__main__':
    while current_retry < max_retries and current_index < max_index:
        try:
            options = FirefoxOptions()
            options.add_argument('--headless')
            browser = webdriver.Firefox(options=options)
            base_url = "https://dictionary.law.com/Default.aspx?selected="

            scrape(current_index)
            current_index += 1
        except (KeyboardInterrupt, Exception) as e:
            print(f"Exception occurred at index {current_index}. {e}")
            current_retry += 1
            if (current_retry < max_retries):
                print(f"Retrying {current_retry}...")
        finally:
            browser.quit()

    write_thesaurus()

    ## Merge the temp files
    # paths = glob.glob(os.path.join(os.getcwd(), "thesaurus *.txt"), recursive=True)

    # final_dict = {}
    # for path in paths:
    #     with open(path, "r") as f:
    #         dict = eval(f.read())
    #     final_dict.update(dict)

    # with open("thesaurus.txt", "w") as final:
    #     final.write(str(final_dict))