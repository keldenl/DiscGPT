import requests
def get_prompt(query: str) -> str:
    url = f"https://www.reddit.com/r/{query}.json"
    response = requests.get(url, headers = {'User-agent': 'gpt-llama.cpp'})

    if response.status_code == 200:
        json_data = response.json()
        top_post = json_data['data']['children'][1]['data']
        title = top_post['title']
        self_text = top_post['selftext']
        url = top_post['url']
        prompt = f"""Given information on a recent top Reddit post from r/{query}, write as if you're talking to your friend and provide a friendly explanation what your friend missed and cite your sources in the end in the following format:
# Explanation
<explanation to catch your friend up about the post>
(Source: <link>)

Here's the reddit post's information
# Reddit Post Information
Title
{title}

Link
{url}

Content
{self_text}

# Summary"""
        return prompt
    else:
        print(response)
        print("Error loading data from URL.")
        return ''
