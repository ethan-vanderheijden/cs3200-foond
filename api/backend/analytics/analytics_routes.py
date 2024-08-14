from flask import Blueprint, jsonify
from backend.db_connection import get_cursor

analytics = Blueprint("analytics", __name__, url_prefix="/analytics")


# Route to get restaurants with the lowest average in a single category
@analytics.route("/<category>", methods=["GET"])
def get_lowest_average(category):
    if category not in ["price", "cuisine", "formality"]:
        return jsonify({"error": "Invalid category"}), 400

    with get_cursor() as cursor:
        cursor.execute(
            f"""
            select re.name, avg(rr.{category}Score) as avg_score
            from Restaurant re
            join Recommendation r on re.id = r.restId
            join Recommendation_Review rr on r.custId = rr.custId AND r.seqNum = rr.seqNum
            where rr.{category}Score is not null
            group by re.name
            order by avg_score asc
            limit 10
            """
        )
        results = cursor.fetchall()

    if results:
        return jsonify(results)
    else:
        return jsonify({"error": "No data found"}), 404
