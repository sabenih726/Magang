import pandas as pd
import os
import hashlib
import re
from datetime import datetime

# File paths
USERS_FILE = "data/users.csv"
LOGIN_HISTORY_FILE = "data/login_history.csv"

# ----------- User Data Management -----------

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        return pd.DataFrame(columns=["username", "password", "full_name", "email", "role", "department"])

def save_users(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(USERS_FILE, index=False)

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Simple regex-based email validation"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def authenticate_user(username, password):
    """Authenticate a user using hashed password"""
    users_df = load_users()
    if username in users_df['username'].values:
        user_row = users_df[users_df['username'] == username].iloc[0]
        if user_row['password'] == hash_password(password):
            return user_row.drop(labels='password').to_dict()
    return None

def add_user(user_data):
    """Add a new user with hashed password"""
    users_df = load_users()
    if user_data['username'] in users_df['username'].values:
        return False, "Username already exists"
    if not validate_email(user_data["email"]):
        return False, "Invalid email format"

    user_data["password"] = hash_password(user_data["password"])
    new_user_df = pd.DataFrame([user_data])
    users_df = pd.concat([users_df, new_user_df], ignore_index=True)
    save_users(users_df)
    return True, "User added successfully"

def delete_user(username):
    users_df = load_users()
    if username in users_df['username'].values:
        users_df = users_df[users_df['username'] != username]
        save_users(users_df)
        return True
    return False

# ----------- Login Activity Logging -----------

def log_user_activity(username, action):
    """Log login or logout activity"""
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = pd.DataFrame([{
        "username": username,
        "action": action,
        "timestamp": timestamp
    }])

    if os.path.exists(LOGIN_HISTORY_FILE):
        df = pd.read_csv(LOGIN_HISTORY_FILE)
        df = pd.concat([df, log_entry], ignore_index=True)
    else:
        df = log_entry

    df.to_csv(LOGIN_HISTORY_FILE, index=False)

def get_login_history():
    """Retrieve login/logout history"""
    if os.path.exists(LOGIN_HISTORY_FILE):
        return pd.read_csv(LOGIN_HISTORY_FILE)
    else:
        return pd.DataFrame(columns=["username", "action", "timestamp"])
