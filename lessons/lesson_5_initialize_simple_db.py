import sqlite3

connection = sqlite3.connect("user.db")

cursor = connection.cursor()

create_table_query = """
    CREATE TABLE IF NOT EXISTS users(
        id integer primary key,
        first_name text,
        last_name text,
        phone_number text
    );
"""

cursor.execute(create_table_query)
connection.commit()
connection.close()




sample_data_query = """
    INSERT INTO users (
        id, first_name, last_name, phone_number
    )
    VALUES (
        ?, ?, ?, ?
    )
"""


SAMPLE_DATA = [
    (111, "Rakibul", "Hasan", "11111111111"),
    (112, "Abdur", "Rahim", "22222222222"),
    (113, "Abul", "Kalam", "33333333333"),
    (114, "Oni", "Khan", "44444444444"),
    (115, "Mehedi", "Himel", "55555555555"),
]


# with sqlite3.connect("user.db") as connection:
#     cursor = connection.cursor()
#     cursor.executemany(sample_data_query, SAMPLE_DATA)



fetch_data_query = """
    SELECT id, first_name, last_name, phone_number FROM users
"""

rows = []

with sqlite3.connect("user.db") as connection:
    cursor = connection.cursor()
    cursor.execute(fetch_data_query)
    rows = cursor.fetchall()


for row in rows:
    print(f"ID: {row[0]} || Name: {row[1]} {row[2]} || Contact: {row[3]}")
