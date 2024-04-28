#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from flask import Flask

app = Flask(__name__)


@app.route("/search/<query>")
def search(query: str):
    req = requests.get(
        "https://annas-archive.org/search",
        params={"q": query, "sort": "newest_added"},
        timeout=5,
    )
    soup = BeautifulSoup(req.text, features="lxml")

    feed = FeedGenerator()
    feed.title(f"Anna's Archive Search: {query}")
    feed.link(href=req.url, rel="self")
    feed.description(f"Search results for: {query}")

    for entry in soup.find_all(
        "div",
        attrs={
            "class": [
                "h-[125] flex flex-col justify-center",
                "h-[125] flex flex-col justify-center js-scroll-hidden",
            ],
        },
    )[::-1]:
        # Hide partial matches
        if "overflow-hidden" in entry.find_parent("div").attrs["class"]:
            continue

        contents = entry.encode_contents().decode().strip()

        # Uncomment hidden entries
        if contents.startswith("<!--") and contents.endswith("-->"):
            entry = BeautifulSoup(contents[4:-3], features="lxml")

        md5 = entry.find("a").attrs["href"].split("/")[-1]

        feed_entry = feed.add_entry()
        feed_entry.id(str(hash(query + md5)))
        feed_entry.title(f"{entry.find('h3').text} ({md5})")
        feed_entry.link(href=f"https://annas-archive.org/md5/{md5}")

    return feed.rss_str(pretty=True)


if __name__ == "__main__":
    app.run()
