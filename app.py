from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from passlib.context import CryptContext
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from routes import *

app = Flask(__name__)
CORS(app)  # Allow frontend to access API

# Secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # using XAMPP
    database="charity_db"
)

cursor = db.cursor()
print("✅ Database Connected Successfully!")

# ✅ 1. User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get("Name")
    email = data.get("Email")
    password = data.get("Password")
    role = data.get("role", "user")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        cursor.execute("INSERT INTO Users (Name, Email, Password,role) VALUES (%s, %s, %s,%s)",
                       (name, email, hashed_password,role))
        db.commit()
        return jsonify({"message": "User registered successfully!"}), 200

    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists!"}), 400

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500

# ✅ 2. User Login
from werkzeug.security import check_password_hash

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("Email")
    password = data.get("Password")

    # Fetch the user by email
    cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
    user = cursor.fetchone()

    # Check if user exists and password matches the hashed password
    if user and check_password_hash(user[3], password):  # user[3] is the hashed password column
        return jsonify({"message": "Login successful!", "user_id": user[0]}), 200
    else:
        return jsonify({"error": "Invalid credentials!"}), 401

# ✅ 3. Make a Donation
@app.route("/donate", methods=["POST"])
def donate():
    data = request.json
    current_date = datetime.now().date()
    try:
        # set default values for missing fields
        charity_id = data.get("charity_id", 1)  # default to charity_id = 1
        payment_status = data.get("payment_status", "completed")  # default status

        cursor.execute("""
                INSERT INTO Donations (user_id, charity_id, amount, date, payment_status)
                VALUES (%s, %s, %s, %s, %s)
            """, (data["user_id"], charity_id, data["amount"], current_date, payment_status))
        db.commit()
        return jsonify({"message": "Donation successful!"})
    except Exception as e:
        print("❌ Donation Error:", e)
        return jsonify({"error": "Donation failed!"}), 500

# ✅ 4. Get Donation History
@app.route("/donations/<int:user_id>", methods=["GET"])
def get_donations(user_id):
    cursor.execute("SELECT donation_id, amount, date FROM Donations WHERE user_id = %s", (user_id,))
    donations = cursor.fetchall()
    return jsonify([{"donation_id": row[0], "amount": row[1], "date": row[2]} for row in donations])

# @app.route("/transaction/<int:donation_id>", methods=["GET"])
# def get_transaction(donation_id):
#     cursor.execute(
#         "SELECT payment_method, transaction_status, transaction_date FROM Transaction WHERE donation_id = %s",
#         (donation_id,)
#     )
#     transaction = cursor.fetchone()
#     if transaction:
#         return jsonify({
#             "payment_method": transaction[0],
#             "transaction_status": transaction[1],
#             "transaction_date": str(transaction[2])
#         })
#     else:
#         return jsonify({"message": "No transaction found"}), 404



@app.route("/fund-usage/<int:charity_id>", methods=["GET"])
def get_fund_usage(charity_id):
    cursor.execute("SELECT amount_spent, purpose, report, report_date FROM Fund_usage WHERE charity_id = %s", (charity_id,))
    usage = cursor.fetchall()
    return jsonify([
        {
            "amount_spent": row[0],
            "purpose": row[1],
            "report": row[2],
            "report_date": row[3]
        } for row in usage
    ])


# ✅ Run the app
if __name__ == "__main__":
    app.run(debug=True)
