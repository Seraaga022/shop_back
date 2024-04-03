from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from PIL import Image
import DATABASE as DATABASE
import sqlite3
import json
import logging
import base64
import os
import io
import uuid
import time


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logging.basicConfig(level=logging.INFO)
# app.config['SECRET_KEY'] = 'its my very secret password that no one supposed to know'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/DATAbase.db'
# logging.getLogger('flask_cors').level = logging.DEBUG




def get_items_quantity_totalCount_totalPrice_customerId(id):
    conn = get_db_connection()
    cur = conn.cursor()
    finall = []
    quantity = 0
    total_price = 0
    cur.execute('''SELECT *, COUNT(products.price) AS price FROM cart 
                     JOIN products
                     ON products.product_id = cart.product_id
                     WHERE customer_id = ?
                     GROUP BY cart.cart_id
                ''', (id,)) # Use parameterized query
    items = cur.fetchall()
    for item in items:
        quantity += item["quantity"] # Assuming this is the quantity column
        total_price += item["price"] * item["quantity"] # Multiply price by quantity and add to total_price
        finall.append({
            "cart_id": item["cart_id"],
            "customer_id": item["customer_id"],
            "product_id": item["product_id"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "product_price": item["price"],
            "quantity": item["quantity"],
            "product_price": item["price"]
        })

    return jsonify({"items": finall, "quantity": quantity, "item_count": len(items), "total_price": total_price})
# usage
# items = response.get_json()["items"]
# for item in items:
#     cart_id = item["cart_id"]
# quantity = response.get_json()["quantity"]
# item_count = response.get_json()["item_count"]
# total_price = response.get_json()["total_price"]


@app.route('/COI/<int:id>', methods=["GET"])
def Check_out_info(id):
    conn = get_db_connection()
    cur = conn.cursor()
    finall = []
    quantity = 0
    total_price = 0
    cur.execute('''SELECT *, COUNT(products.price) AS price FROM cart 
                     JOIN products
                     ON products.id = cart.product_id
                     WHERE customer_id = ?
                     GROUP BY cart.cart_id
                ''', (id,)) # Use parameterized query
    items = cur.fetchall()
    for item in items:
        quantity += item["quantity"] # Assuming this is the quantity column
        total_price += item["price"] * item["quantity"] # Multiply price by quantity and add to total_price
        finall.append({
            "cart_id": item["cart_id"],
            "customer_id": item["customer_id"],
            "product_id": item["product_id"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "product_price": item["price"],
        })
    return jsonify({"items": finall, "quantity": quantity, "item_count": len(items), "total_price": total_price}), 200


@app.route('/Pcategories', methods=["GET"])
def get_parent_categories():
    conn = sqlite3.Connection('db/DATAbase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM categories where parent_category_id IS NULL")
    PARENT_CATEGORIES = c.fetchall()
    category_list = []
    for category in PARENT_CATEGORIES:
        with open(f'static/category_symbol/{category[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        category_dict = {
            "category_id": category[0],
            "name": category[1],
            "description": category[2],
            "parent_category_id": category[3],
            "created_at": category[4],
            "image": encoded_string,
        }
        category_list.append(category_dict)
    return jsonify(category_list), 200


@app.route('/ALLcategory/<int:parent_id>', methods=["GET"])
def get_category_with_this_parentID(parent_id):
    category_list = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM categories
                   WHERE categories.parent_category_id = ?''', (parent_id,))
    categories = cur.fetchall()
    for category in categories:
        with open(f'static/category_symbol/{category[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        category_list.append({
            "category_id": category[0],
            "name": category[1],
            "description": category[2],
            "parent_category_id": category[3],
            "created_at": category[4],
            "image": encoded_string,
        })

    print(f"the number of categories found by this => '{parent_id}' category id is = {len(category_list)} ")
    return jsonify(category_list), 200


@app.route('/subCategory/<int:sub_cat_id>', methods=["GET"])
def get_sub_category_by_id(sub_cat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    finall_products = []
    cur.execute(f''' SELECT * FROM products WHERE category_id = {sub_cat_id} ''')
    products = cur.fetchall()
    for product in products:
        with open(f'static/product_images/{product[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        finall_products.append({
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": encoded_string
        })
    return jsonify(finall_products), 200


@app.route('/products', methods=['GET'])
def get_products_for_customer():
    final_products = []
    for product in DATABASE.GET_ALL_PRODUCTS:
        # Read the image file and convert it to base64
        with open(f'static/product_images/{product[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        final_products.append({
            "product_id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": encoded_string, # The base64 encoded image
        })

    return jsonify(final_products), 200

    # if request.method == 'GET':
    # elif request.method == 'POST':


@app.route('/searchProducts', methods=['GET'])
def get_products_for_customer_search():
    final_products = []
    for product in DATABASE.GET_ALL_PRODUCTS:
        # Read the image file and convert it to base64
        with open(f'static/product_images/{product[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        final_products.append({
            "product_id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": encoded_string, # The base64 encoded image
        })

    return jsonify(final_products), 200

    # if request.method == 'GET':
    # elif request.method == 'POST':


@app.route('/', methods=["GET"])
def test_back_end():
    return jsonify('ok')

def get_db_connection():
    conn = sqlite3.connect('db/DATAbase.db')
    conn.row_factory = sqlite3.Row
    return conn



# -------------------------- ADMIN START -----------------------
# -------------------------- FUNCTIONS ---------------

# CUSTOMER
# Create a new customer
def create_customer(name, email, phone, image):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(" INSERT INTO customers (name, email, phone, image) VALUES (?, ?, ?, ?)", (name, email, phone, image))
    conn.commit()
    cur.execute(''' SELECT id from customers order by id DESC LIMIT 1 ''')
    customer_id = cur.fetchone()[0]
    conn.close()
    return customer_id

# Get a customer by ID
def get_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer = cur.fetchone()
    with open(f'static/customer_img/{customer[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    final_customer = {
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "registration_date": customer[4],
            "image": encoded_string,
        }
    conn.close()
    return final_customer

# Update a customer
def update_customer(customer_id, name, email, phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE customers SET name = ?, email = ?, phone = ? WHERE id = ?', (name, email, phone, customer_id))
    conn.commit()
    conn.close()
    return get_customer(customer_id)

# Delete a customer
def delete_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    conn.close()
    
    

# CATEGORY
# Create a new category
def create_category(name, description, parent_category_id, image):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO categories (name, description, parent_category_id, image) VALUES (?, ?, ?, ?)", (name, description, parent_category_id, image,))
    conn.commit()
    cur.execute(''' SELECT id from categories order by id DESC LIMIT 1 ''')
    category_id = cur.fetchone()[0]
    conn.close()
    return category_id

# Get a category by ID
def get_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
    category = cur.fetchone()
    # with open(f'static/category_symbol/{category[5]}', 'rb') as image_file:
    #         encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    final_category = {
            "id": category[0],
            "name": category[1],
            "description": category[2],
            "PCI": category[3],
            # "created_at": category[4],
            # "image": encoded_string,
        }
    conn.close()
    return final_category

# Update a category
def update_category(name, description, parent_category_id, category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE categories SET name = ?, description = ?, parent_category_id = ? WHERE id = ?', (name, description, parent_category_id, category_id))
    conn.commit()
    conn.close()
    return get_category(category_id)

# Delete a category
def delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    conn.commit()
    conn.close()



# PRODUCT
# Create a new product
def create_product(name, description, price, category_id, image):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, description, price, category_id, image) VALUES (?, ?, ?, ?, ?)", (name, description, price, category_id, image))
    conn.commit()
    cur.execute(''' SELECT id FROM products ORDER BY id DESC LIMIT 1 ''')
    product_id = cur.fetchone()[0]
    conn.close()
    return product_id

# Get a product by ID
def get_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cur.fetchone()
    final_products = {
        "product_id": product[0],
        "name": product[1],
        "description": product[2],
        "price": product[3],
        "category_id": product[4],
        }
    conn.close()
    if product is None:
        return '', 404
    return final_products

# Update a product
def update_product(product_id, name, description, price, category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE products SET name = ?, description = ?, price = ?, category_id = ? WHERE id = ?', (name, description, price, category_id, product_id))
    conn.commit()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cur.fetchone()
    final_products = {
        "product_id": product[0],
        "name": product[1],
        "description": product[2],
        "price": product[3],
        "category_id": product[4],
        }
    conn.close()
    if product is None:
        return '', 404
    return final_products
    
# Delete a product
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()


def get_user_name_by_id(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * from users WHERE id = ? ''', (id,))
    user_name = ''
    if c.fetchone() != None:
        user_name = c.fetchone()[1]
    return user_name


def get_user_id_by_name(name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * FROM users WHERE username = ? ''', (name))
    user_id = 0
    if c.fetchone() != None:
        user_id = c.fetcone()[0]
    
    return user_id

# -------------------------- ROUTES ------

# CUSTOMER
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
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM customers WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    customers = cur.fetchall()
    
    # Convert the database records to a list of dictionaries for the response
    final_customers = []
    for customer in customers:
        final_customers.append({
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
        })

    total_count = len(DATABASE.GET_ALL_CUSTOMERS)
    response = jsonify({"data": final_customers})
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = f'customers 0-{len(final_customers)}/{total_count}'
    return response, 200


@app.route('/customer', methods=['POST'])
def create_customer():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    image_file = request.files.get('image')

    if user_exists(phone, name):
        return jsonify({'message': 'User already exists'}), 400
    if image_file:
        image = Image.open(image_file)
        if image.format.upper() != 'PNG':
            image = image.convert('RGBA')
        unique_filename = generate_unique_filename_png('static/customer_img')
        image_filename = f'{unique_filename}.png'
        image_path = os.path.join('static/customer_img', image_filename)
        image.save(image_path, 'PNG') # Specify 'PNG' as the format

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(" INSERT INTO customers (name, email, phone, image) VALUES (?, ?, ?, ?)", (name, email, phone, image_filename))
        conn.commit()
        cur.execute(''' SELECT id from customers order by id DESC LIMIT 1 ''')
        customer_id = cur.fetchone()[0]
        conn.close()
    else: 
        cur = conn.cursor()
        cur.execute(" INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        cur.execute(''' SELECT id from customers order by id DESC LIMIT 1 ''')
        customer_id = cur.fetchone()[0]
        conn.close()

    return jsonify(get_customer(customer_id)), 201


@app.route('/customer/<id>', methods=['GET'])
def get_customer_by_id(id):
    customer = get_customer(id)
    if customer is None:
        return '', 404
    return jsonify(customer), 200


@app.route('/customer/<int:id>', methods=['PUT'])
def update_customer_by_id(id):
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    updated = update_customer(id, name, email, phone)
    return jsonify(updated), 200


@app.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer_by_id(id):
    delete_customer(id)
    return jsonify({"customer_id":id}), 200




# CATEGORY
@app.route('/category', methods=['GET'])
def list_category():
    logging.debug("Received 'GET' request for /category")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM categories WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    categories = cur.fetchall()
    final_categories = []
    
    # Convert the database records to a list of dictionaries for the response
    for category in categories:
        final_categories.append({
            "id": category[0],
            "name": category[1],
            "description": category[2],
            # "PCI": category[3],
            "PCI": category[3] if category[3] is not None else 'parent',
            "created_at": category[4],
        })

    total_count = len(DATABASE.GET_ALL_CATEGORIES)
    # total_count = 123
    response = jsonify({ "data": final_categories })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'customers 0-{len(final_categories)}/{total_count}'
    return response, 200


@app.route('/category', methods=['POST'])
def create_category():
    name = request.form['name']
    description = request.form['description']
    parent_category_id = request.form.get('PCI')
    image_file = request.files.get('image')

    if image_file:
        image = Image.open(image_file)
        if image.format.upper() != 'PNG':
            image = image.convert('RGBA')
        image_filename = f'{name}.png'
        image_path = os.path.join('static/category_symbol', image_filename)
        image.save(image_path, 'PNG') # Specify 'PNG' as the format

    if parent_category_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO categories (name, description, parent_category_id, image) VALUES (?, ?, ?)", (name, description, parent_category_id, f'{name}.png'))
        conn.commit()
        cur.execute(''' SELECT id from categories order by id DESC LIMIT 1 ''')
        category_id = cur.fetchone()[0]
        cur.close()
        conn.close()
    else: 
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO categories (name, description, image) VALUES (?, ?, ?)", (name, description, f'{name}.png'))
        conn.commit()
        cur.execute(''' SELECT id from categories order by id DESC LIMIT 1 ''')
        category_id = cur.fetchone()[0]
        cur.close()
        conn.close()

    conn = get_db_connection() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
    category = cur.fetchone()
    final_category = {
            "id": category[0],
            "name": category[1],
            "description": category[2],
            "PCI": category[3],
        }
    conn.close()

    return jsonify(final_category), 201


@app.route('/category/<int:id>', methods=['GET'])
def get_category_by_id(id):
    category = get_category(id)
    if category is None:
        return '', 404
    return jsonify(category), 200


@app.route('/category/<int:id>', methods=['PUT'])
def update_category_by_id(id):
    name = request.form.get('name')
    description = request.form.get('description')
    parent_category_id = request.form.get('PCI')
    # image_file = request.files.get("image")

    # if image_file: 
    #     if image.format != 'PNG':
    #         image = image.convert('RGBA')
    #     image_path = os.path.join('static/category_symbol', f'{name}.png')
    #     image.save(image_path)

    updated = update_category(name, description, parent_category_id, id)
    return jsonify(updated), 200


@app.route('/category/<int:id>', methods=['DELETE'])
def delete_category_by_id(id):
    delete_category(id)
    return jsonify({"category_id": id}), 200
  



# PRODUCT
@app.route('/product', methods=['GET'])
def list_product():
    logging.debug("Received 'GET' request for /products")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    products = cur.fetchall()
    final_products = []
    
    # Convert the database records to a list of dictionaries for the response
    for product in products:
        final_products.append({
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "Cat": product[4],
        })

    total_count = len(DATABASE.GET_ALL_PRODUCTS)
    response = jsonify({ "data": final_products })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'customers 0-{len(final_products)}/{total_count}'
    return response, 200


@app.route('/product', methods=['POST'])
def create_product():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category_id = request.form.get('Cat')
    image_file = request.files.get('image')

    if image_file:
        image = Image.open(image_file)
        if image.format.upper() != 'JPEG':
            image = image.convert('RGB')
        image_filename = f'{name}.jpeg'
        image_path = os.path.join('static/product_images', image_filename)
        image.save(image_path, 'JPEG')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO products (name, description, price, category_id, image) VALUES (?, ?, ?, ?, ?)", (name, description, price, category_id, f'{name}.jpeg'))
    conn.commit()
    cur.execute(''' SELECT id from categories order by id DESC LIMIT 1 ''')
    product_id = cur.fetchone()[0]
    cur.close()
    conn.close()


    conn = get_db_connection() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cur.fetchone()
    final_product = {
        "id": product[0],
        "name": product[1],
        "description": product[2],
        "price": product[3],
        "category_id": product[4],
        }
    conn.close()

    return jsonify(final_product), 201


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cur.fetchone()
    final_products = {
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "Cat": product[4],
        }
    conn.close()
    if product is None:
        return '', 404
    return jsonify(final_products), 200


@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product_by_id(product_id):
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category_id = request.form.get('Cat')
    updated = update_product(product_id, name, description, price, category_id)
    return jsonify(updated), 200


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product_by_id(product_id):
    delete_product(product_id)
    return jsonify({"product_id": product_id}), 200




# PAYMENT
@app.route('/payment', methods=['GET'])
def list_payment():
    logging.debug("Received 'GET' request for /payments")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM payments WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    payments = cur.fetchall()
    final_payments = []
    
    # Convert the database records to a list of dictionaries for the response
    for payment in payments:
        final_payments.append({
            "id": payment[0],
            "order_id": payment[1],
            "payment_method": payment[2],
            "amount": payment[3],
            "payment_date": payment[4],
        })

    total_count = len(DATABASE.GET_ALL_PAYMENTS)
    response = jsonify({ "data": final_payments })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'customers 0-{len(final_payments)}/{total_count}'
    return response, 200


@app.route('/payment', methods=['POST'])
def create_payment():
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    amount = request.form.get('amount')


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO payments (order_id, payment_method, amount) VALUES (?, ?, ?)", (order_id, payment_method, amount))
    conn.commit()
    cur.execute(''' SELECT id from payments order by id DESC LIMIT 1 ''')
    payment_id = cur.fetchone()[0]
    cur.close()
    conn.close()


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
    payment = cur.fetchone()
    final_payment = {
        "id": payment[0],
        "order_id": payment[1],
        "payment_method": payment[2],
        "amount": payment[3],
        "payment_date": payment[4]}
    conn.close()

    return jsonify(final_payment), 201


@app.route('/payment/<int:id>', methods=['GET'])
def get_payment_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM payments WHERE id = ?', (id,))
    payment = cur.fetchone()
    final_payment = {
            "id": payment[0],
            "order_id": payment[1],
            "payment_method": payment[2],
            "amount": payment[3],
            "payment_date": payment[4],
        }
    conn.close()
    if payment is None:
        return '', 404
    return jsonify(final_payment), 200


@app.route('/payment/<int:id>', methods=['PUT'])
def update_payment_by_id(id):
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    amount = request.form.get('amount')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' UPDATE payments SET order_id = ?, payment_method = ?, amount = ? WHERE id = ? ''', (order_id, payment_method, amount, id,))
    conn.commit()
    c.close()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * FROM payments WHERE id = ? ''', (id,))
    payment = c.fetchone()
    final_back = {
        "id": payment[0],
        "order_id": payment[1],
        "payment_method": payment[2],
        "amount": payment[3],
        # "payment_date": payment[4],
    }
    conn.close()

    return jsonify(final_back), 200


@app.route('/payment/<int:id>', methods=['DELETE'])
def delete_payment_by_id(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' DELETE FROM payments WHERE id = ? ''', (id,))
    conn.commit()
    c.close()
    conn.close()
    return jsonify({"payment id": id}), 200




# ADDRESS
@app.route('/address', methods=['GET'])
def list_address():
    logging.debug("Received 'GET' request for /addresses")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM addresses WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    addresses = cur.fetchall()
    final_addresses = []
    
    # Convert the database records to a list of dictionaries for the response
    for address in addresses:
        final_addresses.append({
            "id": address[0],
            "order_id": address[1],
            "recipient_name": address[2],
            "address": address[3],
            "state": address[4],
            "country": address[5],
            "city": address[6],
            "postal_code": address[7],
        })

    total_count = len(DATABASE.GET_ALL_ADDRESSs)
    response = jsonify({ "data": final_addresses })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'addresses 0-{len(final_addresses)}/{total_count}'
    return response, 200


@app.route('/address', methods=['POST'])
def create_address():
    order_id = request.form.get('order_id')
    name = request.form.get('recipient_name')
    address = request.form.get('address')
    state = request.form.get('state')
    country = request.form.get('country')
    city = request.form.get('city')
    poste = request.form.get('postal_code')


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' INSERT INTO addresses(order_id, recipient_name, address, state, country, city, postal_code) VALUES (?, ?, ?, ?, ?, ?, ?)''', (order_id, name, address, state, country, city, poste))
    conn.commit()
    cur.execute(''' SELECT id from addresses order by id DESC LIMIT 1 ''')
    address_id = cur.fetchone()[0]
    cur.close()
    conn.close()


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM addresses WHERE id = ?', (address_id,))
    address = cur.fetchone()
    final_address = {
        "id": address[0],
        "order_id": address[1],
        "recipient_name": address[2],
        "address": address[3],
        "state": address[4],
        "country": address[5],
        "city": address[6],
        "postal_code": address[7],
        }
    conn.close()

    return jsonify(final_address), 201


