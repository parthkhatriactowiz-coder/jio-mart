import logging
from concurrent.futures import ThreadPoolExecutor
from parsor import JioMartParser
from product_repository import JioMartProductSave
from database import get_db_connection, GET_PENDING_INPUTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

MAX_WORKERS = 10


def process_row(row):
    input_id = row["id"]
    url = row["url"]
    pincode = str(row["pincode"])

    logger.info(f"Processing ID: {input_id} | Pincode: {pincode}")

    parser = JioMartParser()
    price_data = parser.get_product_details(url, pincode)
    print(f"Price Data: {price_data}")

    # try:
    #     conn = get_db_connection()
    #     repo = JioMartProductSave(conn)
    #     repo.save(input_id, url, pincode, price_data)
    #     repo.close()
    #     conn.close()
    #     logger.info(f"Saved ID: {input_id}")
    # except Exception as err:
    #     logger.error(f"Error saving ID {input_id}: {err}")


def main():
    try:
        conn = get_db_connection()
        repo = JioMartProductSave(conn)
        repo.ensure_table()

        db_cursor = conn.cursor(dictionary=True)
        db_cursor.execute(GET_PENDING_INPUTS)
        rows = db_cursor.fetchall()

        db_cursor.close()
        repo.close()
        conn.close()

        logger.info(f"Found {len(rows)} pending records to process.")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(process_row, rows[:10])

        logger.info("Finished processing all records.")

    except Exception as e:
        logger.error(f"Database error: {e}")


if __name__ == "__main__":
    main()
