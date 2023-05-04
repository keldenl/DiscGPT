from bs4 import BeautifulSoup
import requests
# from datetime import datetime


# archive_base = 'https://web.archive.org/web/https://twitter.com/elonmusk/status/1653262203343052806'
# url = 'https://twitter.com/explore'


# def read_tweet(url: str) -> str:
#     # url = 'https://twitter.com/toteskosh/status/1491809570997555201'
#     website = requests.get(archive_base + url, headers=headers, allow_redirects=False)
#     r = website.text

#     soup = BeautifulSoup(r, "lxml")
#     print(soup)
#     tweet_text = soup.find(
#         "p", {"class": "TweetTextSize TweetTextSize--jumbo js-tweet-text tweet-text"})
#     print(tweet_text)
#     dest = soup.find('a', {"class": "twitter-timeline-link u-hidden"})
#     dest.decompose()
#     content = tweet_text.text
#     print(content)
#     return content

import re

INVISIBLE_ELEMS = ('style', 'script', 'head', 'title')
RE_SPACES = re.compile(r'\s{3,}')


def get_visible_text(soup):
    """ get visible text from a document """
    text = ' '.join([
        s for s in soup.strings
        if s.parent.name not in INVISIBLE_ELEMS
    ])
    # collapse multiple spaces to two spaces.
    return RE_SPACES.sub('  ', text)


def scrape_site(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    website = requests.get(url, headers=headers)
    soup = BeautifulSoup(website.text, 'lxml')
    web_text = ' '.join(p.text for p in soup.find_all(['h1', 'h2', 'h3', 'p', 'span']))
    return web_text[:4000] # strip ALL whitespace and get only first 2000 characters


def get_prompt(url:str, query:str) -> str:
    prompt = "Website Content:\n"
    prompt += scrape_site(url)
    prompt += (
        "\n\nInstructions:\nCompose a comprehensive reply to the query using the website content given. "
        "Only include information found in the website content and don't add any additional information. "
        "Make sure the answer is correct and don't output false content. "
        "If the text does not relate to the query, simply state 'Text Not Found in website'. Ignore outlier "
        "website content which has nothing to do with the question. Only answer what is asked. The "
        f"answer should be short and concise. Answer step-by-step. \n\nQuery: {query}\nAnswer: "
    )
    return prompt


# print(scrape_site('https://www.geeksforgeeks.org/beautifulsoup-search-by-text-inside-a-tag/#'))
# read_tweet('https://twitter.com/elonmusk/status/1653262203343052806')


# get_prompt('what is gpt-llama.cpp?')
#
# print(results)

# Generic
# soup = BeautifulSoup(website.content, 'html.parser')
# # print(soup.prettify())
# tags = soup.find_all(['p', 'h2', 'title'])
# # tags = soup.find_all(['span'])
# for soups in tags:
#     if soups.string is not None:
#         print(soups.tag)
#         print(soups.string)


#     # print(soups)