@app.route('/address/<int:id>', methods=['GET'])
def get_address_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM addresses WHERE id = ?', (id,))
    address = cur.fetchone()
    final_address = {
            "id": address[0],
            "order_id": address[1],
            "recipient_name": address[2],
            "address": address[3],
            "state": address[4],
            "country": address[5],
            "city": address[6],
            "postal_code": address[7],
        }
    conn.close()
    if address is None:
        return '', 404
    return jsonify(final_address), 200


@app.route('/address/<int:id>', methods=['PUT'])
def update_address_by_id(id):
    order_id = request.form.get('order_id')
    name = request.form.get('recipient_name')
    address = request.form.get('address')
    state = request.form.get('state')
    country = request.form.get('country')
    city = request.form.get('city')
    poste = request.form.get('postal_code')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' UPDATE addresses SET order_id = ?, recipient_name = ?, address = ?, state = ?, country = ?, city = ?, postal_code = ? WHERE id = ? ''', (order_id, name, address, state, country, city, poste, id,))
    conn.commit()
    c.close()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * FROM addresses WHERE id = ? ''', (id,))
    address = c.fetchone()
    final_back = {
        "id": address[0],
        "order_id": address[1],
        "recipient_name": address[2],
        "address": address[3],
        "state": address[4],
        "country": address[5],
        "city": address[6],
        "postal_code": address[7],
    }
    conn.close()

    return jsonify(final_back), 200


@app.route('/address/<int:id>', methods=['DELETE'])
def delete_address_by_id(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' DELETE FROM payments WHERE id = ? ''', (id,))
    conn.commit()
    c.close()
    conn.close()
    return jsonify({"shipping address id": id}), 200




