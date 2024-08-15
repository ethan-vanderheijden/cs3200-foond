from flask import Blueprint, request, jsonify
import logging
from backend.db_connection import get_cursor

# Initialize logging
logger = logging.getLogger(__name__)

# Blueprint setup for group routes
groups = Blueprint("groups", __name__, url_prefix="/groups")


# Route to create a new group
@groups.route("/", methods=["POST"])
def create_group():
    data = request.json
    group_name = data.get("name")
    description = data.get("description")

    if not group_name:
        return jsonify({"error": "Group name is required"}), 400

    query = """
        INSERT INTO Dining_Group (name, description)
        VALUES (%s, %s)
    """
    params = (group_name, description)

    try:
        with get_cursor() as cursor:
            cursor.execute(query, params)
            insert_id = cursor.lastrowid
            logger.info(
                f"Group ({insert_id}) created with name: {group_name} and description: {description}"
            )
            return jsonify({"newId": insert_id}), 201
    except Exception as e:
        logger.error(f"Failed to create group: {str(e)}")
        return jsonify({"error": "Failed to create group", "details": str(e)}), 500


# Route to add or remove a user from a group
@groups.route("/<group_id>", methods=["PUT"])
def modify_group_members(group_id):
    data = request.json
    action = data.get("action")
    cust_id = data.get("custId")

    if not action or not cust_id:
        return jsonify({"error": "Action and customer ID are required"}), 400

    if action not in ["add", "remove"]:
        return jsonify({"error": "Invalid action"}), 400

    query = (
        """
        INSERT INTO Cust_Group (custId, groupId)
        VALUES (%s, %s)
    """
        if action == "add"
        else """
        DELETE FROM Cust_Group
        WHERE custId = %s AND groupId = %s
    """
    )
    params = (cust_id, group_id)

    try:
        with get_cursor() as cursor:
            cursor.execute(query, params)
            logger.info(f"Action '{action}' performed on user {cust_id} in group {group_id}")
            return (
                jsonify(
                    {
                        "message": f"User {cust_id} {'added to' if action == 'add' else 'removed from'} group {group_id}"
                    }
                ),
                200,
            )
    except Exception as e:
        logger.error(f"Failed to modify group members: {str(e)}")
        return jsonify({"error": "Failed to modify group members", "details": str(e)}), 500


# Route to retrieve all users in a group
@groups.route("/<group_id>", methods=["GET"])
def get_group_members(group_id):
    query = """
        SELECT Customer.id, firstName, lastName, email
        FROM Customer
        JOIN Cust_Group ON Customer.id = Cust_Group.custId
        WHERE Cust_Group.groupId = %s
    """
    params = (group_id,)

    try:
        with get_cursor() as cursor:
            cursor.execute(query, params)
            members = cursor.fetchall()
            logger.info(f"Retrieved members for group {group_id}")
            return jsonify(members), 200
    except Exception as e:
        logger.error(f"Failed to retrieve group members: {str(e)}")
        return jsonify({"error": "Failed to retrieve group members", "details": str(e)}), 500


# Route to generate group recommendations
@groups.route("/<group_id>/recommendation", methods=["GET"])
def generate_group_recommendation(group_id):
    query = """
        SELECT Restaurant.id as restId, Restaurant.name, Restaurant.email, Recommendation.explanation
        FROM Recommendation
        JOIN Restaurant ON Recommendation.restId = Restaurant.id
        WHERE Recommendation.groupId = %s
    """
    params = (group_id,)

    try:
        with get_cursor() as cursor:
            cursor.execute(query, params)
            recommendations = cursor.fetchall()
            logger.info(f"Generated recommendations for group {group_id}")
            return jsonify(recommendations), 200
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {str(e)}")
        return jsonify({"error": "Failed to generate recommendations", "details": str(e)}), 500
