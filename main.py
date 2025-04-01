from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from utils.scrape import Tracker
from utils.send_email import Email
from utils.loggers import read_cfg
import utils.loggers as lg

app = Flask(__name__)

def save_to_database(db_connection, stocks):
    try:
        cursor = db_connection.cursor()
        
        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stock_name VARCHAR(100),
                quantity INT,
                price FLOAT,
                date DATE
            );
        """)

        # Insert the stock data into the table
        for stock, details in stocks.items():
            query = """
            INSERT INTO stocks (stock_name, quantity, price, date)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (stock, details['quantity'], details['price'], datetime.now().strftime('%Y-%m-%d')))
        
        # Commit the transaction
        db_connection.commit()
        cursor.close()
        
        print("✅ Stock data saved to the database successfully!")
    except Exception as e:
        print(f"❌ Failed to save data to the database: {e}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_stock', methods=['POST'])
def add_stock():
    try:
        print("🔍 Receiving stock data from frontend...")  # Debug message
        config, db_connection = read_cfg()
        
        if not db_connection:
            print("❌ Database connection failed.")
            return jsonify({"error": "Database connection failed."})
        
        # Receive JSON data
        data = request.json
        print(f"📥 Received Data: {data}")
        
        stock_name = data['stock_name']
        quantity = int(data['quantity'])
        price = float(data['price'])
        
        new_stock = {stock_name: {"quantity": quantity, "price": price}}
        
        # Save stock to JSON file
        try:
            with open('utils/data/new_stocks.json', 'r+') as file:
                data = json.load(file)
                data.update(new_stock)
                file.seek(0)
                json.dump(data, file, indent=4)
            print("✅ Stock saved to JSON file.")
        except Exception as e:
            print(f"❌ Failed to save stock to JSON file: {e}")
        
        # Save to database
        try:
            if db_connection:
                save_to_database(db_connection, new_stock)
                db_connection.close()
                print("✅ Stock saved to database.")
            else:
                print("❌ Database connection not established.")
        except Exception as e:
            print(f"❌ Failed to save to database: {e}")
            return jsonify({"error": f"Failed to save to database: {e}"})
        
        return jsonify({"message": "Stock added successfully!"})
    
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return jsonify({"error": str(e)})


@app.route('/view_stocks')
def view_stocks():
    try:
        config, db_connection = read_cfg()
        cursor = db_connection.cursor()
        
        # Fetch all stocks from the database
        cursor.execute("SELECT stock_name, quantity, price, date FROM stocks;")
        stocks = cursor.fetchall()
        db_connection.close()

        # Format stocks data to be returned as JSON
        stocks_list = []
        for name, quantity, price, date in stocks:
            stocks_list.append({
                "name": name,
                "quantity": quantity,
                "price": price,
                "date": date.strftime('%Y-%m-%d') if date else "No Date Found"
            })

        print("📦 Data Sent to Frontend: ", stocks_list)
        return jsonify(stocks_list)
        
    except Exception as e:
        print(f"❌ Error fetching stocks: {e}")
        return jsonify({"error": str(e)})

@app.route('/remove_stock', methods=['DELETE'])
def remove_stock():
    try:
        stock_name = request.args.get('stock_name')
        if not stock_name:
            return jsonify({"error": "Stock name is required!"}), 400
        
        config, db_connection = read_cfg()
        cursor = db_connection.cursor()
        
        query = "DELETE FROM stocks WHERE stock_name = %s"
        cursor.execute(query, (stock_name,))
        db_connection.commit()
        
        cursor.close()
        db_connection.close()
        
        print(f"✅ Stock '{stock_name}' removed successfully.")
        return jsonify({"message": f"Stock '{stock_name}' removed successfully!"})
    
    except Exception as e:
        print(f"❌ Failed to remove stock: {e}")
        return jsonify({"error": str(e)})

@app.route('/edit_stock', methods=['POST'])
def edit_stock():
    try:
        data = request.json
        original_name = data['original_name']
        new_name = data['new_name']
        new_quantity = int(data['new_quantity'])
        new_price = float(data['new_price'])
        new_date = data['new_date']

        config, db_connection = read_cfg()
        cursor = db_connection.cursor()

        # Update the stock in the database
        query = """
        UPDATE stocks 
        SET stock_name = %s, quantity = %s, price = %s, date = %s 
        WHERE stock_name = %s
        """
        cursor.execute(query, (new_name, new_quantity, new_price, new_date, original_name))
        db_connection.commit()
        
        cursor.close()
        db_connection.close()

        print(f"✅ Stock '{original_name}' updated successfully.")
        return jsonify({"message": f"Stock '{original_name}' updated successfully!"})
    
    except Exception as e:
        print(f"❌ Failed to update stock: {e}")
        return jsonify({"error": str(e)})



@app.route('/test_db')
def test_db():
    try:
        config, db_connection = read_cfg()
        
        if db_connection:
            return "✅ Database connection successful!"
        else:
            return "❌ Database connection failed."
    except Exception as e:
        return f"❌ Error: {e}"
    
if __name__ == "__main__":
    app.run(debug=True)