# ADMINLOG
@app.route('/adminLog', methods=['GET'])
def list_admin_log():
    logging.debug("Received 'GET' request for /admin logs")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM adminLogs WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    logs = cur.fetchall()
    final_logs = []
    
    # Convert the database records to a list of dictionaries for the response
    for log in logs:
        user_name = get_user_name_by_id(log[1])
        final_logs.append({
            "id": log[0],
            "user_id": log[1],
            "user_name": user_name,
            "action": log[2],
            "action_date": log[3],
            "ip_address": log[4],
        })

    total_count = len(DATABASE.GET_ALL_ADMIN_LOGS)
    response = jsonify({ "data": final_logs })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'addresses 0-{len(final_logs)}/{total_count}'
    return response, 200


@app.route('/adminLog', methods=['POST'])
def create_admin_log():
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    ip = request.form.get('ip_address')


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' INSERT INTO adminLogs (user_id, action, ip_address) VALUES (?, ?, ?)''', (user_id, action, ip))
    conn.commit()
    cur.execute(''' SELECT id from adminLogs order by id DESC LIMIT 1 ''')
    Log_id = cur.fetchone()[0]
    cur.close()
    conn.close()


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM adminLogs WHERE id = ?', (Log_id,))
    adminLog = cur.fetchone()
    final_address = {
        "id": adminLog[0],
        "user_id": adminLog[1],
        "action": adminLog[2],
        "ip_address": adminLog[4],
        }
    conn.close()

    return jsonify(final_address), 201


