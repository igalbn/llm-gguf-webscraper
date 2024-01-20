# %%
# Scraper of tabular data. About LLM models in GGUF format on site Hagging Face.
# https://github.com/igalbn/llm-gguf-webscraper

import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

NUMBER_ZERO = 0
NUMBER_ONE = 1
BLANK_STRING = ''

wait_time = 11.05
test_mode = True  # read only few pages

# %%
# blank DataFrame to store the scraped data
columns_names = ['name', 'downloads', 'likes', 'updated', 'type', 'link']
df = pd.DataFrame(columns=columns_names)


def make_item(item):  # receive data about one model
    global df
    name = item.find('h4')
    if (name is not None):
        name = name.text.strip()

    downloads = item.find(
        'svg', {
            'class': 'flex-none w-3 text-gray-400 mr-0.5'})
    if (downloads):
        downloads = downloads.find_next_sibling(text=True).strip()

    likes = item.find('svg', {'class': 'flex-none w-3 text-gray-400 mr-1'})
    if (likes):
        likes = likes.find_next_sibling(text=True).strip()

    updated = item.find('time')
    if (updated):
        updated = updated.text.strip()

    type = None
    type = item.find('span').previous_sibling.strip()

    link = item.find('a')['href']

    row = [name, downloads, likes, updated, type, link]
    df.loc[len(df)] = row


# %%
def make_page(page_items):  # data from one page of models
    page_items_num = len(page_items)
    for i in range(page_items_num):
        current_item = page_items[i]
        make_item(current_item)

# %%


def read_page(index):
    page_link = f'https://huggingface.co/models?library=gguf&p={index}&sort=created'
    print(page_link)
    page = requests.get(page_link)
    page_soup = BeautifulSoup(page.content, "html.parser")

    return page_soup


def make_all_pages():   # all pages of GGUF models. sort by "Recently created"
    global items_section, items
    pass

    pages_num = 2  # in test mode read two pages
    if (not test_mode):
        pages_num = int(read_page(NUMBER_ZERO).find('ul',
                                                    {'class': 'flex select-none items-center justify-between space-x-2 text-gray-700 sm:justify-center mt-10 mx-auto'})
                        .find_all('li')[-2].text.strip())

    for i in range(pages_num):
        print(i)
        soup = read_page(i)

        items_section = soup.find(
            'div', {'class': 'grid grid-cols-1 gap-5 2xl:grid-cols-2'})
        items = items_section.find_all(
            'article', {'class': 'overview-card-wrapper group/repo'})

        make_page(items)

        time.sleep(wait_time)


make_all_pages()

# %%
# df.head(2)

# %%
# remove dublicates
new_df = df.drop_duplicates(subset='name', keep=False)

# Print the new dataframe
# new_df

# %%
result_file_name = f'gguf_models{"_test" if test_mode else BLANK_STRING}.csv'
new_df.to_csv(result_file_name, index=False)
