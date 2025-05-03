import streamlit as st
import requests
import re
import os
import random
import base64

# ✅ Function to encode background image

def get_base64_of_bin_file(bin_file_path):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg_from_local(image_path):
    bin_str = get_base64_of_bin_file(image_path)
    css_code = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

# ✅ Background folder setup
background_folder = "Assets"  # Make sure this folder exists
images = os.listdir(background_folder)
selected_image = 'BG.jpg'

# API Base URL
BASE_URL = "http://127.0.0.1:5000"

# Session State for Logged-in User
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""

# Sidebar Navigation
st.sidebar.title("Navigation")
if st.session_state["user_id"] is None:
    page = st.sidebar.radio("Go to", ["Register", "Login"])
else:
    page = st.sidebar.radio("Go to", ["Dashboard", "Donate & History", "Logout","Fund Usage"])

# ✅ Background image based on page
if page == "Login":
    selected_image = "Login_bg.jpg"
elif page == "Register":
    selected_image = "Register_bg.jpg"
elif page == "Donate & History":
    selected_image = "Donation_bg.jpg"
elif page == "Dashboard":
    selected_image = "dashboard_bg.jpg"
else:
    selected_image = "BG.jpg"  # default image

# ✅ Set background using selected image
image_path = os.path.join("Assets", selected_image)
set_bg_from_local(image_path)

# ✅ Register Page
if page == "Register":
    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    st.title("User Registration")
    name = st.text_input("Name")
    email = st.text_input("Email")
    if email and not is_valid_email(email):
        st.error("❌ Invalid Email Format")
    password = st.text_input("Password", type="password")
    if password and len(password) < 6:
        st.error("❌ Password should be at least 6 characters long")

    if st.button("Register"):
        if is_valid_email(email) and len(password) >= 6:
            try:
                response = requests.post(f"{BASE_URL}/register",
                                         json={"Name": name, "Email": email, "Password": password, "role": "user"})
                if response.status_code == 200:
                    st.success(response.json().get("message", "Registration Successful!"))
                else:
                    st.error(response.json().get("error", "❌ Registration failed!"))
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Network error: {e}")
        else:
            st.error("❌ Fix the errors above before registering!")




# ✅ Login Page
elif page == "Login":
    st.title("User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(f"{BASE_URL}/login", json={"Email": email, "Password": password})
        if response.status_code == 200:
            st.success(response.json()["message"])
            st.session_state["user_id"] = response.json()["user_id"]
        else:
            st.error(f"Error: {response.json()['error']}")


# ✅ Dashboard Page
elif page == "Dashboard":
    st.title("Dashboard")
    st.subheader(f"Welcome, {st.session_state['user_name']} 😊")
    st.write("Explore the features using the menu!")

# ✅ Donate & History Page
elif page == "Donate & History":
    if st.session_state["user_id"] is None:
        st.warning("Please log in first!")
    else:
        st.title("Make a Donation")
        charity_options = {
            "Child Education": 1,
            "Health Support": 2,
            "Women Empowerment": 3
        }
        selected_charity = st.selectbox("Choose Charity", list(charity_options.keys()))
        charity_id = charity_options[selected_charity]

        amount = st.number_input("Enter amount", min_value=1)

        if st.button("Donate"):
            payload = {
                "user_id": st.session_state["user_id"],
                "charity_id": charity_id,
                "amount": amount,
                "payment_status": "completed"
            }
            response = requests.post(f"{BASE_URL}/donate", json=payload)
            try:
                st.success(response.json()["message"])
            except requests.exceptions.JSONDecodeError:
                st.error("❌ Donation failed! Server error.")
                st.write("Raw response:", response.text)

        st.title("Donation History")
        response = requests.get(f"{BASE_URL}/donations/{st.session_state['user_id']}")
        history = response.json()
        for entry in history:
            st.write(f"Amount: {entry['amount']} | Date: {entry['date']}")

        # 🎯 Fetch and display Transaction History
        # st.title("Transaction History")
        # for entry in history:
        #     donation_id = entry["donation_id"]  # New line: get donation_id from donation history
        #
        #     transaction_response = requests.get(f"{BASE_URL}/transaction/{donation_id}")
        #     if transaction_response.status_code == 200:
        #         transaction = transaction_response.json()
        #         st.write(
        #             f"Donation ID: {donation_id} | Payment Method: {transaction['payment_method']} | Status: {transaction['transaction_status']} | Date: {transaction['transaction_date']}")
        #     else:
        #         st.write(f"No transaction details found for Donation ID {donation_id}.")

elif page == "Add Fund Usage":
    st.title("Add Fund Usage Report")

    charity_id = st.number_input("Charity ID", min_value=1, step=1)
    amount_spent = st.number_input("Amount Spent", min_value=0.0)
    purpose = st.text_area("Purpose of Fund Usage")
    report = st.text_area("Detailed Report")
    report_date = st.date_input("Report Date")

    if st.button("Submit Fund Usage"):
        response = requests.post(f"{BASE_URL}/fund_usage", json={
            "charity_id": charity_id,
            "amount_spent": float(amount_spent),
            "purpose": purpose,
            "report": report,
            "report_date": str(report_date)
        })

        if response.status_code == 200:
            st.success("✅ Fund usage data submitted successfully")
        else:
            st.error("❌ Failed to submit fund usage data")


elif page == "Fund Usage":
    st.title("Fund Usage Reports")

    charity_id = st.number_input("Enter Charity ID", min_value=1, step=1)

    if st.button("Get Fund Usage"):
        response = requests.get(f"{BASE_URL}/fund_usage/{charity_id}")

        if response.status_code == 200:
            data = response.json()
            if data:
                for entry in data:
                    st.subheader(f"Amount Spent: ₹{entry['amount_spent']}")
                    st.write(f"Purpose: {entry['purpose']}")
                    st.write(f"Report: {entry['report']}")
                    st.write(f"Report Date: {entry['report_date']}")
                    st.markdown("---")
            else:
                st.info("No fund usage data found for this charity.")
        else:
            st.error("Failed to fetch data.")


# ✅ Logout
elif page == "Logout":
    st.session_state["user_id"] = None
    st.session_state["user_name"] = ""
    st.success("Logged out successfully!")
