from flask import Blueprint, request
from backend.db_connection import get_cursor

customers = Blueprint("customers", __name__, url_prefix="/customers")


# Get customer detail for customer with particular <cust_id>
# Includes basic info like name and email as well as preference data
@customers.route("/<cust_id>", methods=["GET", "PUT"])
def customer_info(cust_id):
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


@customers.route("/<cust_id>/recommendations", methods=["POST"])
def customer_recommendation(cust_id):
    with get_cursor() as cursor:
        formality_price_query = """
        select r.id
        from Restaurant r
        where (
            not exists (select 1 from Cust_Price where custId = %(custId)s)
                or
            r.priceId in
            (select cp.priceId
            from Customer c
                    join Cust_Price cp on c.id = cp.custId
            where c.id = %(custId)s)
        )
        and (
            not exists (select 1 from Cust_Formality where custId = %(custId)s)
                or
            r.formalityId in
            (select cf.formalityId
            from Customer c
                    join Cust_Formality cf on c.id = cf.custId
            where c.id = %(custId)s)
        )
        """

        cursor.execute(
            "select exists(select * from Cust_Cuisine where custId = %s) as hasPref", cust_id
        )
        has_cuisine_pref = cursor.fetchone()
        cuisine_query = ""
        if has_cuisine_pref["hasPref"]:
            cuisine_query = """
            intersect distinct
            select rc.restId
            from Customer c
                    join Cust_Cuisine cc on c.id = cc.custId
                    join Rest_Cuisine rc on cc.cuisineId = rc.cuisineId
            where c.id = %(custId)s
            """

        cursor.execute(
            "select exists(select * from Cust_Diet where custId = %s) as hasPref", cust_id
        )
        has_diet_pref = cursor.fetchone()
        diet_query = ""
        if has_diet_pref["hasPref"]:
            diet_query = """
            intersect distinct
            select restId
            from Rest_Diet
            where dietId in (
                with recursive cte (id) as (
                    select cd.dietId
                    from Customer c
                        join Cust_Diet cd on c.id = cd.custId
                    where c.id = %(custId)s
                    union distinct
                    select dc.id
                    from Diet_Category dc
                        join cte on dc.parentCategory = cte.id
                )
                select * from cte
            )
            group by restId
            """

        cursor.execute(
            f"""
            select id
            from ({formality_price_query + cuisine_query + diet_query}) as Matching_Restaurants
            order by rand()
            limit 3
            """,
            {"custId": cust_id},
        )
        restaurant_recs = cursor.fetchall()

        if restaurant_recs:
            next_seq_num = 1
            cursor.execute(
                "select max(seqNum) as curSeqNum from Recommendation where custId = %s group by custId",
                cust_id,
            )
            cur_seq_num = cursor.fetchone()
            if cur_seq_num:
                next_seq_num = cur_seq_num["curSeqNum"] + 1

            formatted_recs = []

            values = ""
            for i, rec in enumerate(restaurant_recs):
                formatted_recs.append({"seqNum": next_seq_num + i, "restId": rec["id"]})
                values += f"({cust_id}, {next_seq_num + i}, {rec['id']}, 'Generated based on profile preferences'),"
            values = values.rstrip(",")

            cursor.execute(
                "insert into Recommendation (custId, seqNum, restId, explanation) values " + values
            )

            return formatted_recs
        else:
            return []


@customers.route("/<cust_id>/recommendations/<seq_num>", methods=["PUT"])
def accept_recommendation(cust_id, seq_num):
    accepted = request.json["accepted"]
    with get_cursor() as cursor:
        cursor.execute(
            "update Recommendation set accepted = %(accepted)s where custId = %(custId)s and seqNum = %(seqNum)s",
            {
                "accepted": accepted,
                "custId": cust_id,
                "seqNum": seq_num,
            },
        )
        return ""
