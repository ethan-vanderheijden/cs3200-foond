from flask import Blueprint, request, current_app
from backend.db_connection import get_cursor

customers = Blueprint("customers", __name__, url_prefix="/customers")


# Get customer detail for customer with particular <cust_id>
# Includes basic info like name and email as well as preference data
@customers.route("/<cust_id>", methods=["GET", "PUT"])
def customer(cust_id):
    if request.method == "GET":
        with get_cursor() as cursor:
            cursor.execute(
                """
                select firstName, middleInitial, lastName, email, longitude, latitude
                from Customer
                where id = %s
                """,
                cust_id,
            )
            data = cursor.fetchall()
            if data:
                cust_data = data[0]

                # Helper method for joining Customer with a preference-related table
                def get_cust_pref(pref_table_name, short_name=None):
                    if not short_name:
                        short_name = pref_table_name

                    with get_cursor() as inner_cursor:
                        inner_cursor.execute(
                            f"""
                            select id
                            from Cust_{short_name} a
                            join {pref_table_name} b on a.{short_name}Id = b.id
                            where a.custId = %s
                            """,
                            cust_id,
                        )
                        ids = inner_cursor.fetchall()
                        return [item["id"] for item in ids]

                cust_data["prices"] = get_cust_pref("Price")
                cust_data["formality"] = get_cust_pref("Formality")
                cust_data["cuisine"] = get_cust_pref("Cuisine")
                cust_data["diet"] = get_cust_pref("Diet_Category", "Diet")

                return cust_data
            else:
                return "Invalid user id", 400
    elif request.method == "PUT":
        data = request.json

        current_app.logger.info(data["longitude"])

        with get_cursor() as cursor:
            cursor.execute(
                """
                update Customer
                set firstName=%(firstName)s, middleInitial=%(middleInitial)s,
                    lastName=%(lastName)s, email=%(email)s,
                    longitude=%(longitude)s, latitude=%(latitude)s
                where id=%(id)s
                """,
                {
                    **data,
                    "id": cust_id,
                },
            )

        def rebuild_prefs(table_name, fields, data):
            with get_cursor() as cursor:
                cursor.execute(f"delete from {table_name} where custId = %s", cust_id)

                if data:
                    values = ""
                    for item in data:
                        values += f"({','.join(item)}),"
                    values = values.rstrip(",")

                    cursor.execute(
                        f"""
                        insert into {table_name} ({','.join(fields)})
                        values {values}
                        """
                    )

        price_values = [(cust_id, pId) for pId in data["pricePreferences"]]
        formality_values = [(cust_id, fId) for fId in data["formalityPreferences"]]
        cuisine_values = [(cust_id, cId) for cId in data["cuisinePreferences"]]
        diet_values = [(cust_id, dId) for dId in data["dietPreferences"]]

        rebuild_prefs("Cust_Price", ["custId", "priceId"], price_values)
        rebuild_prefs("Cust_Formality", ["custId", "formalityId"], formality_values)
        rebuild_prefs("Cust_Cuisine", ["custId", "cuisineId"], cuisine_values)
        rebuild_prefs("Cust_Diet", ["custId", "dietId"], diet_values)

        return ""
