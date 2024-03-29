from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
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
# logging.getLogger('flask_cors').level = logging.DEBUG
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/DATAbase.db'
# db = SQLAlchemy(app)




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
        })
    return jsonify({"items": finall, "quantity": quantity, "item_count": len(items), "total_price": total_price}), 200


@app.route('/Pcategories', methods=["GET"])
def get_parent_categories():
    category_list = []
    for category in DATABASE.GET_PARENT_CATEGORIES:
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


# --------------------------------------------------------------------------------------------------------------------


def get_db_connection():
    conn = sqlite3.connect('db/DATAbase.db')
    conn.row_factory = sqlite3.Row
    return conn


# CUSTOMER
# Create a new customer
def create_customer(name, email, phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO customers (name, email, phone_number) VALUES (?, ?, ?)", (name, email, phone,))
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
            "phone_number": customer[3],
            "registration_date": customer[4],
            "image": encoded_string,
        }
    conn.close()
    return final_customer

# Update a customer
def update_customer(customer_id, name, email, phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE customers SET name = ?, email = ?, phone_number = ? WHERE id = ?', (name, email, phone, customer_id))
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
    with open(f'static/category_symbol/{category[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    final_category = {
            "id": category[0],
            "name": category[1],
            "description": category[2],
            "PCI": category[3],
            # "created_at": category[4],
            "image": encoded_string,
        }
    conn.close()
    return final_category

# Update a category
def update_category(name, description, parent_category_id, image, category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE categories SET name = ?, description = ?, parent_category_id = ?, image = ? WHERE id = ?', (name, description, parent_category_id, image, category_id,))
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
    cur.execute(''' SELECT product_id FROM products ORDER BY product_id DESC LIMIT 1 ''')
    product_id = cur.fetchone()[0]
    conn.close()
    return product_id

# # Get a product by ID
# def get_product(product_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
#     product = cur.fetchone()
#     with open(f'static/product_images/{product[5]}', 'rb') as image_file:
#             encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#     final_products = {
#             "product_id": product[0],
#             "name": product[1],
#             "description": product[2],
#             "price": product[3],
#             "category_id": product[4],
#             "image": encoded_string, # The base64 encoded image
#         }
#     conn.close()
#     if product is None:
#         return '', 404
#     return jsonify(final_products), 200

# Update a product
def update_product(product_id, name, description, price, category_id, image):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE products SET name = ?, description = ?, price = ?, category_id = ?, image = ? WHERE product_id = ?', (name, description, price, category_id, image, product_id))
    conn.commit()
    conn.close()
    # return get_product(product_id)

# Delete a product
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()

# # Get all products
# def get_all_products(limit):
# # def get_all_customers():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute(f'SELECT * FROM products LIMIT {limit}')
#     # cur.execute(f'SELECT * FROM products')
#     products = cur.fetchall()
#     final_products = []
#     for product in products:
#         final_products.append({
#             "product_id": product[0],
#             "name": product[1],
#             "description": product[2],
#             "price": product[3],
#             "category_id": product[4],
#             "image": product[5],
#         })
#     conn.close()
#     return final_products








@app.route('/', methods=['GET'])
def test_backEnd():
    return jsonify('ok')


# @app.route('/category/<int:id>')
# def get_category_by_id(id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute(f"SELECT * from categories where id = ?", (id,))
#     category = cur.fetchone()
#     final_cate = {
#         "category_id": category[0],
#         "name": category[1],
#         "description": category[2],
#         "parent_category_id": category[3],
#         "created_at": category[4],
#         "image": category[5],
#     }
#     conn.close()
#     return jsonify(final_cate), 200




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

    query = f'SELECT * FROM customers ORDER BY {field} {order} LIMIT ? OFFSET ?'
    params = (end - start + 1, start)
    
    # Apply filters to the query
    for key, value in filters.items():
        query += f' AND {key} = ?'
        params += (value)
    
    cur.execute(query, params)
    
    # Fetch the customers from the database
    customers = cur.fetchall()
    
    # Convert the database records to a list of dictionaries for the response
    final_customers = []
    for customer in customers:
        with open(f'static/customer_img/{customer[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        final_customers.append({
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "registration_date": customer[4],
            "image": encoded_string,
        })

    total_count = len(DATABASE.GET_ALL_CUSTOMERS)
    response = jsonify(final_customers)
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = f'customers 0-{len(final_customers)}/{total_count}'
    return response, 200


@app.route('/customer', methods=['POST'])
def add_customer():
    name = request.json['name']
    phone = request.json['phone']
    email = request.json['email']
    customer_id = create_customer(name, email, phone)
    return jsonify(get_customer(customer_id)), 201


@app.route('/customer/<id>', methods=['GET'])
def get_customer_by_id(id):
    customer = get_customer(id)
    if customer is None:
        return '', 404
    return jsonify(customer), 200


@app.route('/customer/<int:id>', methods=['PUT'])
def update_customer_by_id(id):
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    updated = update_customer(id, name, email, phone)
    return jsonify(updated), 200


@app.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer_by_id(id):
    delete_customer(id)
    return jsonify({"customer_id":id}), 200
    



# category
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
    filters = {} # Default empty filter
    
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

    # Construct the query based on the field
    if field == 'PCI':
        query = f'SELECT * FROM categories ORDER BY parent_category_id {order} LIMIT ? OFFSET ?'
    else:
        query = f'SELECT * FROM categories ORDER BY {field} {order} LIMIT ? OFFSET ?'
    
    params = [end - start + 1, start]
    
    # Apply filters to the query
    for key, value in filters.items():
        query += f' AND {key} = ?'
        params += (value)
    
    try:
        cur.execute(query, params)
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

    cur.execute(query, params)
    
    # Fetch the customers from the database
    categories = cur.fetchall()
    
    # Convert the database records to a list of dictionaries for the response
    final_categories = []
    for category in categories:
        with open(f'static/category_symbol/{category[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        final_categories.append({
            "id": category[0],
            "name": category[1],
            "description": category[2],
            "parent_category_id": category[3],
            "created_at": category[4],
            "image": encoded_string,
        })

    total_count = len(DATABASE.GET_ALL_CATEGORIES)
    # total_count = 123
    response = jsonify(final_categories)
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = f'customers 0-{len(final_categories)}/{total_count}'
    return response, 200

