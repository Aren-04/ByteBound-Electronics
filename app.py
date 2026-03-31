from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from groq import Groq
import os
import traceback

app = Flask(__name__)
app.secret_key = 'ByteBound_Secret_Key_2026'

# --- DATABASE CONFIGURATION ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://db:27017/fynode_store")
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)

RAINFOREST_KEY = "1614BD84B09645E9AE75246005391601"
client = Groq(api_key="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")

# --- JINJA CUSTOM FILTERS ---
@app.template_filter('last_six')
def last_six_filter(s):
    return str(s)[-6:]

# --- AUTHENTICATION ---

@app.route('/')
def index():
    return redirect(url_for('store'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = mongo.db.users.find_one({"username": u})
        if user and check_password_hash(user['password'], p):
            session.clear()
            session['user'] = u
            session['email'] = user.get('email')
            session['role'] = user.get('role', 'customer')
            session['cart'] = {}
            return redirect(url_for('admin_dashboard') if session['role'] == 'admin' else url_for('store'))
        flash("Invalid username or password.", "danger")
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Logic to send reset email or update DB would go here
        flash("Password reset link sent to your email!", "info")
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username')
        e = request.form.get('email')
        p = request.form.get('password')
        if mongo.db.users.find_one({"username": u}):
            flash("Username already exists.", "danger")
        else:
            hashed_p = generate_password_hash(p)
            role = 'admin' if mongo.db.users.count_documents({}) == 0 else 'customer'
            mongo.db.users.insert_one({"username": u, "email": e, "password": hashed_p, "role": role})
            flash("Account created! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- STORE LOGIC ---

@app.route('/store')
def store():
    if 'user' not in session: return redirect(url_for('login'))
    query = {}
    search = request.args.get('search')
    category = request.args.get('category')
    if search:
        query['title'] = {'$regex': search, '$options': 'i'}
    if category:
        query['category'] = category
    products = list(mongo.db.products.find(query))
    cart_count = sum(session.get('cart', {}).values())
    return render_template('store.html', products=products, cart_count=cart_count)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({"response": "I didn't catch that."})

    try:
        # 1. Fetch live product data from your MongoDB
        products = list(mongo.db.products.find({}, {"_id": 0, "title": 1, "price": 1, "category": 1}))
        
        # 2. Format a compact list for the AI to read
        product_list = "\n".join([f"- {p['title']} ({p['category']}): ₹{p['price']}" for p in products])

        # 3. Enhanced System Prompt
        system_instruction = (
            "You are ByteBot, a friendly and concise electronics store assistant for ByteBound. "
            "Rules: 1. Be welcoming but straight to the point. 2. No long descriptions. "
            "3. Use ONLY the following product data to answer availability or price questions:\n"
            f"{product_list}\n"
            "If a product isn't listed, politely say we don't carry it yet."
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150 # Keeps responses short
        )

        bot_response = completion.choices[0].message.content
        return jsonify({"response": bot_response})
        
    except Exception as e:
        print("\n" + "="*20 + " CHATBOT ERROR " + "="*20)
        traceback.print_exc()
        return jsonify({"response": "I'm having a quick reboot. Try again in a second!"}), 500

@app.route('/product/<product_id>')
def product_detail(product_id):
    p = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if not p: return redirect(url_for('store'))
    suggestions = list(mongo.db.products.find({"category": p['category'], "_id": {"$ne": p['_id']}}).limit(4))
    cart_count = sum(session.get('cart', {}).values())
    return render_template('product.html', product=p, suggestions=suggestions, cart_count=cart_count)

# --- CART LOGIC ---

@app.route('/add_to_cart/<product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    session.modified = True
    return redirect(request.referrer or url_for('store'))

@app.route('/add_one/<product_id>')
def add_one(product_id):
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/remove_one/<product_id>')
def remove_one(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        cart[product_id] -= 1
        if cart[product_id] <= 0:
            cart.pop(product_id)
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        cart_data = session.get('cart', {})
        items = []
        total_price = 0
        for pid, qty in cart_data.items():
            prod = mongo.db.products.find_one({"_id": ObjectId(pid)})
            if prod:
                total_price += prod['price'] * qty
                items.append({"title": prod['title'], "qty": qty})
        order = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "display_items": items,
            "total_amount": total_price,
            "status": "Paid"
        }
        res = mongo.db.orders.insert_one(order)
        session['cart'] = {}
        return redirect(url_for('order_success', order_id=str(res.inserted_id)))

    cart_items = []
    total = 0
    for pid, qty in session.get('cart', {}).items():
        p = mongo.db.products.find_one({"_id": ObjectId(pid)})
        if p:
            total += p['price'] * qty
            cart_items.append({"product": p, "quantity": qty})
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/success/<order_id>')
def order_success(order_id):
    order = mongo.db.orders.find_one({"_id": ObjectId(order_id)})
    return render_template('success.html', order_id=order_id, name=order['name'], total=order['total_amount'])

# --- ADMIN ---

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    orders = list(mongo.db.orders.find().sort("_id", -1))
    revenue = sum(o.get('total_amount', 0) for o in orders)
    return render_template('admin_orders.html', orders=orders, revenue=revenue)

@app.route('/admin/seed')
def seed_data():
    if session.get('role') != 'admin': 
        return redirect(url_for('login'))
    
    # Mapping DummyJSON categories to your ByteBound sidebar categories
    category_map = [
        {"remote_cat": "laptops", "local_cat": "Laptops"},
        {"remote_cat": "smartphones", "local_cat": "Processors"},
        {"remote_cat": "mobile-accessories", "local_cat": "Accessories"},
        {"remote_cat": "tablets", "local_cat": "Accessories"},
        {"remote_cat": "furniture", "local_cat": "Monitors"} # Using furniture as a placeholder for Monitors if needed
    ]

    all_products = []
    
    try:
        for mapping in category_map:
            # DummyJSON endpoint: https://dummyjson.com/products/category/laptops
            url = f"https://dummyjson.com/products/category/{mapping['remote_cat']}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                for item in products:
                    all_products.append({
                        "title": item.get('title'),
                        "price": float(item.get('price', 999) * 80), # Converting USD to approx INR
                        "thumbnail": item.get('thumbnail'),
                        "category": mapping['local_cat'], 
                        "description": item.get('description', 'Premium electronics.')
                    })
            else:
                print(f"Failed to fetch {mapping['remote_cat']}: {response.status_code}")

        if all_products:
            # Wipe and Re-seed
            mongo.db.products.delete_many({})
            mongo.db.products.insert_many(all_products)
            flash(f"Successfully synced {len(all_products)} items from DummyJSON!", "success")
        else:
            flash("No products found in DummyJSON response.", "warning")

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Sync Error: {str(e)}", "danger")

    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)