import logging
import os
import re
import time
import requests
from markdownify import markdownify as md

logger = logging.getLogger("scraper")

USER_AGENT = "Mozilla/5.0 (compatible; OptiBotKBSync/1.0)"

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "untitled"


def fetch_articles(base_url: str, max_articles: int = 0):
    headers = {"User-Agent": USER_AGENT}
    next_url = base_url
    total = 0

    while next_url:
        logger.info(f"Fetching {next_url}")
        response = requests.get(next_url, headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Request failed with status {response.status_code}: {next_url}")
            break

        data = response.json()
        articles = data.get("articles", [])

        for article in articles:
            title = article.get("title", "Untitled")
            article_id = str(article.get("id", ""))
            url = article.get("html_url", "")
            updated_at = article.get("updated_at", "")
            raw_html = article.get("body") or ""

            slug = slugify(title) if slugify(title) != "untitled" else article_id
            markdown_body = md(raw_html, heading_style="ATX").strip()

            file_content = (
                f"---\n"
                f'title: "{title}"\n'
                f"id: {article_id}\n"
                f"url: {url}\n"
                f"updated_at: {updated_at}\n"
                f"---\n\n"
                f"# {title}\n\n"
                f"Article URL: {url}\n\n"
                f"{markdown_body}\n"
            )

            yield {
                "id": article_id,
                "title": title,
                "slug": slug,
                "url": url,
                "updated_at": updated_at,
                "markdown": file_content,
            }

            total += 1
            if max_articles and total >= max_articles:
                logger.info(f"Reached MAX_ARTICLES cap ({max_articles}); stopping.")
                return

        next_url = data.get("next_page")
        if next_url:
            time.sleep(0.3)


def write_article_to_disk(article: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{article['slug']}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article['markdown'])
    return filepath