# (name, description, parent_category_id, image, category_id)

@app.route('/category', methods=['POST'])
def add_category():
    name = request.json['name']
    description = request.json['description']
    parent_category_id = request.json['PCI']
    base64_image = request.json['image']

    image_data = base64.b64decode(base64_image.split(',')[1])
    image = Image.open(io.BytesIO(image_data))

        # Convert to PNG if not already
    if image.format != 'PNG':
        image = image.convert('RGBA')

        # Save image to folder
    image_path = os.path.join('static/category_symbol', f'{name}.png')
    image.save(image_path)

    category_id = create_category(name, description, parent_category_id, image, category_id)
    return jsonify(get_category(category_id)), 201


@app.route('/category/<int:id>', methods=['GET'])
def get_category_by_id(id):
    category = get_category(id)
    if category is None:
        return '', 404
    return jsonify(category), 200


@app.route('/category/<int:id>', methods=['PUT'])
def update_category_by_id(id):
    name = request.json['name']
    description = request.json['description']
    parent_category_id = request.json['PCI']
    base64_image = request.json['image']

    # Check if the base64_image string is in the expected format
    # if ',' in base64_image:
    #     # Split the base64 string and decode the second part (the actual image data)
    #     try:
    #         image_data = base64.b64decode(base64_image.split(',')[1])
    #     except IndexError:
    #         # Handle the case where the base64_image string does not contain a comma
    #         # or the split operation fails for some reason
    #         return jsonify({"error": "Invalid image format"}), 400
    # else:
    #     # If the base64_image string does not contain a comma,
    #     # try to decode it directly (assuming it's a raw base64 string without a data URI scheme)
    #     try:
    #         image_data = base64.b64decode(base64_image)
    #     except base64.binascii.Error:
    #         # Handle the case where the base64_image string is not valid base64
    #         return jsonify({"error": "Invalid base64 image data"}), 400
    # image = Image.open(io.BytesIO(image_data))


    # Convert to PNG if not already
    if image.format != 'PNG':
        image = image.convert('RGBA')

    # Save image to folder
    image_path = os.path.join('static/category_symbol', f'{name}.png')
    image.save(image_path)

    # Assuming update_category function is defined elsewhere
    updated = update_category(name, description, parent_category_id, f'{name}.png', id)
    return jsonify(updated), 200


