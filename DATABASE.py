from datetime import date, datetime
import sqlite3

conn = sqlite3.Connection('db/DATAbase.db')
c = conn.cursor()

# create customers table
c.execute('''CREATE TABLE IF NOT EXISTS customers
             (customer_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              name VARCHAR(50) NOT NULL, 
              email VARCHAR(100) NOT NULL, 
              phone_number VARCHAR(15) NOT NULL, 
              registration_date DATE NOT NULL)''')

# create products table and path of image
c.execute('''CREATE TABLE IF NOT EXISTS products
             (product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              name VARCHAR(100) NOT NULL, 
              description TEXT NOT NULL, 
              price DECIMAL(10,2) NOT NULL, 
              category_id INT NOT NULL, 
              image TEXT NOT NULL)''')

# create orders table
c.execute('''CREATE TABLE IF NOT EXISTS orders
             (order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              customer_id INT NOT NULL, 
              order_date DATETIME NOT NULL, 
              total_amount DECIMAL(10,2) NOT NULL, 
              status VARCHAR(20) NOT NULL)''')

# create orderDetails table
c.execute('''CREATE TABLE IF NOT EXISTS orderDetails
             (order_detail_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              order_id INT NOT NULL, 
              product_id INT NOT NULL, 
              quantity INT NOT NULL, 
              unit_price DECIMAL(10,2) NOT NULL)''')

# create categories table
c.execute('''CREATE TABLE IF NOT EXISTS categories
             (category_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              name VARCHAR(50) NOT NULL, 
              description TEXT NOT NULL, 
              parent_category_id INT, 
              created_at DATETIME NOT NULL)''')

# create users table
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              username VARCHAR(50) NOT NULL, 
              password_hash VARCHAR(100) NOT NULL, 
              email VARCHAR(100) NOT NULL, 
              role VARCHAR(20) NOT NULL)''')

# create payments table
c.execute('''CREATE TABLE IF NOT EXISTS payments
             (payment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              order_id INT NOT NULL, 
              payment_method VARCHAR(50) NOT NULL, 
              amount DECIMAL(10,2) NOT NULL, 
              payment_date DATETIME NOT NULL)''')

# create shippingAddresses table
c.execute('''CREATE TABLE IF NOT EXISTS shippingAddresses
             (address_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              customer_id INT NOT NULL, 
              recipient_name VARCHAR(100) NOT NULL, 
              address_line1 VARCHAR(255) NOT NULL, 
              address_line2 VARCHAR(255), 
              city VARCHAR(100) NOT NULL, 
              state VARCHAR(100) NOT NULL, 
              postal_code VARCHAR(20) NOT NULL, 
              county VARCHAR(100) NOT NULL)''')

# create feedbacks table
c.execute('''CREATE TABLE IF NOT EXISTS feedbacks
             (feedback_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              customer_id INT NOT NULL, 
              order_id INT NOT NULL, 
              rating INT NOT NULL, 
              comment TEXT NOT NULL, 
              feedback_date DATETIME NOT NULL)''')

# create adminLogs table
c.execute('''CREATE TABLE IF NOT EXISTS adminLogs
             (log_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              user_id INT NOT NULL, 
              action VARCHAR(100) NOT NULL, 
              action_date DATETIME NOT NULL, 
              ip_address VARCHAR(50) NOT NULL)''')

now = datetime.now()
DateTimeNow = now.strftime("%d/%m/%Y %H:%M:%S")

# name, description, parent_category_id, created_at
categories = [
    ('mobile', 'just mobiles', None, DateTimeNow),
    ('electronic', 'all electronic stuff', None, DateTimeNow),
    ('laptop', 'all laptops', 2, DateTimeNow),
    ('headphone', 'just headphone', 2, DateTimeNow),
    ('home_And_Kitchen', 'everything in kitchen and house either', None, DateTimeNow),
    ('kithen', 'everythin in kitchen', 3, DateTimeNow),
    ('Furniture_And_Home_Decoration', 'furnitures and intire house decoration either', 3, DateTimeNow),
    ('hypermarket', 'comestible stuff', None, DateTimeNow),
    ('snacks', 'snacks stuff', 4, DateTimeNow),
    ('essential_products', 'its just what it is', 4, DateTimeNow)
]
# c.execute('''INSERT INTO categories (name, description, parent_category_id, created_at) VALUES ('mobile', 'just mobiles', NULL, DATETIME('now')),
#           ('electronic', 'all electronic stuff', NULL, DATETIME('now')),
#           ('laptop', 'all laptops', 2, DATETIME('now')),
#           ('headphone', 'just headphone', 2, DATETIME('now')),
#           ('home_And_Kitchen', 'everything in kitchen and house either', NULL, DATETIME('now')),
#           ('kithen', 'everythin in kitchen', 3, DATETIME('now')),
#           ('Furniture_And_Home_Decoration', 'furnitures and intire house decoration either', 3, DATETIME('now')),
#           ('hypermarket', 'comestible stuff', NULL, DATETIME('now')),
#           ('snacks', 'snacks stuff', 4, DATETIME('now')),
#           ('essential_products', 'its just what it is', 4, DATETIME('now'))''')


