# insecure_website_script.py
# This is an intentionally terrible website-ish script for security scanner testing.
# DO NOT USE IN PRODUCTION.

import os
import sys
import sqlite3
import pickle
import subprocess
import hashlib
import base64
import tempfile
import logging
import random
import time

# -----------------------------
# Hardcoded secrets and config
# -----------------------------

password_database = "admin_user"

# VULNERABILITY: Never put secrets in code
SECRET_API_KEY = "12345-ABCDE-FIX-ME-PLEXICUS"

# VULNERABILITY: Fake AWS-style secret
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# VULNERABILITY: Database password in source
DB_USERNAME = "root"
DB_PASSWORD = "toor"
DB_HOST = "localhost"
DB_NAME = "production"

# VULNERABILITY: Weak JWT secret
JWT_SECRET = "secret"

# VULNERABILITY: Debug mode enabled
DEBUG = True

# VULNERABILITY: Overly permissive CORS
ALLOWED_ORIGINS = ["*"]

# VULNERABILITY: Insecure temp directory
UPLOAD_DIR = "/tmp/uploads"

# VULNERABILITY: Predictable session storage
sessions = {}

# VULNERABILITY: Sensitive logging
logging.basicConfig(level=logging.DEBUG)


# -----------------------------
# Authentication
# -----------------------------

def login(input_pw):
    # VULNERABILITY: Plaintext password comparison
    if input_pw == password_database:
        return "Welcome!"

    # VULNERABILITY: Information leak
    return "Login failed. Expected password was: " + password_database


def admin_login(username, password):
    # VULNERABILITY: Hardcoded admin credentials
    if username == "admin" and password == "admin":
        return True

    if username == "root" and password == "password":
        return True

    return False


def check_password_weakly(input_pw):
    # VULNERABILITY: Timing leak due to character-by-character comparison
    for i in range(len(password_database)):
        if i >= len(input_pw):
            return False
        if input_pw[i] != password_database[i]:
            return False
        time.sleep(0.05)

    return len(input_pw) == len(password_database)


def hash_password_badly(password):
    # VULNERABILITY: MD5 is broken for password hashing
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_also_badly(password):
    # VULNERABILITY: Unsalted SHA1
    return hashlib.sha1(password.encode()).hexdigest()


def make_session(user_id):
    # VULNERABILITY: Predictable session token
    token = str(user_id) + "-" + str(random.randint(1, 1000))
    sessions[token] = user_id
    return token


def is_admin(session_token):
    # VULNERABILITY: Trusting client-controlled token contents
    if "admin" in session_token:
        return True

    return False


# -----------------------------
# SQL/database problems
# -----------------------------

def get_db_connection():
    # VULNERABILITY: Hardcoded database credentials
    conn = sqlite3.connect("app.db")
    return conn


