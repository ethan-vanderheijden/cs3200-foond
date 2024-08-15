from urllib import request
from flask import Blueprint
from backend.db_connection import get_cursor

groups = Blueprint("groups", __name__, url_prefix="/groups")

'''
def update_profile_data():
    requests.put(
        "http://api:4000/customers/" + str(USER_ID),
        json={
            "firstName": st.session_state.first,
            "middleInitial": st.session_state.mi,
            "lastName": st.session_state.last,
            "email": st.session_state.email,
            "longitude": st.session_state.longitude,
            "latitude": st.session_state.latitude,
            "pricePreferences": st.session_state.prices,
            "cuisinePreferences": st.session_state.cuisines,
            "dietPreferences": st.session_state.diets,
            "formalityPreferences": st.session_state.formalities,
        },
    )

@st.cache_data
def get_available_preferences():
    return requests.get("http://api:4000/groups").json()
'''

@groups.route("/<groupID>/reccomendations", methods=["GET", "POST"])
def get_available_preferences(groupId):
    if request.method == "GET":
        group_get(groupId)
    elif request.method == "POST":
        group_post(groupId)
    else:
        print("unknown group ")

def group_get(groupId):
    with get_cursor() as cursor:
        data = {
            "diets": {},
            "formalities": {},
            "prices": {},
            "cuisines": {},
        }

        def list_to_dict(list_data):
            return {
                item["id"]: {key: item[key] for key in item if key != "id"} for item in list_data
            }

        sql = f"""
        SELECT cui.name AS name
        FROM Dining_Group dg
        JOIN Cust_Group cg ON dg.id = cg.custId
        JOIN Customer c ON c.id = cg.custId
        JOIN Cust_Cuisine cc ON cc.custId = c.id
        JOIN Cuisine cui ON cui.id cc.custId
        WHERE dg.id = {groupId}
        GROUP BY cui.id, cui.name
        ORDER BY COUNT(c.id)
        LIMIT 1;
        """

        cursor.execute("select id, name, description from Diet_Category")
        data["diets"] = list_to_dict(cursor.fetchall())
        cursor.execute("select id, name, description from Formality")
        data["formalities"] = list_to_dict(cursor.fetchall())
        cursor.execute("select id, rating, description from Price")
        data["prices"] = list_to_dict(cursor.fetchall())
        cursor.execute("select id, name, description from Cuisine")
        data["cuisines"] = list_to_dict(cursor.fetchall())

        return data

def group_post(group_id):
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
                "id": group_id,
            },
        )