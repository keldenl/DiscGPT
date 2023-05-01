import requests


def get_prompt(query: str, user: str) -> str:
    url = f"https://www.reddit.com/r/{query}.json"
    response = requests.get(url, headers={'User-agent': 'gpt-llama.cpp'})

    if response.status_code == 200:
        json_data = response.json()
        idx = 0
        posts = json_data['data']['children']

        # Filter out stickied posts
        for p in posts:
            if p['data']['stickied']:
                idx += 1
            else :
                break

        top_post = posts[idx]['data']
        title = top_post['title']
        url = top_post['permalink']
        self_text = top_post['selftext']

        # If there's no text content, it must have a link?
        if len(self_text) == 0:
            self_text = top_post['url']

        prompt = f"""Title: {title}
Subreddit: {query}
Link: https://www.reddit.com{url}

Content:
{self_text[:2000]}

-----
Provide the link to the post and summarize the post for the user @{user}. If the content is also a link, provide that after the summary:

Post Link: """
        return prompt
    else:
        print(response)
        print("Error loading data from URL.")
        return ''