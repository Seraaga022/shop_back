import sqlite3 

# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('db/DATAbase.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create a new customer
def create_customer(name, email, phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO customers (name, email, phone_number, registration_date) VALUES (?, ?, ?, DATE('now'))", (name, email, phone))
    conn.commit()
    customer_id = cur.lastrowid
    conn.close()
    return customer_id


# Create 40 customers
for i in range(40):
    name = f'Customer {i}'
    email = f'customer{i}@example.com'
    phone = f'555-123-456{i}'
    create_customer(name, email, phone)
