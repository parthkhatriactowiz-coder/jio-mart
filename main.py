from parsor import JioMartParser
from product_repository import JioMartProductSave
from database import get_db_connection, GET_PENDING_INPUTS
import time


def print_variant(variant, index):

    print(f"\n{'=' * 60}")
    print(f"VARIANT {index}")
    print(f"{'=' * 60}")

    for key, value in variant.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"{key}: {value[:100]}...")
        else:
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
    print(f"Has Error: {price_data.get('has_error', False)}")

    if price_data.get("error_message"):
        print(f"Error Message: {price_data.get('error_message')}")

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
        cursor = JioMartProductSave(conn)
        cursor.ensure_table()

        read_cursor = conn.cursor(dictionary=True)
        read_cursor.execute(GET_PENDING_INPUTS)
        rows = read_cursor.fetchall()
        read_cursor.close()

        for row in rows[:10]:
            pincode = row.get("pincode")
            input_id = row.get("id")
            url = row.get("url")

            print(f"\nProcessing ID: {input_id}, Pincode: {pincode}")
            print(f"URL: {url}")

            price = parser.get_product_details(url, str(pincode))
            print_product(price)

            try:
                cursor.save(input_id, url, pincode, price)
            except Exception as save_error:
                print(f"Error saving product data for ID {input_id}: {save_error}")
                conn.rollback()

            time.sleep(0.5)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Database not found or error: {e}")


if __name__ == "__main__":
    main()
