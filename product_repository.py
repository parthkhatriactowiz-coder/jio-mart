import json
from database import INSERT_PRODUCT, UPDATE_INPUT_STATUS, CREATE_PRODUCT_TABLE
from response_storage import ResponseStorage


class JioMartProductSave:

    def __init__(self, conn, storage_dir="raw_responses"):
        self.conn = conn
        self.cursor = conn.cursor()
        self.storage = ResponseStorage(storage_dir)

    def ensure_table(self):
        self.cursor.execute(CREATE_PRODUCT_TABLE)
        self.conn.commit()

    def _to_json_str(self, val):
        if val is None:
            return None
        return (
            json.dumps(val, ensure_ascii=False)
            if isinstance(val, (dict, list))
            else str(val)
        )

    def save(self, input_id, url, pincode, price_data):
        if not price_data or price_data.get("has_error") or not price_data.get("variants"):
            self.cursor.execute(UPDATE_INPUT_STATUS, ("failed", input_id))
            self.conn.commit()
            return

        raw_res = price_data.get("raw_response")
        res_hash, rel_file = self.storage.save_response(url, pincode, raw_res)

        variants = price_data.get("variants", [])
        slug = price_data.get("slug", "")
        rows = []

        for v in variants:
            row = (
                input_id,
                slug,
                v.get("product_name"),
                v.get("size"),
                v.get("mrp") or None,
                v.get("selling_price") or None,
                v.get("effective_price") or None,
                v.get("currency_code"),
                v.get("currency_symbol"),
                v.get("discount"),
                bool(v.get("available")),
                v.get("pincode"),
                v.get("distance_in_meter") or None,
                v.get("quantity"),
                v.get("delivery_promise"),
                v.get("key_features"),
                v.get("brand_name"),
                v.get("sold_by"),
                self._to_json_str(v.get("origin_countries")),
                v.get("manufacturer_name"),
                v.get("manufacturer_address"),
                v.get("product_code"),
                v.get("shelf_life"),
                self._to_json_str(v.get("item_dimensions")),
                self._to_json_str(v.get("item_specifications")),
                v.get("product_showcase"),
                v.get("disclaimer"),
                res_hash,
                rel_file,
            )
            rows.append(row)

        self.cursor.executemany(INSERT_PRODUCT, rows)
        self.cursor.execute(UPDATE_INPUT_STATUS, ("success", input_id))
        self.conn.commit()

    def close(self):
        self.cursor.close()
