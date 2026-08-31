import pandas as pd
from database import get_db_connection

data = pd.read_excel("jiomart_inputs.xlsx")

conn = get_db_connection()

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jiomart_inputs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500),
    pincode VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending'
)
""")

for i in range(len(data)):
    url = data.loc[i, "URL"]
    pincode = str(data.loc[i, "Pincode"])

    cursor.execute(
        "INSERT INTO jiomart_inputs (url, pincode, status) VALUES (%s, %s, 'pending')",
        (url, pincode),
    )

conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully!")
