import requests


def get_prompt(query: str, user: str) -> str:
    url = f"https://www.reddit.com/r/{query}.json"
    response = requests.get(url, headers={'User-agent': 'gpt-llama.cpp'})

    if response.status_code == 200:
        json_data = response.json()
        top_post = json_data['data']['children'][1]['data']
        title = top_post['title']
        self_text = top_post['selftext']
        url = top_post['url']
        prompt = f"""Title: {title}
Subreddit: {query}
Link: {url}

Content:
{self_text[:2000]}

-----

Summarize this for a second-grade student @{user}. Provide the link to the post upfront:
Link:"""
        return prompt
    else:
        print(response)
        print("Error loading data from URL.")
        return ''