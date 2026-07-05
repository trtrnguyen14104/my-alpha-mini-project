import argparse
import logging
import sys

from config import Config
import scraper
import file_search_manager
from state_store import StateStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def sync():
    client = file_search_manager.get_client(Config.GOOGLE_API_KEY)
    state = StateStore(Config.STATE_FILE)
    store = file_search_manager.get_or_create_store(
        client, state.get_store_name(), Config.FILE_SEARCH_STORE_DISPLAY_NAME
    )
    state.set_store_name(store.name)

    seen_ids = set()
    added = updated = skipped = 0
    total_files = 0

    for article in scraper.fetch_articles(Config.SOURCE_API_URL, max_articles=Config.MAX_ARTICLES):
        total_files += 1
        seen_ids.add(article['id'])
        filepath = scraper.write_article_to_disk(article, Config.ARTICLES_DIR)

        status = state.classify(article['id'], article['updated_at'])

        if status == "unchanged":
            skipped += 1
            continue

        if status == "updated":
            old = state.get(article['id'])
            if old and old.get("document_name"):
                file_search_manager.delete_document(client, old["document_name"])

        document_name = file_search_manager.upload_article(client, store, article, filepath)
        state.set(article['id'], article['updated_at'], document_name)

        if status == "added":
            added += 1
            logger.info(f"[ADDED] {article['title']}")
        else:
            updated += 1
            logger.info(f"[UPDATED] {article['title']}")

    removed = 0
    for stale_id in state.known_ids() - seen_ids:
        stale = state.get(stale_id)
        if stale and stale.get("document_name"):
            file_search_manager.delete_document(client, stale["document_name"])
        state.remove(stale_id)
        removed += 1
        logger.info(f"[REMOVED] article_id={stale_id} (no longer in source)")

    state.save()

    logger.info(
        "SYNC SUMMARY: "
        f"files_scraped={total_files}, added={added}, updated={updated}, "
        f"skipped={skipped}, removed={removed}, store={store.name}"
    )
    return {
        "files_scraped": total_files,
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "removed": removed,
    }


def sanity_check(question: str):
    import chat

    client = file_search_manager.get_client(Config.GOOGLE_API_KEY)
    state = StateStore(Config.STATE_FILE)
    store_name = state.get_store_name()
    if not store_name:
        raise RuntimeError(
            "No File Search store recorded in state.json yet"
        )
    answer = chat.ask(client, store_name, question, Config.CHAT_MODEL)
    print(f"\nQuestion: {question}\n\nAnswer:\n{answer}\n")


def main():
    parser = argparse.ArgumentParser(description="OptiBot KB sync job")
    parser.add_argument("--ask", type=str, default=None)
    args = parser.parse_args()

    try:
        if args.ask:
            sanity_check(args.ask)
        else:
            sync()
    except Exception:
        logger.exception("Job failed")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
