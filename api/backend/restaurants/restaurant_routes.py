from flask import Blueprint, request, current_app
from backend.db_connection import get_cursor

restaurants = Blueprint("restaurants", __name__, url_prefix="/restaurants")


@restaurants.route("/restaurants", methods=["GET", "PUT"])
def restaurant(rest_id):
    if request.method == "GET":
        with get_cursor() as cursor:
            cursor.execute(
                """
                select name, email, phone, priceId, formalityId
                from restaurants
                where restaurant_id = %s
                """,
                rest_id,
            )
            data = cursor.fetchall()
            if data:
                rest_data = data[0]

                def get_rest_info(pref_table):
                    with get_cursor() as inner_cursor:
                        if pref_table == "Diet_Category":
                            inner_cursor.execute(
                                f"""
                                select dc.id, dc.name, dc.description
                                from Diet_Category dc join Rest_Diet rd on dc.id = rd.dietId
                                join Restaurant r on rd.restId = r.id
                                where r.id = %s
                                """,
                                rest_id,
                            )
                        elif pref_table == "Cuisine":
                            inner_cursor.execute(
                                f"""
                                select c.id, c.name, c.description
                                from Cuisine c join Rest_Cuisine rc on c.id = rc.cuisineId
                                join Restaurant r on rc.restId = r.id
                                where r.id = %s
                                """,
                                rest_id,
                            )
                        elif pref_table == "Price":
                            inner_cursor.execute(
                                f"""
                                select p.id, p.rating, p.description
                                from Price p join Restaurant r on p.id = r.priceId
                                where r.id = %s
                                """,
                                rest_id,
                            )
                        elif pref_table == "Formality":
                            inner_cursor.execute(
                                f"""
                                select f.id, f.name, f.description
                                from Formality f join Restaurant r on f.id = r.formalityId
                                where r.id = %s
                                """,
                                rest_id,
                            )
                        elif pref_table == "Location":
                            inner_cursor.execute(
                                f"""
                                select l.longitude, l.latitude
                                from Location l join Restaurant r on l.restId = r.id
                                where r.id = %s
                                """,
                                rest_id,
                            )
                        elif pref_table == "Operating_Hours":
                            inner_cursor.execute(
                                f"""
                                select o.dayOfWeek, o.startTime, o.endTime
                                from Operating_Hours o join Restaurant r on o.restId = r.id
                                where r.id = %s
                                """,
                                rest_id,
                            )
                        rests = inner_cursor.fetchall()
                        return rests

                rest_data["diet"] = get_rest_info("Diet_Category")
                rest_data["cuisine"] = get_rest_info("Cuisine")
                rest_data["prices"] = get_rest_info("Price")
                rest_data["formality"] = get_rest_info("Formality")
                rest_data["location"] = get_rest_info("Location")
                rest_data["operating_hours"] = get_rest_info("Operating_Hours")

                return rest_data
            else:
                return "Invalid restaurants id", 400

    elif request.method == "PUT":
        data = request.json

        current_app.logger.info(data["email"])

        with get_cursor() as cursor:
            cursor.execute(
                """
                update Restaurant
                set id=%(id)s, name=%(name)s, email=%(email)s, 
                    phone=%(phone)s, priceId=%(priceId)s, formalityId=%(formalityId)s
                where id=%(id)s
                """,
                {
                    **data,
                    "id": rest_id,
                },
            )


@restaurants.route("/<int:restaurantID>/reviews", methods=["GET"])
def get_restaurant_reviews(restaurantID):
    try:
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    r.name AS restaurant_name,
                    rr.custId,
                    rr.seqNum,
                    rr.comment AS review_text,
                    re.recommendation,
                    rr.dietScore,
                    rr.priceScore,
                    rr.cuisineScore,
                    rr.formalityScore,
                    rr.locationScore
                FROM 
                    Restaurant r
                JOIN 
                    Recommendation re ON r.id = re.restId
                JOIN 
                    Recommendation_Review rr ON re.custId = rr.custId AND re.seqNum = rr.seqNum
                WHERE 
                    r.id = %s
                """,
                (restaurantID,),
            )
            records = cursor.fetchall()

        if records:
            return jsonify(records), 200
        else:
            return jsonify({"error": "No reviews found for this restaurant"}), 404

    except Exception as e:
        current_app.logger.error(f"Error fetching reviews: {e}")
        return jsonify({"error": "An error occurred while fetching reviews"}), 500