@app.route('/adminLog/<int:id>', methods=['GET'])
def get_admin_log_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM adminLogs WHERE id = ?', (id,))
    adminLog = cur.fetchone()
    user_name = get_user_name_by_id(adminLog[1])
    final_adminLog = {
        "id": adminLog[0],
        "user_id": adminLog[1],
        "user_name": user_name,
        "action": adminLog[2],
        "action_date": adminLog[3],
        "ip_address": adminLog[4],
        }
    conn.close()
    if adminLog is None:
        return '', 404
    return jsonify(final_adminLog), 200


@app.route('/adminLog/<int:id>', methods=['PUT'])
def update_admin_log_by_id(id):
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    ip = request.form.get('ip_address')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' UPDATE adminLogs SET user_id = ?, action = ?, ip_address = ? WHERE id = ? ''', (user_id, action, ip, id))
    conn.commit()
    c.close()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * FROM adminLogs WHERE id = ? ''', (id,))
    address = c.fetchone()
    final_back = {
        "id": address[0],
        "user_id": address[1],
        "action": address[2],
        "ip_address": address[4],
    }
    conn.close()

    return jsonify(final_back), 200


@app.route('/adminLog/<int:id>', methods=['DELETE'])
def delete_admin_log_by_id(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' DELETE FROM adminLogs WHERE id = ? ''', (id,))
    conn.commit()
    c.close()
    conn.close()
    return jsonify({"admin log id": id}), 200