@app.route('/category/<int:id>', methods=['DELETE'])
def delete_category_by_id(id):
    delete_category(id)
    return jsonify({"category_id": id}), 200
  





# PRODUCT
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    category_id = request.json['category_id']
    image = request.json['image']
    product_id = create_customer(name, description, price, category_id, image)
    # return jsonify(get_product(product_id)), 201

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
    product = cur.fetchone()
    with open(f'static/product_images/{product[5]}', 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    final_products = {
            "product_id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category_id": product[4],
            "image": encoded_string, # The base64 encoded image
        }
    conn.close()
    if product is None:
        return '', 404
    return jsonify(final_products), 200

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



# check if client exicsts or not
def user_exists(phone, username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM customers WHERE phone_number = ? AND name = ?''', (phone, username))
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
            INSERT INTO customers (name, email, phone_number, image) VALUES (?, ?, ?, ?)''', (name, email, phone, f'{unique_filename}.png'))
    else:
            # Insert the new customer into the database without the image path
        cur.execute('''
            INSERT INTO customers (name, email, phone_number) VALUES (?, ?, ?)''', (name, email, phone))

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
                products.product_id, 
                products.name, 
                products.price, 
                products.image
            FROM cart 
            JOIN products ON cart.product_id = products.product_id 
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
        cur.execute(''' INSERT INTO addresses (recipient_name, address, state, country, city, postal_code) VALUES 
                            (?, ?, ?, ?, ?, ?) ''', (reciepient_name, address_lineOne, state, country, city, postal_code))
        conn.commit()


        cur.execute(''' SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1 ''')
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
        cur.execute(''' INSERT INTO addresses (recipient_name, address, state, country, city, postal_code) VALUES 
                            (?, ?, ?, ?, ?, ?) ''', (reciepient_name, address_lineOne, state, country, city, postal_code))
        conn.commit()


        cur.execute(''' SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1 ''')
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
    cur.execute(''' SELECT * FROM orders WHERE order_id = ? ''', (id,))
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
    cur.execute(''' SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1 ''')
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
        os.remove(rmv_path)

        # Generate a unique filename for the image
        unique_filename = generate_unique_filename_png('static/customer_img')
        image_path = os.path.join('static/customer_img', f'{unique_filename}.png')
        image.save(image_path)

        # Update the customer's image path in the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE customers SET name = ?, email = ?, phone_number = ?, image = ? where id = ?', (name, email, phone, f'{unique_filename}.png', id))
        conn.commit()
        cur.close()
        conn.close()
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE customers SET name = ?, email = ?, phone_number = ? where id = ?', (name, email, phone, id))
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
            "phone_number": customer[3],
            "registration_date": customer[4],
            "image": "data:image/png;base64," + encoded_string,
        }
    conn.close()
    
    return jsonify(final_customer), 200

@app.route('/ordersIngageCustomer/<id>', methods=["GET"])
def ordersIngageCustomer(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' SELECT * from orders WHERE (status = 'pending' OR status = 'sent' OR status = 'completed') AND customer_id = ? GROUP BY order_id ''', (id,))
    orders = cur.fetchall()
    finall_orders = []
    for order in orders: 
        finall_orders.append({
            "id": order["order_id"],
            "customer_id": order["customer_id"],
            "date": order["order_date"],
            "total_amount": order["total_amount"],
            "status": order["status"],
        })

    return jsonify(finall_orders), 200




@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404   

if __name__ == '__main__':
    app.run(debug=True)