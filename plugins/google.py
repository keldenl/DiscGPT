from bs4 import BeautifulSoup
import requests
from datetime import datetime

# Create HTTP client with headers that look like a real web browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}

def scrape_search(query: str, page=1, max_results=4):
    """scrape search results for a given keyword"""
    url = f"https://www.google.com/search?hl=en&q={query}" + (
        f"&start={10*(page-1)}" if page > 1 else "")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all divs with class "g"
    divs_with_class_g = soup.find_all(class_="g")

    # Print the number of divs found
    print(f"Found {len(divs_with_class_g)} divs with class 'g':")
    results = []

    # Loop through the search results and extract information
    for result in divs_with_class_g:
        # Extract the title of the search result
        try:
            title = result.find('h3').text
        except:
            title = 'N/A'
        
        # Extract the link of the search result
        link = result.find('a')['href']
        
        # Extract the description of the search result
        try:
            snippet = ' '.join(s.text for s in result.select(".lEBKkf span"))
        except:
            snippet = 'N/A'

        results.append({'title': title, 'link': link, 'snippet': snippet})
    
    return results[:max_results]


def get_prompt(query:str) -> str:
    results = scrape_search(query, max_results=4)
    result_str = '\n\n'.join([f"Title: {d['title']}\nLink: {d['link']}\nSnippet: {d['snippet']}" for d in results])
    return f"""Web search results:
{result_str}

Current date: {datetime.now().strftime('%H:%M:%S %m-%d-%Y')}
Instructions: Using the provided web search results, write a comprehensive reply to the given query. Make sure to cite results using (Source: <URL>) notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.

Query: {query}
Answer:"""