# FEEDBACK
@app.route('/feedback', methods=['GET'])
def list_feedback():
    logging.debug("Received 'GET' request for /feedback")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM feedbacks WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    feedbacks = cur.fetchall()
    final_feedbacks = []
    
    # Convert the database records to a list of dictionaries for the response
    for feedback in feedbacks:
        final_feedbacks.append({
            "id": feedback[0],
            "customer_id": feedback[1],
            "order_id": feedback[2],
            "rating": feedback[3],
            "comment": feedback[4],
            "feedback_date": feedback[4],
        })

    total_count = len(DATABASE.GET_ALL_FEEDBACKS)
    response = jsonify({ "data": final_feedbacks })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'feedbacks 0-{len(final_feedbacks)}/{total_count}'
    return response, 200


@app.route('/feedback', methods=['POST'])
def create_feedback():
    customer_id = request.form.get('customer_id')
    order_id = request.form.get('order_id')
    rating = request.form.get('rating')
    comment_text = request.form.get('comment')


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' INSERT INTO feedbacks(customer_id, order_id, rating, comment) VALUES (?, ?, ?, ?)''', (customer_id, order_id, rating, comment_text))
    conn.commit()
    cur.execute(''' SELECT id from feedbacks order by id DESC LIMIT 1 ''')
    feedback_id = cur.fetchone()[0]
    cur.close()
    conn.close()


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM feedbacks WHERE id = ?', (feedback_id,))
    feedback = cur.fetchone()
    final_feedback = {
        "id": feedback[0],
        "customer_id": feedback[1],
        "order_id": feedback[2],
        "rating": feedback[3],
        "comment": feedback[4],
        "feedback_date": feedback[4],
        }
    conn.close()

    return jsonify(final_feedback), 201


@app.route('/feedback/<int:id>', methods=['GET'])
def get_feedback_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM feedbacks WHERE id = ?', (id,))
    feedback = cur.fetchone()
    final_feedback = {
        "id": feedback[0],
        "customer_id": feedback[1],
        "order_id": feedback[2],
        "rating": feedback[3],
        "comment": feedback[4],
        "feedback_date": feedback[4],  
        "ans": "",
    }
    conn.close()
    if feedback is None:
        return '', 404
    return jsonify(final_feedback), 200


@app.route('/feedback/<int:id>', methods=['PUT'])
def update_feedback_by_id(id):
    # customer_id = request.form.get('customer_id')
    # order_id = request.form.get('order_id')
    # rating = request.form.get('rating')
    # comment_text = request.form.get('comment')
    feedback_id = request.form.get('id')
    ans = request.form.get('ans')

    conn = get_db_connection()
    c = conn.cursor()
    # c.execute(''' UPDATE feedbacks SET customer_id = ?, order_id = ?, rating = ?, comment WHERE id = ? ''', (customer_id, order_id, rating, comment_text, id,))
    c.execute("INSERT INTO adminAns(admin_name, feedback_id, ans) VALUES (?, ?, ?)", ("John Doe", feedback_id, ans))
    conn.commit()
    c.close()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * FROM feedbacks WHERE id = ? ''', (id,))
    feedback = c.fetchone()
    final_feedback = {
        "id": feedback[0],
        "customer_id": feedback[1],
        "order_id": feedback[2],
        "rating": feedback[3],
        "comment": feedback[4],
        "feedback_date": feedback[4],
    }
    conn.close()

    return jsonify(final_feedback), 200


@app.route('/feedback/<int:id>', methods=['DELETE'])
def delete_feedback_by_id(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' DELETE FROM feedbacks WHERE id = ? ''', (id,))
    conn.commit()
    c.close()
    conn.close()
    return jsonify({"feedback id": id}), 200




