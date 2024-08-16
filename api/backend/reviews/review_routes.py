from flask import Blueprint, request, current_app
from backend.db_connection import get_cursor

# Blueprint for review routes
reviews = Blueprint("reviews", __name__, url_prefix="/reviews")


# Route to handle adding or deleting a review based on customer ID and sequence number
@reviews.route("/<cust_id>/<seq_num>", methods=["POST", "DELETE"])
def reviews_info(cust_id, seq_num):
    if request.method == "POST":
        data = request.json  # Get the JSON data from the request
        with get_cursor() as cursor:
            # Insert a new review into the Recommendation_Review table
            cursor.execute(
                f"""
                insert into Recommendation_Review (custId, seqNum, dietScore, priceScore, cuisineScore, formalityScore, locationScore, comment)
                values ({cust_id}, {seq_num}, {data["dietScore"] or "null"},
                    {data["priceScore"] or "null"}, {data["cuisineScore"] or "null"},
                    {data["formalityScore"] or "null"}, {data["locationScore"] or "null"},
                    '{data["comment"]}')
                """
            )
            return ""  # Return an empty response

    elif request.method == "DELETE":
        sql = (
            """
            delete from Recommendation_Review where custId = """
            + str(cust_id)
            + """ and seqNum = """
            + str(seq_num)
            + """
        """
        )
        with get_cursor() as cursor:
            cursor.execute(sql)
            return ""
    # Log the data for debugging purposes
    current_app.logger.info(data)
