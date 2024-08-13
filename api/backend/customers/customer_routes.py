from flask import Blueprint


from backend.db_connection import get_cursor

customers = Blueprint("customers", __name__, url_prefix="/customers")


# Get customer detail for customer with particular <cust_id>
# Includes basic info like name and email as well as preference data
@customers.route("/<cust_id>", methods=["GET"])
def get_customers():
    cursor = get_cursor()
    query = "Select * from Customer"
    cursor.execute(query)
    data = cursor.fetch_all()
    response = make_response(data)
    response.status_code = 200
    response.mimetime = "application/json"
    return response
