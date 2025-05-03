from flask import Flask, request, jsonify, Blueprint
from app import app, mysql
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# User Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = generate_password_hash(data['password'])

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (Name, Email, Password) VALUES (%s, %s, %s)",
                (data['Name'], data['Email'], hashed_password))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "User registered successfully!"})


# User Login
@app.route('/login', methods=['POST'])
def user_login():
    data = request.json
    email = data['Email']
    password = data['Password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE Email = %s", [email])
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[3], password):  # Password Check
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# Make a Donation
@app.route('/donate', methods=['POST'])
def user_donate():
    data = request.json
    user_id = data['user_id']
    amount = data['amount']
    message = data['message']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO donations (user_id, amount, message) VALUES (%s, %s, %s)",
                (user_id, amount, message))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Donation successful!"})

# @app.route('/transaction/<int:donation_id>', methods=['GET'])
# def get_transaction_by_donation(donation_id):
#     try:
#         cur = mysql.connection.cursor(dictionary=True)
#         cur.execute("SELECT * FROM Transaction WHERE donation_id = %s", (donation_id,))
#         transaction = cur.fetchone()
#         cur.close()
#
#         if transaction:
#             return jsonify(transaction), 200
#         else:
#             return jsonify({"error": "Transaction not found"}), 404
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/fund_usage', methods=['POST'])
def add_fund_usage():
    try:
        data = request.json
        charity_id = data['charity_id']
        amount_spent = data['amount_spent']
        purpose = data['purpose']
        report = data['report']
        report_date = data['report_date']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Fund_usage (charity_id, amount_spent, purpose, report, report_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (charity_id, amount_spent, purpose, report, report_date))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Fund usage added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

routes = Blueprint('routes', __name__)
@app.route("/fund_usage/<int:charity_id>", methods=["GET"])
def get_fund_usage_by_charity(charity_id):
    try:
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM Fund_usage WHERE charity_id = %s", (charity_id,))
        data = cur.fetchall()
        cur.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




