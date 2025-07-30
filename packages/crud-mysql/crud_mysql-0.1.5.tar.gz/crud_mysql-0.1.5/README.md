main.py / app.py - example

from flask import Flask
from flask_cors import CORS
from crud-mysql import crud

app = Flask(__name__)

app.register_blueprint(crud)

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)

cred.json - example

{
    "user": {
        "allowd_methods": ["GET", "POST", "DELETE", "PUT"],
        "fetch_all": "true",
        "schema": {
            "name": "VARCHAR(100)",
            "email": "VARCHAR(100)",
            "encrypted_password": "VARCHAR(100)",
            "account_id": "INT",
            "is_active": "INT"
        }
    },
    "account": {
        "allowd_methods": ["GET", "POST", "DELETE"],
        "fetch_all": "false",
        "schema": {
            "name": "VARCHAR(100)",
            "subscription_type": "VARCHAR(100)",
            "root_user": "INT"
        }
    }
}