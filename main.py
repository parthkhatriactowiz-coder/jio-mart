from parsor import JioMartParser
import time
from database import get_db_connection, GET_PENDING_INPUTS


def print_variant(variant, index):
    """Print a single variant with all its details"""

    print(f"\n{'=' * 60}")
    print(f"VARIANT {index}")
    print(f"{'=' * 60}")

    for key, value in variant.items():
        print(f"{key}: {value}")

    print(f"{'=' * 60}")


def print_product(price_data):
    """Print all product variants"""
    if price_data is None:
        print("No product data available")
        return

    print("\n" + "=" * 50)
    print("PRODUCT DETAILS")
    print("=" * 50)

    print(f"Slug: {price_data.get('slug', 'N/A')}")
    print(f"Total Variants: {price_data.get('total_variants', 0)}")

    # Print each variant with all its details
    variants = price_data.get("variants", [])
    if variants:
        for idx, variant in enumerate(variants, 1):
            print_variant(variant, idx)
    else:
        print("No variants found")

    print("=" * 50)


def main():
    parser = JioMartParser()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(GET_PENDING_INPUTS)
        rows = cursor.fetchall()

        for row in rows[:10]:
            pincode = row.get("pincode")
            input_id = row.get("id")
            url = row.get("url")

            print(f"\nProcessing ID: {input_id}, Pincode: {pincode}")
            print(f"URL: {url}")

            location = parser.get_pincode_details(str(pincode))

            price = parser.get_product_price(url, str(pincode))
            print_product(price)

            time.sleep(0.5)

        conn.close()

    except Exception as e:
        print(f"Database not found or error: {e}")


if __name__ == "__main__":
    main()