# ORDERS
@app.route('/order', methods=['GET'])
def list_order():
    logging.debug("Received 'GET' request for /orders")
    range_str = request.args.get('range')
    sort_str = request.args.get('sort')
    filter_str = request.args.get('filter')
    
    # Initialize variables for pagination, sorting, and filtering
    start = 0
    end = 10 # Default end value, adjust as needed
    field = 'id' # Default sort field
    order = 'ASC' # Default sort order
    filters = {} # Corrected: Initialize filters as an empty dictionary
    
    if range_str:
        range_list = json.loads(range_str)
        start = range_list[0]
        end = range_list[1]
    
    if sort_str:
        sort_list = json.loads(sort_str)
        field = sort_list[0]
        order = sort_list[1]
    
    if filter_str:
        filters = json.loads(filter_str)
    
    conn = sqlite3.connect('db/DATAbase.db')
    cur = conn.cursor()

    # Corrected: Start with a base query that always evaluates to true
    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    # Apply filters to the query
    for key, value in filters.items():
        query += f" AND {key} LIKE '%{value}%'"

    # Add the ORDER BY clause
    query += f" ORDER BY {field} {order}"

    # Add the LIMIT and OFFSET clauses
    query += f" LIMIT ? OFFSET ?"
    params.append(end - start + 1) # Limit
    params.append(start) # Offset

    # Execute the query with the params
    print(query, params)
    cur.execute(query, params)

    # Fetch the customers from the database
    orders = cur.fetchall()
    final_orders = []
    
    # Convert the database records to a list of dictionaries for the response
    for order in orders:
        final_orders.append({
            "id": order[0],
            "customer_id": order[1],
            "order_date": order[2],
            "total_amount": order[3],
            "status": order[4],
        })

    total_count = len(DATABASE.GET_ALL_ORDERS)
    response = jsonify({ "data": final_orders })
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] =f'addresses 0-{len(final_orders)}/{total_count}'
    return response, 200


@app.route('/order', methods=['POST'])
def create_order():
    customer_id = request.form.get('customer_id')
    amount = request.form.get('total_amount')
    status = request.form.get('status')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?) ''', (customer_id, amount, status))
    conn.commit()

    c.execute(''' SELECT * FROM orders ORDER BY id DESC LIMIT 1 ''')
    order_id = ''
    result = c.fetchone()
    if result is not None:
        order_id = result[0]
    c.close()
    conn.close()


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cur.fetchone()
    final_order = {
        "id": order[0],
        "customer_id": order[1],
        # "order_date": order[2],
        "total_amount": order[3],
        "status": order[4],
        }
    conn.close()

    return jsonify(final_order), 201


@app.route('/order/<int:id>', methods=['GET'])
def get_order_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM orders WHERE id = ?', (id,))
    order = cur.fetchone()
    final_order = {
        "id": order[0],
        "customer_id": order[1],
        # "order_date": order[2],
        "total_amount": order[3],
        "status": order[4],
        }
    conn.close()
    if order is None:
        return '', 404
    return jsonify(final_order), 200


@app.route('/order/<int:id>', methods=['PUT'])
def update_order_by_id(id):
    customer_id = request.form.get('customer_id')
    amount = request.form.get('total_amount')
    status = request.form.get('status')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' UPDATE orders SET customer_id = ?, total_amount = ?, status = ? WHERE id = ? ''', (customer_id, amount, status, id,))
    conn.commit()
    c.close()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' SELECT * FROM orders WHERE id = ? ''', (id,))
    order = c.fetchone()
    final_order = {
        "id": order[0],
        "customer_id": order[1],
        "order_date": order[2],
        "total_amount": order[3],
        "status": order[4],
    }
    conn.close()

    return jsonify(final_order), 200


@app.route('/order/<int:id>', methods=['DELETE'])
def delete_order_by_id(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(''' DELETE FROM orders WHERE id = ? ''', (id,))
    conn.commit()
    c.close()
    conn.close()
    return jsonify({"order id": id}), 200


# ------------------------ ADMIN END ------------------------------------





# check if client exicsts or not
def user_exists(phone, username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM customers WHERE phone = ? AND name = ?''', (phone, username))
        # Fetch the result
    result = cur.fetchone()
        # Close the cursor and connection
    cur.close()
    conn.close()
        # If a result is found, the user exists; otherwise, they do not
    return result

@app.route('/Login', methods = ['POST'])
def handle_login():
    name = request.json["name"]
    phone = request.json["phone"]
    customer = user_exists(phone, name)
    if customer:
        with open(f'static/customer_img/{customer[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return jsonify({
            'message': 'User exists',
            'id': customer[0],
            'name': customer[1],
            'email': customer[2],
            'phone': customer[3],
            'date': customer[4],
            'image': "data:image/png;base64," + encoded_string,
        }), 200
    else:
        return jsonify({'message': 'User does not exist'}), 400


def generate_unique_filename_png(directory):
    while True:
            # Generate a random UUID and convert it to a string
        random_name = str(uuid.uuid4())
            # Append the current timestamp to the UUID
        file_name = f'{random_name}_{int(time.time())}'
        #     # Create the full file path
        file_path = os.path.join(directory, f'{file_name}.png')
            # Check if the file already exists
        if not os.path.exists(file_path):
            return file_name

@app.route('/SignUp', methods=['POST'])
def handle_signup():
        # Extract the customer details from the request data
    name = request.json["name"]
    email = request.json["email"]
    phone = request.json["phone"]
    base64_image = request.json.get("image") # Use .get() to avoid KeyError if "image" is not provided

        # Establish connection
    conn = get_db_connection()
    cur = conn.cursor()

    if user_exists(phone, name):
        return jsonify({'message': 'User already exists'}), 400

        # Decode base64 image
    if base64_image:
        image_data = base64.b64decode(base64_image.split(',')[1])
        image = Image.open(io.BytesIO(image_data))

            # Convert to PNG if not already
        if image.format != 'PNG':
            image = image.convert('RGBA')

            # this, returs a string that combined wiht current time stamp  
        unique_filename = generate_unique_filename_png('static/customer_img')

            # Save image to folder
        image_path = os.path.join('static/customer_img', f'{unique_filename}.png')
        image.save(image_path)

            # Insert the new customer into the database with the image path
        cur.execute('''
            INSERT INTO customers (name, email, phone, image) VALUES (?, ?, ?, ?)''', (name, email, phone, f'{unique_filename}.png'))
    else:
            # Insert the new customer into the database without the image path
        cur.execute('''
            INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)''', (name, email, phone))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/cart', methods=['POST'])
def handle_Add_to_cart():
    product_id = request.json["product_id"]
    quantity = request.json["quantity"]
    customer_id = request.json["customer_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    SELECT * FROM cart WHERE customer_id = ? AND product_id = ?''', (customer_id, product_id))
    existing_cart_item = cur.fetchone()

    if existing_cart_item:
        cur.execute('''
            UPDATE cart
            SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
            WHERE customer_id = ? AND product_id = ?''', (quantity, customer_id, product_id))
    else:
        cur.execute('''
            INSERT INTO cart (customer_id, product_id, quantity, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)''', (customer_id, product_id, quantity))

    conn.commit()

    return jsonify({'message': 'Item added to cart'}), 200


