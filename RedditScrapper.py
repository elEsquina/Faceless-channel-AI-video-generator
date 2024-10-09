from bs4 import BeautifulSoup
import requests
import re
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt_tab')
import json 

#IMPLEMENT THE ABILITY TO REMEMBER WHICH SUBREDDITS HAVE BEEN SCRAPED
class Scrapper:
    def __init__(self, subreddits: list) -> None:
        self.all_posts = []

        for subreddit in subreddits:
            print(f"Scraping {subreddit}...")
            posts = self.scrape_subreddit(subreddit)
            # Sanitize the posts before extending
            sanitized_posts = self.sanitize_posts(posts)
            
            self.all_posts.extend(sanitized_posts)
            print(f"Found {len(sanitized_posts)} sanitized posts from {subreddit}\n")

        print(f"Total sanitized posts: {len(self.all_posts)}")

         

    def scrape_subreddit(self, subreddit) -> list:
        url = f"https://www.reddit.com/r/{subreddit}/?feedViewType=compactView"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        posts = []
        for post_div in soup.find_all('a', {'slot': 'text-body'}):
            post = post_div.text.strip()
            posts.append(post)

        return posts


    def sanitize_posts(self, posts) -> list:
        sanitized_posts = []

        for post in posts:
            words = post.lower().replace("aita", "am i the asshole?").split()
            sanitized_words = [word for word in words if re.search(r'[a-zA-Z0-9]', word)]
            sanitized_posts.append(' '.join(sanitized_words))

        return sanitized_posts
    

    def tokenize_post(self, post) -> list:
        return sent_tokenize(post)
    

    def save(self) -> None: 
        dataobject = {
            idx: {
                "post": post,
                "audio": None,
                "tokens": self.tokenize_post(post)
            }
            for idx, post in enumerate(self.all_posts)
        }
        with open("data.json", "w+") as file: 
            json.dump(dataobject, file)

        print(f"Saved {len(self.all_posts)} posts into data.json")




subreddits = [
    "nosleep",
    "tifu",
    "relationship_advice",
    "AmItheAsshole",
    "confession",
    "AskReddit",
    "legaladvice",
    "LetsNotMeet",
    "MaliciousCompliance",
    "ProRevenge",
    "offmychest",
    "unresolvedmysteries",
    "IDontWorkHereLady",
    "TrueCrime",
    "justnomil"
]

scrap = Scrapper(subreddits=subreddits)
scrap.save()