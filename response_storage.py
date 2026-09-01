import os
import json
import zlib
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseStorage:

    def __init__(self, storage_dir="raw_responses"):
        self.storage_dir = storage_dir
        self.date_dir = datetime.now().strftime("%Y-%m-%d")
        self.full_path = os.path.join(self.storage_dir, self.date_dir)
        os.makedirs(self.full_path, exist_ok=True)

    @staticmethod
    def generate_hash(url, pincode):
        return hashlib.sha256(f"{url}:{pincode}".encode()).hexdigest()

    def save_response(self, url, pincode, raw_response):
        if not raw_response:
            return None, None

        try:
            res_hash = self.generate_hash(url, pincode)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{res_hash}_{timestamp}.json.gz"
            filepath = os.path.join(self.full_path, filename)

            content = (
                json.dumps(raw_response)
                if isinstance(raw_response, dict)
                else str(raw_response)
            )
            compressed = zlib.compress(content.encode("utf-8"), level=9)

            with open(filepath, "wb") as f:
                f.write(compressed)

            return res_hash, os.path.join(self.date_dir, filename)

        except Exception as e:
            logger.error(f"Error saving raw response for {url}: {e}")
            return None, None
