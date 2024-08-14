import logging
import atexit
import os
from dotenv import load_dotenv
from flask import Flask

from backend.db_connection import init_db, cleanup_db
from backend.customers.customer_routes import customers
from backend.groups.group_routes import groups  # Import the groups blueprint

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def create_app():
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    # Set Flask configuration from environment variables
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Initialize the database
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT", 3306))  # Default to 3306 if not provided
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("MYSQL_ROOT_PASSWORD")
    db_name = os.getenv("DB_NAME")

    if not all([db_host, db_user, db_password, db_name]):
        app.logger.error("Missing required database environment variables.")
        raise ValueError("Missing required database environment variables.")

    init_db(db_host, db_port, db_user, db_password, db_name)

    def close_db():
        app.logger.info("Server stopping, closing db")
        cleanup_db()

    atexit.register(close_db)

    # Register blueprints with Flask app object
    app.register_blueprint(customers)
    app.register_blueprint(groups)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
