from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

# app.py

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/producter')
client = MongoClient(host=host)
db = client.get_default_database()
products = db.products
comments = db.comments

app = Flask(__name__)


@app.route('/')
def products_index():
    """homepage"""
    return render_template('products_index.html', products=products.find()) 

@app.route('/products/new')
def products_new():
    """Create a new product."""
    return render_template('products_new.html', product={}, title='New product')

@app.route('/products', methods=['POST'])
def products_submit():
    """Submit a new product."""
    product = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'created_at': datetime.now()
    }
    print(product)
    product_id = products.insert_one(product).inserted_id
    return redirect(url_for('products_show', product_id=product_id))

@app.route('/products/<product_id>')
def products_show(product_id):
    """Show a single product."""
    product = products.find_one({'_id': ObjectId(product_id)})
    product_comments = comments.find({'product_id': ObjectId(product_id)})
    return render_template('products_show.html', product=product, comments=product_comments)

@app.route('/products/<product_id>/edit')
def products_edit(product_id):
    """Show the edit form for a product."""
    product = products.find_one({'_id': ObjectId(product_id)})
    return render_template('products_edit.html', product=product, title='Edit product')

@app.route('/products/<product_id>', methods=['POST'])
def products_update(product_id):
    """Submit an edited product."""
    updated_product = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': request.form.get('videos').split()
    }
    products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': updated_product})
    return redirect(url_for('products_show', product_id=product_id))

# app.py
...
@app.route('/products/<product_id>/delete', methods=['POST'])
def products_delete(product_id):
    """Delete one product."""
    products.delete_one({'_id': ObjectId(product_id)})
    return redirect(url_for('products_index'))

@app.route('/products/comments', methods=['POST'])
def comments_new():
    """Submit a new comment."""
    comment = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'product_id': ObjectId(request.form.get('product_id'))
    }
    print(comment)
    return redirect(url_for('products_show', product_id=request.form.get('product_id')))

@app.route('/products/comments/<comment_id>', methods=['POST'])
def comments_delete(comment_id):
    """Action to delete a comment."""
    comment = comments.find_one({'_id': ObjectId(comment_id)})
    comments.delete_one({'_id': ObjectId(comment_id)})
    return redirect(url_for('products_show', product_id=comment.get('product_id')))

if __name__ == '__main__':
  app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT', 5000))
