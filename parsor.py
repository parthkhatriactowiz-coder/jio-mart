import requests
import json
import re
from datetime import datetime, timezone
from utils import JioMartUtils


class JioMartParser:

    def __init__(self):
        self.session = requests.Session()
        self.utils = JioMartUtils()

        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": "Bearer Njg1OTQ1ZjQ2YzhjN2FlZTNmM2FmNjA1OlRwS3c3d0Q5aA==",
            "cache-control": "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "x-currency-code": "INR",
            "x-fp-sdk-version": "1.10.3-70tmp-1.beta.3",
        }

        self.cookies = {
            "AKA_A2": "A",
            "anonymous_id": "2b656abdf8d649e8bee688bf79512c95",
            "old_browser_anonymous_id": "2b656abdf8d649e8bee688bf79512c95",
            "anonymous_sig": "dd21fa627ec701fb5d6e63c072af63dc5219e0ea84a1e2ca104958b38016d6b4",
            "WZRK_G": "fcee09d53065492999e9c2e3cc31ebef",
            "_gcl_au": "1.1.1546190768.1788162844",
            "_ga": "GA1.1.1057382056.1788162844",
        }

        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)

    def _update_date(self):
        current_date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.session.headers.update({"x-fp-date": current_date})

    def get_pincode_details(self, pincode):
        self._update_date()

        url = f"https://www.jiomart.com/api/service/application/logistics/v1.0/pincode/{pincode}"

        try:
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"Failed for pincode: {pincode}")
                return None

            data = response.json()

            if not data.get("success"):
                print(f"API error for pincode: {pincode}")
                return None

            if not data.get("data") or len(data["data"]) == 0:
                print(f"No data found for pincode: {pincode}")
                return None

            location = data["data"][0]

            city = state = country = None
            if location.get("parents"):
                for parent in location.get("parents", []):
                    if parent.get("sub_type") == "city":
                        city = parent.get("name")
                    elif parent.get("sub_type") == "state":
                        state = parent.get("name")
                    elif parent.get("sub_type") == "country":
                        country = parent.get("name")

            coords = location.get("lat_long", {}).get("coordinates", [])
            longitude = coords[0] if len(coords) > 0 else None
            latitude = coords[1] if len(coords) > 1 else None

            zone = location.get("meta_code", {}).get("zone")

            return {
                "pincode": pincode,
                "city": city,
                "state": state,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "zone": zone,
            }

        except Exception as e:
            print(f"Error getting pincode details: {e}")
            return None

    def get_product_price(self, url, pincode):
        self._update_date()

        match = re.search(r"/product/([^/?]+)", url)
        if not match:
            print(f"Could not extract slug from URL: {url}")
            return None

        slug = match.group(1)

        location = self.get_pincode_details(pincode)
        if not location:
            print(f"Could not get location for pincode: {pincode}")
            return None

        price_url = "https://www.jiomart.com/api/service/application/catalog/v1.0/products/sizes/price"

        payload = {"items": [{"slug": slug, "size": "OS", "is_tradein_opted": False}]}

        geo = {
            "latitude": str(location.get("latitude", "")),
            "longitude": str(location.get("longitude", "")),
        }
        self.session.headers["x-geolocation"] = json.dumps(geo)

        loc_detail = {
            "country": location.get("country", "INDIA"),
            "country_iso_code": "IN",
            "city": location.get("city", ""),
            "pincode": str(location.get("pincode", "")),
            "state": location.get("state", ""),
        }
        self.session.headers["x-location-detail"] = json.dumps(loc_detail)

        self.session.headers["content-type"] = "application/json"

        try:
            response = self.session.post(price_url, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"Price API failed for: {slug}")
                return None

            data = response.json()

            items = data.get("items", [])
            if not items:
                print(f"No items found for slug: {slug}")
                return None

            variants = []
            for item in items:
                variant_data = self.utils._parse_variant(item)
                variants.append(variant_data)

            return {
                "slug": slug,
                "variants": variants,
                "total_variants": len(variants),
            }

        except Exception as e:
            print(f"Error getting price: {e}")
            return None