@app.route('/cart/<int:C_ID>', methods=['GET'])
def get_Shopping_cart_items_by_user_id(C_ID):
    cart_id = C_ID
    if not cart_id:
        return jsonify({"error": "C_ID is required"}), 400

    final_cate = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT 
                cart.cart_id,
                cart.quantity, 
                cart.created_at, 
                cart.updated_at, 
                products.id, 
                products.name, 
                products.price, 
                products.image
            FROM cart 
            JOIN products ON cart.product_id = products.id 
            WHERE cart.customer_id = ?''', (cart_id,))
    CARTS = cur.fetchall()
    for cart in CARTS:
        try: 
            with open(f'static/product_images/{cart[7]}', 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            # Handle the case where the image file is not found
            encoded_string = None
        except Exception as e:
            # Handle other exceptions
            print(f"Error opening image file: {e}")
            encoded_string = None
        
        cart_items = {
            "cart_id": cart[0],
            "quantity": cart[1],
            "created_at": cart[2],
            "updated_at": cart[3],
            "product_id": cart[4],
            "product_name": cart[5],
            "product_price": cart[6],
            "product_image": encoded_string,
        }
        final_cate.append(cart_items)

    cur.close()
    conn.close()

    return jsonify(final_cate), 200


@app.route('/cart', methods=['PUT'])
def update_product_quantity():
    cart_id = request.json["cartId"]
    new_quantity =  request.json["quantity"]

    if not cart_id:
        return jsonify({"error": "itemId is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Update the quantity of the cart item
    try:
        if new_quantity == 0:
            # If the new quantity is 0, delete the record
            cur.execute('DELETE FROM cart WHERE cart_id = ?', (cart_id,))
            conn.commit()
            return jsonify({"message": "Item removed from cart"}), 200
        else:
            cur.execute('''
            UPDATE cart
            SET quantity = ?
            WHERE cart_id = ?''', (new_quantity, cart_id))
            conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({"message": "Cart item quantity updated"}), 200

# check out order
@app.route('/COOSF', methods=["POST", "PUT"])
def check_out_add_order():
    customer_id = request.json["customerId"]
    reciepient_name = request.json["customerName"]
    status = request.json["status"]
    address_lineOne = request.json["address"]
    city = request.json["city"]
    state = request.json["state"]
    postal_code = request.json["postalCode"]
    country = request.json["country"]
    response = get_items_quantity_totalCount_totalPrice_customerId(customer_id)
    items = response.get_json()["items"]
    total_amount = response.get_json()["total_price"]


    if request.method == "POST":
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' INSERT INTO orders (customer_id, total_amount, status) VALUES 
                        (?, ?, ?) ''', (customer_id, total_amount, status))
        conn.commit()
        cur.close()
        conn.close()


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' INSERT INTO addresses (order_id, recipient_name, address, state, country, city, postal_code) VALUES 
                            (?, ?, ?, ?, ?, ? ,?) ''', (order_id, reciepient_name, address_lineOne, state, country, city, postal_code))
        conn.commit()


        cur.execute(''' SELECT id FROM orders ORDER BY id DESC LIMIT 1 ''')
        order_id = cur.fetchone()[0]
        cur.close()
        conn.close()


        conn = get_db_connection()
        cur = conn.cursor()
        for item in items:
            cur.execute(''' INSERT INTO orderDetails (order_id, product_id, quantity, unit_price) VALUES 
                                (?, ?, ?, ?)''', (order_id, 
                                                item["product_id"], 
                                                item["quantity"], 
                                                item["product_price"],
                                                ))
            conn.commit()
        cur.close()
        conn.close()



        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' INSERT INTO payments (order_id, payment_method, amount) VALUES 
                        (?, ?, ?) ''', (order_id, 'Online', total_amount))
        conn.commit()
        cur.close()
        conn.close()


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' DELETE FROM cart where customer_id = ? ''', (customer_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "ordered successfully", "order_id": order_id}), 200          
    
    if request.method == "PUT": 

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' INSERT INTO orders (customer_id, total_amount, status) VALUES 
                        (?, ?, ?) ''', (customer_id, total_amount, status))
        conn.commit()
        cur.close()
        conn.close()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' INSERT INTO addresses (order_id, recipient_name, address, state, country, city, postal_code) VALUES 
                            (?, ?, ?, ?, ?, ?, ?) ''', (order_id, reciepient_name, address_lineOne, state, country, city, postal_code))
        conn.commit()


        cur.execute(''' SELECT id FROM orders ORDER BY id DESC LIMIT 1 ''')
        order_id = cur.fetchone()[0]
        cur.close()
        conn.close()


        conn = get_db_connection()
        cur = conn.cursor()
        for item in items:
            cur.execute(''' INSERT INTO orderDetails (order_id, product_id, quantity, unit_price) VALUES 
                                (?, ?, ?, ?)''', (order_id, 
                                                item["product_id"], 
                                                item["quantity"], 
                                                item["product_price"],
                                                ))
            conn.commit()
        cur.close()
        conn.close()


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' INSERT INTO payments (order_id, payment_method, amount) VALUES 
                        (?, ?, ?) ''', (order_id, 'in_location', total_amount))
        conn.commit()
        cur.close()
        conn.close()


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(''' DELETE FROM cart where customer_id = ? ''', (customer_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        
        return jsonify({"message": "price will be in location"}), 200   


@app.route('/Invoice/<int:id>', methods=["GET"])
def get_invoice(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' SELECT * FROM orders WHERE id = ? ''', (id,))
    order = cur.fetchone()
    if order:
        finall = [{
            "total_amount": order["total_amount"],
            "date": order["order_date"],
        }]
        return jsonify(finall), 200
    else:
        return jsonify({"error": "Order not found"}), 404

