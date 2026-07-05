import json
import logging
import os
from typing import Optional

logger = logging.getLogger("state_store")

_STORE_NAME_KEY = "__file_search_store_name__"


class StateStore:
    def __init__(self, path: str):
        self.path = path
        self._state: dict = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self._state = json.load(f)
            logger.info(f"Loaded state for {len(self._state)} articles from {self.path}")
        else:
            self._state = {}
            logger.info(f"No existing state file at {self.path}; starting fresh")

    def save(self):
        tmp_path = f"{self.path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.path)

    def get(self, article_id: str) -> Optional[dict]:
        return self._state.get(article_id)

    def set(self, article_id: str, updated_at: str, document_name: str):
        self._state[article_id] = {
            "updated_at": updated_at,
            "document_name": document_name,
        }

    def remove(self, article_id: str):
        self._state.pop(article_id, None)

    def known_ids(self):
        return {k for k in self._state.keys() if not k.startswith("__")}

    def get_store_name(self) -> Optional[str]:
        return self._state.get(_STORE_NAME_KEY)

    def set_store_name(self, name: str):
        self._state[_STORE_NAME_KEY] = name

    def classify(self, article_id: str, updated_at: str) -> str:
        existing = self.get(article_id)
        if existing is None:
            return "added"
        if existing.get("updated_at") != updated_at:
            return "updated"
        return "unchanged"
