from datetime import datetime


class JioMartUtils:

    def extract_item_dimensions(self, item_dimensions):
        if not isinstance(item_dimensions, dict):
            return {}
        dims = {}
        for name, data in item_dimensions.items():
            if isinstance(data, dict) and data.get("value") is not None:
                dims[name] = {"value": data.get("value"), "unit": data.get("unit")}
        return dims

    def extract_specifications(self, specifications):
        if not isinstance(specifications, list):
            return {}
        specs = {}
        for spec in specifications:
            if not isinstance(spec, dict):
                continue
            sub_list = (
                spec.get("sub_specs")
                if isinstance(spec.get("sub_specs"), list)
                else [spec]
            )
            for item in sub_list:
                if isinstance(item, dict):
                    name = (
                        item.get("display_string")
                        or item.get("name")
                        or item.get("key")
                    )
                    val = item.get("value")
                    if name and val is not None:
                        specs[name] = (
                            ", ".join(str(v) for v in val)
                            if isinstance(val, list)
                            else val
                        )
        return specs

    def extract_key_features(self, key_features):
        if isinstance(key_features, list):
            return " | ".join(
                str(f).strip() for f in key_features if f and str(f).strip()
            )
        return str(key_features or "")

    def extract_delivery_minutes(self, delivery_promise):
        if not isinstance(delivery_promise, dict):
            return None
        try:
            min_dt = datetime.fromisoformat(
                delivery_promise["min"].replace("Z", "+00:00")
            )
            max_dt = datetime.fromisoformat(
                delivery_promise["max"].replace("Z", "+00:00")
            )
            return int((max_dt - min_dt).total_seconds() / 60)
        except Exception:
            return None

    def _parse_variant(self, item):
        price = item.get("price_per_piece") or {}
        attrs = (item.get("_custom_json") or {}).get("attributes") or {}
        variants = attrs.get("variants") or {}
        shelf_life = variants.get("shelf_life") or {}
        mfg = attrs.get("manufacturer") or {}
        mfg_addrs = mfg.get("manufacturing_addresses") or []

        mfg_addr = (
            mfg_addrs[0].get("address")
            if mfg_addrs and isinstance(mfg_addrs[0], dict)
            else None
        )
        item_dims = (variants.get("dimensions") or {}).get("item_dimensions") or {}

        return {
            "product_name": item.get("product_name", ""),
            "slug": item.get("slug", ""),
            "size": item.get("size", ""),
            "mrp": price.get("marked", ""),
            "selling_price": price.get("selling", ""),
            "effective_price": price.get("effective", ""),
            "currency_code": price.get("currency_code", ""),
            "currency_symbol": price.get("currency_symbol", ""),
            "discount": item.get("discount", ""),
            "available": item.get("is_serviceable", False),
            "pincode": item.get("pincode", ""),
            "distance_in_meter": item.get("distance", ""),
            "quantity": item.get("quantity", ""),
            "delivery_promise": self.extract_delivery_minutes(
                item.get("delivery_promise")
            ),
            "key_features": self.extract_key_features(attrs.get("key_features")),
            "brand_name": (attrs.get("brand") or {}).get("name", ""),
            "sold_by": (item.get("seller") or {}).get("name", ""),
            "origin_countries": variants.get("origin_countries", []),
            "manufacturer_name": mfg.get("name", ""),
            "manufacturer_address": mfg_addr,
            "product_code": attrs.get("product_code", ""),
            "shelf_life": f"{shelf_life.get('window', '')} {shelf_life.get('window_unit', '')}",
            "item_dimensions": self.extract_item_dimensions(item_dims),
            "item_specifications": self.extract_specifications(
                attrs.get("specifications")
            ),
            "product_showcase": attrs.get("snippet", ""),
            "disclaimer": attrs.get("disclaimers", ""),
        }
