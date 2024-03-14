from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import DATABASE as DATABASE
from flask_cors import CORS, cross_origin
import sqlite3
import json
import logging
import ast


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logging.basicConfig(level=logging.INFO)
# app.config['SECRET_KEY'] = 'its my very secret password that no one supposed to know'
# logging.getLogger('flask_cors').level = logging.DEBUG
# people_cors = CORS(app, resources={r"/people*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/DATAbase.db'
db = SQLAlchemy(app)
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
def get_all_customers(RngStart, RngEnd):
# def get_all_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM customers LIMIT {RngEnd - RngStart + 1} OFFSET {RngStart}')
    # cur.execute(f'SELECT * FROM customers LIMIT {limit}')
    customers = cur.fetchall()
    final_customers = []
    for customer in customers:
        final_customers.append({
            "customer_id": customer[0],
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
            "product_id": product[0],
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
            "product_id": product[0],
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



# @app.route('/customer', methods=['GET'])
# def list_customer():
#     range = request.args.get('range')
#     customers = get_all_customers(int(range[3])+1)
#     # customers = get_all_customers()
#     response = jsonify(customers)
#     response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
#     response.headers['Content-Range'] = len(customers)
#     return response

# CUSTOMER
# this is good, dont delete it
# @app.route('/customer', methods=['GET'])
# def list_customer():
#     logging.debug("Received 'GET' request for /customer")
#     range_str = request.args.get('range')
#     sort_str = request.args.get('sort')

#     # Initialize variables for pagination and sorting
#     start = 0
#     end = 10 # Default end value, adjust as needed
#     field = 'id' # Default sort field
#     order = 'ASC' # Default sort order

#     # Parse range if provided
#     if range_str:
#         range_list = json.loads(range_str)
#         start = range_list[0]
#         end = range_list[1]
    
#     # Parse sort if provided
#     if sort_str:
#         sort_list = json.loads(sort_str)
#         field = sort_list[0]
#         order = sort_list[1]
        
#     # Log the parsed parameters for debugging
#     # print(f"Range: {start}-{end}, Sort: {field} {order}")
#     logging.debug(f'Range: {start}-{end}, Sort: {field} {order}')
    
#     # Establish a database connection and cursor if not already done
#     conn = sqlite3.connect('db/DATAbase.db')
#     cur = conn.cursor()
    
#     # allowed_fields = ['customer_id', 'name', 'email', 'phone', 'registration_date']
#     # if field not in allowed_fields:
#     #     return jsonify({"error": "Invalid field for sorting"}), 400

#     # For example, if you're using SQLite, your query might look like this:
#     cur.execute(f'SELECT * FROM customers ORDER BY customer_{field} {order} LIMIT ? OFFSET ?', (end - start + 1, start))
    
#     # Fetch the customers from the database
#     customers = cur.fetchall()
    
#     # Convert the database records to a list of dictionaries for the response
#     final_customers = []
#     for customer in customers:
#         final_customers.append({
#             "customer_id": customer[0],
#             "name": customer[1],
#             "email": customer[2],
#             "phone": customer[3],
#             "registration_date": customer[4],
#         })
    
#     # Return the customers as JSON
#     return jsonify(final_customers), 200

# its working completely with range and sort and filter
@app.route('/customer', methods=['GET'])
def list_customer():

    logging.debug("Received 'GET' request for /customer")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Default empty filter
    
    # Parse range if provided
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    # Parse sort if provided
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    # Parse filter if provided
    if filter_str:
        filters = json.loads(filter_str)
    
    # Establish a database connection and cursor if not already done
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Adjust your database query to use LIMIT, OFFSET, ORDER BY, and WHERE based on start, end, field, order, and filters
    # For example, if you're using SQLite, your query might look like this:
    # Note: This is a simplified example. The actual implementation will depend on your database and ORM.
    # Also, ensure to validate the field, order, and filters against a list of allowed values to prevent SQL injection.
    query = f'SELECT * FROM customers ORDER BY customer_{field} {order} LIMIT ? OFFSET ?'
    params = (end - start + 1, start)
    
    # Apply filters to the query
    for key, value in filters.items():
        query += f' AND {key} = ?'
        params += (value,)
    
    cur.execute(query, params)
    
    # Fetch the customers from the database
    customers = cur.fetchall()
    
    # Convert the database records to a list of dictionaries for the response
    final_customers = []
    for customer in customers:
        final_customers.append({
            "customer_id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "registration_date": customer[4],
        })
    
    # Return the customers as JSON
    return jsonify(final_customers), 200

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
    return jsonify({"customer_id":customer_id}), 200
    


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
    return jsonify({"product_id":product_id}), 200







@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404   

if __name__ == '__main__':
    app.run(debug=True,port=80)