# (name, description, price, category_id, image)
products = [
    ('mobile1', 'its the 1ndMobile', 100, 1, '1.png'),
    ('mobile2', 'its the 2rdMobile', 100, 1, '1.png'),
    ('mobile3', 'its the 3thMobile', 100, 1, '1.png'),
    ('mobile4', 'its the 4thMobile', 100, 1, '1.png'),
    ('mobile5', 'its the 5thMobile', 100, 1, '1.png'),
    ('mobile6', 'its the 6thMobile', 100, 1, '1.png'),
    ('mobile7', 'its the 7thMobile', 100, 1, '1.png'),
    ('mobile8', 'its the 8thMobile', 100, 1, '1.png'),
    ('mobile9', 'its the 9thMobile', 100, 1, '1.png'),
    ('mobile10', 'its the 10thMobile', 100, 1, '1.png'),
    ('mobile11', 'its the 11thMobile', 100, 1, '1.png'),
    ('mobile12', 'its the 12thMobile', 100, 1, '1.png'),
    ('mobile13', 'its the 13thMobile', 100, 1, '1.png'),
    ('mobile14', 'its the 14thMobile', 100, 1, '1.png'),
    ('mobile15', 'its the 15thMobile', 100, 1, '1.png'),
    ('mobile16', 'its the 16thMobile', 100, 1, '1.png'),
    ('mobile17', 'its the 17thMobile', 100, 1, '1.png'),
    ('mobile18', 'its the 18thMobile', 100, 1, '1.png'),
    ('mobile19', 'its the 19thMobile', 100, 1, '1.png'),
    ('mobile20', 'its the 20thMobile', 100, 1, '1.png'),
    ('mobile21', 'its the 21thMobile', 100, 1, '1.png'),
    ('mobile22', 'its the 22thMobile', 100, 1, '1.png'),
    ('mobile23', 'its the 23thMobile', 100, 1, '1.png'),
    ('mobile24', 'its the 24thMobile', 100, 1, '1.png'),
    ('mobile25', 'its the 25thMobile', 100, 1, '1.png'),
    ('mobile26', 'its the 26thMobile', 100, 1, '1.png'),
    ('mobile27', 'its the 27thMobile', 100, 1, '1.png'),
    ('mobile28', 'its the 28thMobile', 100, 1, '1.png'),
    ('mobile29', 'its the 29thMobile', 100, 1, '1.png')
]
# c.execute('''INSERT INTO products (name, description, price, category_id, image) VALUES ('mobile1', 'its the 1ndMobile', 100, 1, '1.png'),
#     ('mobile2', 'its the 2rdMobile', 100, 1, '1.png'),
#     ('mobile3', 'its the 3thMobile', 100, 1, '1.png'),
#     ('mobile4', 'its the 4thMobile', 100, 1, '1.png'),
#     ('mobile5', 'its the 5thMobile', 100, 1, '1.png'),
#     ('mobile6', 'its the 6thMobile', 100, 1, '1.png'),
#     ('mobile7', 'its the 7thMobile', 100, 1, '1.png'),
#     ('mobile8', 'its the 8thMobile', 100, 1, '1.png'),
#     ('mobile9', 'its the 9thMobile', 100, 1, '1.png'),
#     ('mobile10', 'its the 10thMobile', 100, 1, '1.png'),
#     ('mobile11', 'its the 11thMobile', 100, 1, '1.png'),
#     ('mobile12', 'its the 12thMobile', 100, 1, '1.png'),
#     ('mobile13', 'its the 13thMobile', 100, 1, '1.png'),
#     ('mobile14', 'its the 14thMobile', 100, 1, '1.png'),
#     ('mobile15', 'its the 15thMobile', 100, 1, '1.png'),
#     ('mobile16', 'its the 16thMobile', 100, 1, '1.png'),
#     ('mobile17', 'its the 17thMobile', 100, 1, '1.png'),
#     ('mobile18', 'its the 18thMobile', 100, 1, '1.png'),
#     ('mobile19', 'its the 19thMobile', 100, 1, '1.png'),
#     ('mobile20', 'its the 20thMobile', 100, 1, '1.png'),
#     ('mobile21', 'its the 21thMobile', 100, 1, '1.png'),
#     ('mobile22', 'its the 22thMobile', 100, 1, '1.png'),
#     ('mobile23', 'its the 23thMobile', 100, 1, '1.png'),
#     ('mobile24', 'its the 24thMobile', 100, 1, '1.png'),
#     ('mobile25', 'its the 25thMobile', 100, 1, '1.png'),
#     ('mobile26', 'its the 26thMobile', 100, 1, '1.png'),
#     ('mobile27', 'its the 27thMobile', 100, 1, '1.png'),
#     ('mobile28', 'its the 28thMobile', 100, 1, '1.png'),
#     ('mobile29', 'its the 29thMobile', 100, 1, '1.png')''')

conn.commit()





c.execute("SELECT * FROM customers")
GET_ALL_CUSTOMERS = c.fetchall()
c.execute("SELECT * FROM products")
GET_ALL_PRODUCTS = c.fetchall()
c.execute("SELECT * FROM orders")
GET_ALL_ORDERS = c.fetchall()
c.execute("SELECT * FROM orderDetails")
GET_ALL_ORDERDETAILS = c.fetchall()
c.execute("SELECT * FROM categories")
GET_ALL_CATEGORIES = c.fetchall()
c.execute("SELECT * FROM categories where parent_category_id IS NULL")
GET_PARENT_CATEGORIES = c.fetchall()