import hashlib
import zlib
import json
import os
from datetime import datetime


class ResponseStorage:

    def __init__(self, storage_dir="raw_responses"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        self.date_dir = datetime.now().strftime("%Y-%m-%d")
        self.full_path = os.path.join(self.storage_dir, self.date_dir)
        os.makedirs(self.full_path, exist_ok=True)

    @staticmethod
    def generate_hash(url, pincode):
        combined = f"{url}:{pincode}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def save_response(self, url, pincode, raw_response):
        if raw_response is None:
            return None, None

        try:
            response_hash = self.generate_hash(url, pincode)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{response_hash}_{timestamp}.json.gz"
            filepath = os.path.join(self.full_path, filename)

            if isinstance(raw_response, dict):
                json_str = json.dumps(raw_response, ensure_ascii=False, indent=2)
            else:
                json_str = str(raw_response)

            compressed_data = zlib.compress(json_str.encode("utf-8"), level=9)

            with open(filepath, "wb") as f:
                f.write(compressed_data)

            file_size = os.path.getsize(filepath)
            relative_path = os.path.join(self.date_dir, filename)

            print(f"Raw response saved to: {filepath} (Size: {file_size} bytes)")

            return response_hash, relative_path

        except Exception as e:
            print(f"Error saving raw response: {e}")
            return None