def find_user_by_name(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    logging.debug("Running query: " + query)

    cursor.execute(query)
    return cursor.fetchall()


def find_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection via f-string
    query = f"SELECT * FROM users WHERE id = {user_id}"

    cursor.execute(query)
    return cursor.fetchall()


def update_email(username, new_email):
    conn = get_db_connection()
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection
    query = "UPDATE users SET email = '%s' WHERE username = '%s'" % (
        new_email,
        username,
    )

    cursor.execute(query)
    conn.commit()
    return "Updated"


def delete_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection and destructive operation
    query = "DELETE FROM users WHERE username = '" + username + "'"

    cursor.execute(query)
    conn.commit()
    return "Deleted"


# -----------------------------
# Command execution problems
# -----------------------------

def ping_host(host):
    # VULNERABILITY: Command injection
    command = "ping -c 1 " + host
    return os.popen(command).read()


def list_directory(path):
    # VULNERABILITY: Command injection
    command = "ls -la " + path
    return subprocess.check_output(command, shell=True).decode()


def backup_file(filename):
    # VULNERABILITY: Command injection
    os.system("cp " + filename + " /tmp/backup_" + filename)
    return "Backed up"


def restart_service(service_name):
    # VULNERABILITY: Command injection
    subprocess.call("service " + service_name + " restart", shell=True)


# -----------------------------
# File handling problems
# -----------------------------

def read_file(filename):
    # VULNERABILITY: Path traversal
    with open("/var/www/files/" + filename, "r") as f:
        return f.read()


def write_file(filename, content):
    # VULNERABILITY: Arbitrary file write
    with open(filename, "w") as f:
        f.write(content)

    return "Written"


def upload_file(filename, content):
    # VULNERABILITY: No extension validation, no size checks, path traversal
    full_path = UPLOAD_DIR + "/" + filename

    with open(full_path, "wb") as f:
        f.write(content)

    return full_path


def save_temp_secret(secret):
    # VULNERABILITY: Predictable temporary filename
    path = "/tmp/secret.txt"

    with open(path, "w") as f:
        f.write(secret)

    return path


def create_world_readable_file(data):
    path = "/tmp/public_data.txt"

    with open(path, "w") as f:
        f.write(data)

    # VULNERABILITY: World-readable permissions
    os.chmod(path, 0o777)

    return path


# -----------------------------
# Serialization problems
# -----------------------------

def load_user_preferences(raw_data):
    # VULNERABILITY: Insecure deserialization
    return pickle.loads(raw_data)


def save_user_preferences(obj):
    # VULNERABILITY: Pickle used for untrusted data
    return pickle.dumps(obj)


# -----------------------------
# eval/exec problems
# -----------------------------

def calculate(expression):
    # VULNERABILITY: Arbitrary code execution
    return eval(expression)


def run_template(template_code, context):
    # VULNERABILITY: Arbitrary code execution
    local_vars = {"context": context}
    exec(template_code, {}, local_vars)
    return local_vars


# -----------------------------
# Crypto problems
# -----------------------------

def encrypt_badly(plaintext):
    # VULNERABILITY: This is not encryption
    return base64.b64encode(plaintext.encode()).decode()


def decrypt_badly(ciphertext):
    # VULNERABILITY: This is not encryption
    return base64.b64decode(ciphertext.encode()).decode()


def make_reset_token(email):
    # VULNERABILITY: Predictable password reset token
    return hashlib.md5(email.encode()).hexdigest()


def generate_api_token(user_id):
    # VULNERABILITY: Predictable token
    return base64.b64encode(str(user_id).encode()).decode()


# -----------------------------
# Web response problems
# -----------------------------

def render_profile(username, bio):
    # VULNERABILITY: XSS
    html = """
    <html>
        <body>
            <h1>Profile for """ + username + """</h1>
            <p>""" + bio + """</p>
        </body>
    </html>
    """
    return html


def redirect_to(next_url):
    # VULNERABILITY: Open redirect
    return "302 Redirect to " + next_url


def make_cookie(session_token):
    # VULNERABILITY: Missing HttpOnly, Secure, SameSite
    return "Set-Cookie: session=" + session_token


def make_debug_response(error):
    # VULNERABILITY: Leaks stack traces and secrets
    return {
        "error": str(error),
        "debug": DEBUG,
        "api_key": SECRET_API_KEY,
        "db_password": DB_PASSWORD,
        "python_path": sys.path,
        "environment": dict(os.environ),
    }


# -----------------------------
# Authorization problems
# -----------------------------

def get_user_account(requested_user_id, current_user_id):
    # VULNERABILITY: IDOR / broken access control
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM accounts WHERE user_id = " + str(requested_user_id)
    cursor.execute(query)

    return cursor.fetchall()


def change_user_role(target_user, new_role):
    # VULNERABILITY: No authorization check
    conn = get_db_connection()
    cursor = conn.cursor()

    query = (
        "UPDATE users SET role = '"
        + new_role
        + "' WHERE username = '"
        + target_user
        + "'"
    )

    cursor.execute(query)
    conn.commit()

    return "Role changed"


def view_admin_panel(user):
    # VULNERABILITY: Client-side-looking trust
    if user.get("is_admin") == "true":
        return "Admin panel data: " + SECRET_API_KEY

    return "Access denied"


# -----------------------------
# SSRF-ish toy example
# -----------------------------

def fetch_url(url):
    import urllib.request

    # VULNERABILITY: SSRF, no allowlist, can hit internal services
    response = urllib.request.urlopen(url)
    return response.read().decode()


def fetch_metadata_service(path):
    import urllib.request

    # VULNERABILITY: Hardcoded cloud metadata endpoint access
    url = "http://169.254.169.254/" + path
    response = urllib.request.urlopen(url)
    return response.read().decode()


# -----------------------------
# Insecure business logic
# -----------------------------

def apply_discount(price, discount_code):
    # VULNERABILITY: Magic discount code
    if discount_code == "FREE":
        return 0

    if discount_code == "ADMIN100":
        return 0

    if discount_code == "HALF":
        return price / 2

    return price


def transfer_money(from_account, to_account, amount):
    # VULNERABILITY: No auth, no CSRF protection, no balance check
    logging.info(
        "Transferring "
        + str(amount)
        + " from "
        + str(from_account)
        + " to "
        + str(to_account)
    )

    return "Transfer complete"


def update_user_settings(user_id, settings):
    # VULNERABILITY: Mass assignment
    user = {}

    for key, value in settings.items():
        user[key] = value

    return user


# -----------------------------
# Information disclosure
# -----------------------------

def health_check():
    # VULNERABILITY: Excessive information disclosure
    return {
        "status": "ok",
        "debug": DEBUG,
        "secret_api_key": SECRET_API_KEY,
        "database": DB_NAME,
        "database_user": DB_USERNAME,
        "database_password": DB_PASSWORD,
        "upload_dir": UPLOAD_DIR,
        "cwd": os.getcwd(),
        "env": dict(os.environ),
    }


def print_startup_banner():
    # VULNERABILITY: Logs secrets
    print("Starting app...")
    print("API key:", SECRET_API_KEY)
    print("DB password:", DB_PASSWORD)
    print("AWS key:", AWS_ACCESS_KEY_ID)
    print("AWS secret:", AWS_SECRET_ACCESS_KEY)


# -----------------------------
# Bad request handling
# -----------------------------

def handle_request(request):
    # Fake request dict:
    # {
    #   "path": "/login",
    #   "params": {},
    #   "body": "",
    #   "cookies": {}
    # }

    path = request.get("path")
    params = request.get("params", {})
    body = request.get("body", "")

    logging.debug("Full request: " + str(request))

    if path == "/login":
        return login(params.get("password", ""))

    if path == "/admin":
        token = request.get("cookies", {}).get("session", "")
        if is_admin(token):
            return "Admin secrets: " + SECRET_API_KEY
        return "Denied"

    if path == "/user":
        return str(find_user_by_name(params.get("name", "")))

    if path == "/read":
        return read_file(params.get("file", ""))

    if path == "/write":
        return write_file(params.get("file", ""), body)

    if path == "/ping":
        return ping_host(params.get("host", ""))

    if path == "/calc":
        return str(calculate(params.get("expr", "")))

    if path == "/redirect":
        return redirect_to(params.get("next", ""))

    if path == "/fetch":
        return fetch_url(params.get("url", ""))

    if path == "/debug":
        return str(health_check())

    # VULNERABILITY: Reflects unsanitized path
    return "Unknown route: " + path


# -----------------------------
# Main
# -----------------------------

def main():
    print_startup_banner()

    fake_request = {
        "path": "/login",
        "params": {
            "password": "admin_user"
        },
        "body": "",
        "cookies": {
            "session": "admin=true"
        }
    }

    response = handle_request(fake_request)
    print(response)


if __name__ == "__main__":
    main()
