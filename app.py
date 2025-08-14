from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import json
import os

app = Flask(__name__)
app.secret_key = 'smashcity_secret_key_2024'

# Sample data structure for inventory and sales
inventory_data = {
    'meat': {'name': 'Ground Beef', 'cost_per_oz': 0.31, 'stock_oz': 160, 'min_stock': 32},
    'cheese_american': {'name': 'American Cheese', 'cost_per_slice': 0.15, 'stock_slices': 80, 'min_stock': 20},
    'cheese_swiss': {'name': 'Swiss Cheese', 'cost_per_slice': 0.18, 'stock_slices': 60, 'min_stock': 15},
    'cheese_pepper_jack': {'name': 'Pepper Jack Cheese', 'cost_per_slice': 0.20, 'stock_slices': 50, 'min_stock': 15},
    'buns': {'name': 'Burger Buns', 'cost_per_unit': 0.35, 'stock_units': 100, 'min_stock': 25},
    'lettuce': {'name': 'Lettuce', 'cost_per_serving': 0.25, 'stock_servings': 50, 'min_stock': 10},
    'tomato': {'name': 'Tomatoes', 'cost_per_serving': 0.30, 'stock_servings': 40, 'min_stock': 10},
    'onions': {'name': 'Onions', 'cost_per_serving': 0.15, 'stock_servings': 60, 'min_stock': 15},
    'mushrooms': {'name': 'Mushrooms', 'cost_per_serving': 0.40, 'stock_servings': 30, 'min_stock': 8},
    'fries': {'name': 'French Fries', 'cost_per_serving': 0.50, 'stock_servings': 80, 'min_stock': 20},
    'mozz_sticks': {'name': 'Mozzarella Sticks', 'cost_per_piece': 0.45, 'stock_pieces': 60, 'min_stock': 12}
}

menu_items = {
    'single_smash': {'name': 'Single Smash Burger', 'price': 5.00, 'cost': 1.62},
    'double_smash': {'name': 'Double Smash Burger', 'price': 8.00, 'cost': 2.24},
    'triple_smash': {'name': 'Triple Smash Burger', 'price': 11.00, 'cost': 2.86},
    'swiss_mushroom': {'name': 'Swiss & Mushroom Burger', 'price': 9.50, 'cost': 2.82},
    'pizza_burger': {'name': 'Pizza Burger', 'price': 9.00, 'cost': 2.45},
    'chopped_cheese': {'name': 'Chopped Cheese Hero', 'price': 7.50, 'cost': 2.10},
    'philly_cheesesteak': {'name': 'Philly Cheesesteak Hero', 'price': 8.50, 'cost': 2.75},
    'regular_fries': {'name': 'Regular Fries', 'price': 3.50, 'cost': 0.50},
    'loaded_fries': {'name': 'Loaded Fries', 'price': 6.50, 'cost': 1.85},
    'mozz_sticks': {'name': 'Mozzarella Sticks (6pc)', 'price': 5.50, 'cost': 2.70}
}

daily_sales = []

@app.route('/')
def dashboard():
    # Calculate key metrics
    total_inventory_value = sum(
        item['stock_oz'] * item['cost_per_oz'] if 'cost_per_oz' in item else
        item['stock_slices'] * item['cost_per_slice'] if 'cost_per_slice' in item else
        item['stock_units'] * item['cost_per_unit'] if 'cost_per_unit' in item else
        item['stock_servings'] * item['cost_per_serving'] if 'cost_per_serving' in item else
        item['stock_pieces'] * item['cost_per_piece']
        for item in inventory_data.values()
    )
    
    today_sales = [sale for sale in daily_sales if sale['date'] == str(date.today())]
    today_revenue = sum(sale['total'] for sale in today_sales)
    today_cost = sum(sale['cost'] for sale in today_sales)
    today_profit = today_revenue - today_cost
    
    low_stock_items = [
        item for key, item in inventory_data.items()
        if (item.get('stock_oz', item.get('stock_slices', item.get('stock_units', item.get('stock_servings', item.get('stock_pieces', 0)))))) <= 
           item['min_stock']
    ]
    
    return render_template('dashboard.html', 
                         inventory_value=total_inventory_value,
                         today_revenue=today_revenue,
                         today_profit=today_profit,
                         low_stock_count=len(low_stock_items))

@app.route('/inventory')
def inventory():
    return render_template('inventory.html', inventory=inventory_data)

@app.route('/menu')
def menu():
    return render_template('menu.html', menu_items=menu_items)

@app.route('/sales')
def sales():
    return render_template('sales.html', sales=daily_sales, menu_items=menu_items)

@app.route('/record_sale', methods=['POST'])
def record_sale():
    item_key = request.json['item']
    quantity = int(request.json['quantity'])
    
    if item_key in menu_items:
        item = menu_items[item_key]
        total = item['price'] * quantity
        cost = item['cost'] * quantity
        
        sale = {
            'id': len(daily_sales) + 1,
            'date': str(date.today()),
            'time': datetime.now().strftime('%H:%M'),
            'item': item['name'],
            'quantity': quantity,
            'price': item['price'],
            'total': total,
            'cost': cost,
            'profit': total - cost
        }
        
        daily_sales.append(sale)
        return jsonify({'success': True, 'sale': sale})
    
    return jsonify({'success': False, 'error': 'Item not found'})

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    item_key = request.json['item']
    new_stock = float(request.json['stock'])
    
    if item_key in inventory_data:
        # Update the appropriate stock field
        if 'stock_oz' in inventory_data[item_key]:
            inventory_data[item_key]['stock_oz'] = new_stock
        elif 'stock_slices' in inventory_data[item_key]:
            inventory_data[item_key]['stock_slices'] = new_stock
        elif 'stock_units' in inventory_data[item_key]:
            inventory_data[item_key]['stock_units'] = new_stock
        elif 'stock_servings' in inventory_data[item_key]:
            inventory_data[item_key]['stock_servings'] = new_stock
        elif 'stock_pieces' in inventory_data[item_key]:
            inventory_data[item_key]['stock_pieces'] = new_stock
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Item not found'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True)
