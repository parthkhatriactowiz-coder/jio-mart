import re
import json
import logging
import requests
from datetime import datetime, timezone
from utils import JioMartUtils

logger = logging.getLogger(__name__)


class JioMartParser:

    def __init__(self):
        self.session = requests.Session()
        self.utils = JioMartUtils()

        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9",
                "authorization": "Bearer Njg1OTQ1ZjQ2YzhjN2FlZTNmM2FmNjA1OlRwS3c3d0Q5aA==",
                "cache-control": "no-cache",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "x-currency-code": "INR",
                "x-fp-sdk-version": "1.10.3-70tmp-1.beta.3",
            }
        )

        self.session.cookies.update(
            {
                "AKA_A2": "A",
                "anonymous_id": "2b656abdf8d649e8bee688bf79512c95",
                "old_browser_anonymous_id": "2b656abdf8d649e8bee688bf79512c95",
                "anonymous_sig": "dd21fa627ec701fb5d6e63c072af63dc5219e0ea84a1e2ca104958b38016d6b4",
                "WZRK_G": "fcee09d53065492999e9c2e3cc31ebef",
                "_gcl_au": "1.1.1546190768.1788162844",
                "_ga": "GA1.1.1057382056.1788162844",
            }
        )

    def _update_date(self):
        self.session.headers["x-fp-date"] = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )

    def get_pincode_details(self, pincode):
        self._update_date()
        url = f"https://www.jiomart.com/api/service/application/logistics/v1.0/pincode/{pincode}"

        try:
            res = self.session.get(url, timeout=30)
            data = res.json()
            if not data.get("success") or not data.get("data"):
                return None

            loc = data["data"][0]
            parents = {p.get("sub_type"): p.get("name") for p in loc.get("parents", [])}
            coords = loc.get("lat_long", {}).get("coordinates", [])

            return {
                "pincode": pincode,
                "city": parents.get("city"),
                "state": parents.get("state"),
                "country": parents.get("country"),
                "latitude": coords[1] if len(coords) > 1 else None,
                "longitude": coords[0] if len(coords) > 0 else None,
                "zone": loc.get("meta_code", {}).get("zone"),
                "iso": loc.get("meta_code", {}).get("iso2"),
            }
        except Exception as e:
            logger.error(f"Error fetching pincode {pincode}: {e}")
            return None

    def get_product_details(self, url, pincode):
        self._update_date()

        match = re.search(r"/product/([^/?]+)", url)
        if not match:
            logger.warning(f"Slug not found in URL: {url}")
            return None

        slug = match.group(1)
        loc = self.get_pincode_details(pincode)
        if not loc:
            logger.warning(f"Location not found for pincode: {pincode}")
            return None

        price_url = "https://www.jiomart.com/api/service/application/catalog/v1.0/products/sizes/price"
        payload = {"items": [{"slug": slug, "size": "OS", "is_tradein_opted": False}]}

        self.session.headers.update(
            {
                "content-type": "application/json",
                "x-geolocation": json.dumps(
                    {
                        "latitude": str(loc.get("latitude", "")),
                        "longitude": str(loc.get("longitude", "")),
                    }
                ),
                "x-location-detail": json.dumps(
                    {
                        "country": loc.get("country", "INDIA"),
                        "country_iso_code": loc.get("iso", "IN"),
                        "city": loc.get("city", ""),
                        "pincode": str(loc.get("pincode", "")),
                        "state": loc.get("state", ""),
                    }
                ),
            }
        )

        try:
            res = self.session.post(price_url, json=payload, timeout=30)
            if res.status_code != 200:
                logger.error(f"Price API error for {slug}: status {res.status_code}")
                return None

            data = res.json()
            items = data.get("items", [])
            if not items:
                return {
                    "slug": slug,
                    "variants": [],
                    "total_variants": 0,
                    "has_error": True,
                    "error_message": "No items found",
                    "raw_response": data,
                }

            has_error = any("error" in item for item in items)
            error_message = next(
                (item.get("error") for item in items if "error" in item), None
            )
            variants = [
                self.utils._parse_variant(item) for item in items if "error" not in item
            ]

            return {
                "slug": slug,
                "variants": variants,
                "total_variants": len(variants),
                "has_error": has_error,
                "error_message": error_message,
                "raw_response": data,
            }
        except Exception as e:
            logger.error(f"Error fetching product price for {slug}: {e}")
            return None
