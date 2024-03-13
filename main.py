from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import DATABASE as DATABASE
from flask_cors import CORS, cross_origin
import sqlite3
import json
import logging
import ast


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# logging.basicConfig(level=logging.INFO)
# app.config['SECRET_KEY'] = 'its my very secret password that no one supposed to know'
# logging.getLogger('flask_cors').level = logging.DEBUG
# people_cors = CORS(app, resources={r"/people*": {"origins": "*"}})

conn = sqlite3.connect('db/DATAbase.db')
c = conn.cursor()










# (name, description, price, category_id, image)
# product = ('mobileN', 'its the NntMobile', 100, 1, '1.png')
# def add_one_product(thing):
#     try:
#         # 5 column
#         c.execute('''INSERT INTO products (name, description, price, category_id, image) VALUES 
#                  (?,?,?,?,?)''', thing)
#         conn.commit()
#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
# add_one_product(product)


# name, description, parent_category_id, created_at
# def add_one_category(name, description, parent_name):
#     c.execute(f"SELECT parent_category_id from category where name = {parent_name}")
#     Pid = c.fetchone()
#     # 4 column
#     c.execute(f'''INSERT INTO categories (name, description, parent_category_id, created_at) VALUES 
#               ({name}, {description}, {Pid}, DATETIME('now'))''')
#     conn.commit()
# add_one_category()

@app.route('/Pcategories')
def get_parent_categories():
    category_list = []
    for category in DATABASE.GET_PARENT_CATEGORIES:
        category_dict = {
            "category_id": category[0],
            "name": category[1],
            "description": category[2],
            "parent_category_id": category[3],
            "created_at": category[4],
        }
        category_list.append(category_dict)
    return jsonify(category_list), 200


@app.route('/Acategories')
def get_all_categories():
    category_list = []
    for category in DATABASE.GET_ALL_CATEGORIES:
        category_dict = {
            "category_id": category[0],
            "name": category[1],
            "description": category[2],
            "parent_category_id": category[3],
            "created_at": category[4],
        }
        category_list.append(category_dict)
    return jsonify(category_list), 200


@app.route('/products', methods=['GET'])
def get_products():
    products_list = []
    for product in DATABASE.GET_ALL_PRODUCTS:
        product_dict = {
            "product_id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": f'/static/products_images/{product[0]}' # Use product ID directly
        }
        products_list.append(product_dict)
    return jsonify(products_list), 200
    # if request.method == 'GET':
    # elif request.method == 'POST':


# @app.route('/main/products/product/<path:filename>')
# def get_image(filename):
#     print('serving image')
#     return send_from_directory('static/product_images', filename)


# @app.route('/main/products/product/<int:id>')
# def serve_image(id):
#     filename = str(id) # Do not include the extension here
#     return send_from_directory('static/products_images', filename)



# "image": f'/static/products_images/{product[0]}'


# --------------------------------------------------------------------------------------------------------------------


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('db/DATAbase.db')
    conn.row_factory = sqlite3.Row
    return conn



# CUSTOMER
# Create a new customer
def create_customer(name, email, phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO customers (name, email, phone_number, registration_date) VALUES (?, ?, ?, DATETIME('now'))", (name, email, phone))
    conn.commit()
    customer_id = cur.lastrowid
    conn.close()
    return customer_id

# Get a customer by ID
def get_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers WHERE customer_id = ?', (customer_id,))
    customer = cur.fetchone()
    final_customer = {
            "customer_id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone_number": customer[3],
            "registration_date": customer[4],
        }
    conn.close()
    return final_customer

# Update a customer
def update_customer(customer_id, name, email, phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE customers SET name = ?, email = ?, phone_number = ? WHERE customer_id = ?', (name, email, phone, customer_id))
    conn.commit()
    conn.close()
    return get_customer(customer_id)

# Delete a customer
def delete_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM customers WHERE customer_id = ?', (customer_id,))
    conn.commit()
    conn.close()

# Get all customers
def get_all_customers(limit):
# def get_all_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM customers LIMIT {limit}')
    # cur.execute(f'SELECT * FROM customers')
    customers = cur.fetchall()
    final_customers = []
    for customer in customers:
        final_customers.append({
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "registration_date": customer[4],
        })
    conn.close()
    return final_customers




# PRODUCT
# Create a new product
def create_product(name, description, price, category_id, image):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, description, price, category_id, image) VALUES (?, ?, ?, ?, ?)", (name, description, price, category_id, image))
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return product_id

# Get a product by ID
def get_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
    product = cur.fetchone()
    final_product = {
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": product[5],
        }
    conn.close()
    return final_product

# Update a product
def update_product(product_id, name, description, price, category_id, image):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE products SET name = ?, description = ?, price = ?, image = ? WHERE product_id = ?', (name, description, price, category_id, image))
    conn.commit()
    conn.close()
    return get_product(product_id)

# Delete a product
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()

# Get all products
def get_all_products(limit):
# def get_all_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM products LIMIT {limit}')
    # cur.execute(f'SELECT * FROM products')
    products = cur.fetchall()
    final_products = []
    for product in products:
        final_products.append({
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": product[5],
        })
    conn.close()
    return final_products








@app.route('/', methods=['GET'])
def test_backEnd():
    return jsonify('ok')



# CUSTOMER
# @app.route('/customer', methods=['GET'])
# def list_customer():
#     range = request.args.get('range')
#     customers = get_all_customers(int(range[3])+1)
#     # customers = get_all_customers()
#     response = jsonify(customers)
#     response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
#     response.headers['Content-Range'] = len(customers)
#     return response

@app.route('/customer', methods=['GET'])
def list_customer():
      range_str = request.args.get('range')
      if range_str:
          range_list = json.loads(range_str)
          limit = range_list[1] - range_list[0] + 1 # Calculate the limit based on the range
          customers = get_all_customers(limit)
      else:
          # Handle the case where 'range' is not provided
          customers = get_all_customers() # Or set a default limit
      response = jsonify(customers)
      response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
      response.headers['Content-Range'] = f'items 0-{len(customers)-1}/{len(customers)}' # Adjust the format as needed
      return response

@app.route('/customer', methods=['POST'])
def add_customer():
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    customer_id = create_customer(name, email, phone)
    return jsonify(get_customer(customer_id)), 201

@app.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    customer = get_customer(customer_id)
    if customer is None:
        return '', 404
    return jsonify(customer), 200

@app.route('/customer/<int:customer_id>', methods=['PUT'])
def update_customer_by_id(customer_id):
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    updated = update_customer(customer_id, name, email, phone)
    return jsonify(updated), 200

@app.route('/customer/<int:customer_id>', methods=['DELETE'])
def delete_customer_by_id(customer_id):
    delete_customer(customer_id)
    return jsonify({"id":customer_id}), 200
    


# PRODUCT
@app.route('/product', methods=['GET'])
def list_product():
    range = request.args.get('range')
    products = get_all_products(int(range[3])+1)
    # products = get_all_customers()
    response = jsonify(products)
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = len(products)
    return response

@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    category_id = request.json['category_id']
    image = request.json['image']
    product_id = create_customer(name, description, price, category_id, image)
    return jsonify(get_product(product_id)), 201

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    product = get_product(product_id)
    if product is None:
        return '', 404
    return jsonify(product), 200

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product_by_id(product_id):
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    category_id = request.json['category_id']
    image = request.json['image']
    updated = update_product(product_id, name, description, price, category_id, image)
    return jsonify(updated), 200

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product_by_id(product_id):
    delete_product(product_id)
    return jsonify({"id":product_id}), 200







@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404   

if __name__ == '__main__':
    app.run(debug=True,port=80)