# rate and comment
@app.route('/RaC', methods=["POST"])
def rate_and_comment():
    customer_id = request.json["customerId"]
    rating = request.json["rate"]
    comment = request.json["comment"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' SELECT id FROM orders ORDER BY id DESC LIMIT 1 ''')
    order_id = cur.fetchone()[0]
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' INSERT INTO feedbacks (customer_id, order_id, rating, comment) VALUES 
                (?, ?, ?, ?) ''', (customer_id, order_id, rating, comment))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify("success"), 200


@app.route('/updateCustomer/<id>', methods=["POST"])
def update_customer_profile(id):
    email = request.json["email"]
    phone = request.json["phone"]
    name = request.json["name"]
    base64_img = request.json.get("image")

    if base64_img:
        image_data = base64.b64decode(base64_img.split(',')[1]) # Remove the data URI scheme if present
        image = Image.open(io.BytesIO(image_data))

        # Convert to PNG if not already
        if image.format != 'PNG':
            image = image.convert('RGBA')


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f''' SELECT * FROM customers where id = {id} ''')
        filenameRmv = cur.fetchone()[5]
        print(filenameRmv)
        conn.commit()
        cur.close()
        conn.close()

        # Delete the previes file
        rmv_path = os.path.join('static/customer_img', filenameRmv)
        if filenameRmv != 'blank-img.png':
            os.remove(rmv_path)

        # Generate a unique filename for the image
        unique_filename = generate_unique_filename_png('static/customer_img')
        image_path = os.path.join('static/customer_img', f'{unique_filename}.png')
        image.save(image_path)

        # Update the customer's image path in the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE customers SET name = ?, email = ?, phone = ?, image = ? where id = ?', (name, email, phone, f'{unique_filename}.png', id))
        conn.commit()
        cur.close()
        conn.close()
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE customers SET name = ?, email = ?, phone = ? where id = ?', (name, email, phone, id))
        conn.commit()
        conn.close()
        cur.close()

    return jsonify('customer successfully updated')


@app.route('/customerProfile/<id>', methods=['GET'])
def get_customer_by_id_profile(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers WHERE id = ?', (id,))
    customer = cur.fetchone()
    with open(f'static/customer_img/{customer[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    final_customer = {
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "registration_date": customer[4],
            "image": "data:image;base64," + encoded_string,
        }
    conn.close()
    
    return jsonify(final_customer), 200


@app.route('/ordersIngageCustomer/<id>', methods=["GET"])
def ordersIngageCustomer(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' SELECT * from orders WHERE (status = 'pending' OR status = 'sent') AND customer_id = ? GROUP BY id ''', (id,))
    orders = cur.fetchall()
    finall_orders = []
    for order in orders: 
        finall_orders.append({
            "id": order["id"],
            "customer_id": order["customer_id"],
            "date": order["order_date"],
            "total_amount": order["total_amount"],
            "status": order["status"],
        })

    return jsonify(finall_orders), 200


@app.route('/ordersHistoryCustomer/<id>', methods=["GET"])
def ordersHistoryCustomer(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' SELECT * from orders WHERE (status = 'completed' OR status = 'canceled') AND customer_id = ? ''', (id,))
    orders = cur.fetchall()
    finall_orders = []
    for order in orders: 
        finall_orders.append({
            "id": order["id"],
            "customer_id": order["customer_id"],
            "date": order["order_date"],
            "total_amount": order["total_amount"],
            "status": order["status"],
        })

    return jsonify(finall_orders), 200


@app.route('/updatedStatusOrder/<id>', methods=["GET"])
def updatedStatusOrder(id):
    conn = sqlite3.Connection('db/DATAbase.db')
    cur = conn.cursor()
    cur.execute(f''' SELECT id, order_id, new_status
                    FROM order_status_history
                    WHERE new_status != old_status AND customer_id = {id} ORDER BY changed_at DESC LIMIT 1 ''')
    sendItems = cur.fetchone()
    if sendItems:
        OSH_id = sendItems[0]
        order_id = sendItems[1]
        new_status = sendItems[2]
    else:
        return jsonify({"message": "there is not any data for this customer !!"}), 200

    return jsonify({"id": OSH_id, "order_id": order_id, "status": new_status, "message": "ok"}), 200


@app.route('/FeedAnsR/<id>', methods=["GET"])
def ans_feedback_customer(id):
    conn = sqlite3.Connection('db/DATAbase.db')
    c = conn.cursor()
    c.execute(''' SELECT *, feedbacks.comment, feedbacks.feedback_date, feedbacks.rating  FROM adminAns JOIN feedbacks ON feedbacks.id = adminAns.feedback_id WHERE feedbacks.customer_id = ? ''', (id,))
    columns = c.fetchall()
    finall = []
    if columns:
        for column in columns:
            finall.append({
                "admin_name": column[1],
                "answer": column[3],
                "ans_date": column[4],
                "feedback": column[9],
                "cus_date": column[10],
                "rating": column[8],
            })
    
    return jsonify(finall), 200







# @app.after_request
# def add_header(response):
#     # Add a custom header to the response
#     response.headers['X-Custom-Header'] = 'Custom Value'
#     return response

@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404   

if __name__ == '__main__':
    app.run(debug=True)