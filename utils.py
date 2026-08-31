from datetime import datetime, timezone, timedelta


class JioMartUtils:

    def extract_item_dimensions(self, item_dimensions):
        if not isinstance(item_dimensions, dict):
            return {}

        dimensions = {}

        for name, data in item_dimensions.items():
            if not isinstance(data, dict):
                continue

            value = data.get("value")
            unit = data.get("unit")

            if value is not None:
                dimensions[name] = {
                    "value": value,
                    "unit": unit,
                }

        return dimensions

    def extract_specifications(self, specifications):
        if not specifications:
            return {}

        extracted_specs = {}

        if isinstance(specifications, list):
            for specification in specifications:
                if not isinstance(specification, dict):
                    continue

                # Check for sub_specs structure
                if "sub_specs" in specification and isinstance(
                    specification.get("sub_specs"), list
                ):
                    sub_specs = specification.get("sub_specs", [])
                    for spec in sub_specs:
                        if isinstance(spec, dict):
                            name = (
                                spec.get("display_string")
                                or spec.get("name")
                                or spec.get("key")
                            )
                            value = spec.get("value")
                            if name and value is not None:
                                if isinstance(value, list):
                                    value = ", ".join(str(v) for v in value)
                                extracted_specs[name] = value
                else:
                    # Flat structure
                    name = (
                        specification.get("display_string")
                        or specification.get("name")
                        or specification.get("key")
                    )
                    value = specification.get("value")
                    if name and value is not None:
                        if isinstance(value, list):
                            value = ", ".join(str(v) for v in value)
                        extracted_specs[name] = value

        return extracted_specs

    def extract_key_features(self, key_features):
        if not key_features:
            return ""

        # If it's a string, return it as is
        if isinstance(key_features, str):
            return key_features

        # If it's a list of strings (like your data)
        if isinstance(key_features, list):
            # Filter out empty strings and join with " | "
            features = [
                str(feature).strip()
                for feature in key_features
                if feature and str(feature).strip()
            ]
            return " | ".join(features) if features else ""

        # If it's any other type, convert to string
        return str(key_features)

    def extract_delivery_minutes(self, delivery_promise):
        if not isinstance(delivery_promise, dict):
            return None

        min_time = delivery_promise.get("min")
        max_time = delivery_promise.get("max")

        if not min_time or not max_time:
            return None

        try:
            min_dt = datetime.fromisoformat(min_time.replace("Z", "+00:00"))
            max_dt = datetime.fromisoformat(max_time.replace("Z", "+00:00"))
            return int((max_dt - min_dt).total_seconds() / 60)

        except (ValueError, TypeError):
            return None

    def _parse_variant(self, item):
        price_info = item.get("price_per_piece", {})
        custom_json = item.get("_custom_json", {})
        attributes = custom_json.get("attributes", {})
        brand = attributes.get("brand", {})
        manufacturer = attributes.get("manufacturer", {})
        variants = attributes.get("variants", {})
        origin_countries = variants.get("origin_countries", [])

        shelf_life_data = variants.get("shelf_life", {})
        shelf_life_window = shelf_life_data.get("window", "")
        shelf_life_unit = shelf_life_data.get("window_unit", "")

        if shelf_life_window:
            shelf_life = str(shelf_life_window) + str(shelf_life_unit)
        else:
            shelf_life = ""

        sold_by = item.get("seller", {}).get("name", "")
        dimensions = variants.get("dimensions", {})
        item_dimensions = dimensions.get("item_dimensions", {})

        item_dimension_data = self.extract_item_dimensions(item_dimensions)
        specifications = attributes.get("specifications", [])
        specification_data = self.extract_specifications(specifications)
        key_features = attributes.get("key_features", [])
        key_features_data = self.extract_key_features(key_features)
        delivery_promise = item.get("delivery_promise", {})
        delivery_minutes = self.extract_delivery_minutes(delivery_promise)

        manufacturing_addresses = manufacturer.get("manufacturing_addresses", [])
        manufacturer_address = None
        if manufacturing_addresses and isinstance(manufacturing_addresses, list):
            first_address = manufacturing_addresses[0]
            if isinstance(first_address, dict):
                manufacturer_address = first_address.get("address")

        return {
            "product_name": item.get("product_name", ""),
            "slug": item.get("slug", ""),
            "size": item.get("size", ""),
            "mrp": price_info.get("marked", ""),
            "selling_price": price_info.get("selling", ""),
            "effective_price": price_info.get("effective", ""),
            "currency_code": price_info.get("currency_code", ""),
            "currency_symbol": price_info.get("currency_symbol", ""),
            "discount": item.get("discount", ""),
            "available": item.get("is_serviceable", False),
            "pincode": item.get("pincode", ""),
            "distance_in_meter": item.get("distance", ""),
            "quantity": item.get("quantity", ""),
            "delivery_promise": delivery_minutes,
            "key_features": key_features_data,
            "brand_name": brand.get("name", ""),
            "sold_by": sold_by,
            "brand_status": brand.get("status", ""),
            "origin_countries": origin_countries,
            "manufacturer_name": manufacturer.get("name", ""),
            "manufacturer_address": manufacturer_address,
            "product_code": attributes.get("product_code", ""),
            "shelf_life": shelf_life,
            "item_dimensions": item_dimension_data,
            "item_specifications": specification_data,
            "product_showcase": attributes.get("snippet", ""),
            "disclaimer": attributes.get("disclaimers", ""),
        }
