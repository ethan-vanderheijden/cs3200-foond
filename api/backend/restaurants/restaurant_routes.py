from flask import Blueprint, request, current_app
from backend.db_connection import get_cursor

import logging

logger = logging.getLogger(__name__)

restaurants = Blueprint("restaurants", __name__, url_prefix="/restaurants")


@restaurants.route("/<rest_id>", methods=["GET", "PUT"])
def restaurant(rest_id):
    if request.method == "GET":
        with get_cursor() as cursor:
            cursor.execute(
                """
                select name, email, phone
                from Restaurant
                where id = %s
                """,
                rest_id,
            )
            data = cursor.fetchall()
            if data:
                rest_data = data[0]

                cursor.execute(
                    """
                    select dc.id, dc.name, dc.description
                    from Diet_Category dc join Rest_Diet rd on dc.id = rd.dietId
                    join Restaurant r on rd.restId = r.id
                    where r.id = %s
                    """,
                    rest_id,
                )
                rest_data["diet"] = cursor.fetchall()

                cursor.execute(
                    """
                    select c.id, c.name, c.description
                    from Cuisine c join Rest_Cuisine rc on c.id = rc.cuisineId
                    join Restaurant r on rc.restId = r.id
                    where r.id = %s
                    """,
                    rest_id,
                )
                rest_data["cuisine"] = cursor.fetchall()

                cursor.execute(
                    """
                    select p.id, p.rating, p.description
                    from Price p join Restaurant r on p.id = r.priceId
                    where r.id = %s
                    """,
                    rest_id,
                )
                rest_data["price"] = cursor.fetchone()

                cursor.execute(
                    """
                    select f.id, f.name, f.description
                    from Formality f join Restaurant r on f.id = r.formalityId
                    where r.id = %s
                    """,
                    rest_id,
                )
                rest_data["formality"] = cursor.fetchone()

                cursor.execute(
                    """
                    select l.longitude, l.latitude
                    from Location l join Restaurant r on l.restId = r.id
                    where r.id = %s
                    """,
                    rest_id,
                )
                rest_data["location"] = cursor.fetchall()

                cursor.execute(
                    """
                    select o.dayOfWeek, o.startTime, o.endTime
                    from Operating_Hours o join Restaurant r on o.restId = r.id
                    where r.id = %s
                    """,
                    rest_id,
                )
                operating_hours = cursor.fetchall()
                for schedule in operating_hours:
                    start_secs = schedule["startTime"].seconds
                    hours, remainder = divmod(start_secs, 3600)
                    minutes = remainder / 60
                    schedule["startTime"] = "{:02}:{:02}".format(int(hours), int(minutes))

                    end_secs = schedule["endTime"].seconds
                    hours, remainder = divmod(end_secs, 3600)
                    minutes = remainder / 60
                    schedule["endTime"] = "{:02}:{:02}".format(int(hours), int(minutes))
                rest_data["operating_hours"] = operating_hours

                return rest_data
            else:
                return "Invalid restaurants id", 400

    elif request.method == "PUT":
        data = request.json

        #.info(data["email"])

        with get_cursor() as cursor:
            #current_app.logger.info(**data)
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

        # def rebuild_restaurant(table, fields, data):
        #     with get_cursor() as cursor:
        #         cursor.execute(f"delete from {table} where restId = %s", rest_id)
        #
        #         if data:
        #             values = ""
        #             for item in data:
        #                 values += f"{','.join(item)}, "
        #                 values = values.rstrip(",")
        #
        #                 cursor.execute(
        #                     f"""
        #                     insert into {table} ({','.join(fields)})
        #                     values {values}
        #                     """
        #                 )
        #
        # diet_values = [(rest_id, dId) for dId in data["restaurantDiet"]]
        # cuisine_values = [(rest_id, cId) for cId in data["restaurantCuisine"]]
        # loc_values = [
        #     (rest_id, longitude, latitude) for longitude, latitude in data["restaurantLocation"]
        # ]
        # oh_values = [
        #     (rest_id, dayOfWeek, startTime, endTime)
        #     for dayOfWeek, startTime, endTime in data["restaurantOH"]
        # ]
        #
        # rebuild_restaurant("Rest_Diet", ["restId", "dietId"], diet_values)
        # rebuild_restaurant("Rest_Cuisine", ["restId", "cuisineId"], cuisine_values)
        # rebuild_restaurant("Location", ["restId", "longitude", "latitude"], loc_values)
        # rebuild_restaurant(
        #     "Operating_Hours", ["restId", "dayOfWeek", "startTime", "endTime"], oh_values
        # )

        return ""


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
            return records, 200
        else:
            return {"error": "No reviews found for this restaurant"}, 404

    except Exception as e:
        current_app.logger.error(f"Error fetching reviews: {e}")
        return {"error": "An error occurred while fetching reviews"}, 500
