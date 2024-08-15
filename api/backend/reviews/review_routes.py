from flask import Blueprint, request, current_app
from backend.db_connection import get_cursor

reviews = Blueprint("reviews", __name__, url_prefix="/reviews")


@reviews.route("/<cust_id>/<seq_num>", methods=["POST", "DELETE"])
def reviews_info(cust_id, seq_num):
    if request.method == "POST":
        data = request.json
        with get_cursor() as cursor:
            cursor.execute(
                f"""
                insert into Recommendation_Review (custId, seqNum, dietScore, priceScore, cuisineScore, formalityScore, locationScore, comment)
                values ({cust_id}, {seq_num}, {data["dietScore"] or "null"},
                    {data["priceScore"] or "null"}, {data["cuisineScore"] or "null"},
                    {data["formalityScore"] or "null"}, {data["locationScore"] or "null"},
                    '{data["comment"]}')
                """
            )
            return ""
    elif request.method == "DELETE":
        sql = """
            delete from Recommendation_Review where custId = """ + str(cust_id) + """ and seqNum = """ + str(seq_num) + """
        """
        with get_cursor() as cursor:
            cursor.execute(sql)
            return ""

    current_app.logger.info(data)
