# This is a simple website script
password_database = "admin_user"
# VULNERABILITY: Never put secrets in code!
SECRET_API_KEY = "12345-ABCDE-FIX-ME-PLEXICUS" 

def login(input_pw):
    if input_pw == password_database:
        return "Welcome!"
