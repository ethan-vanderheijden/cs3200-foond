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


@groups.route("/<group_id>/recommendations", methods=["GET"])
def group_get(group_id):
    sql = """
        SELECT cui.name AS name
        FROM Dining_Group dg
        JOIN Cust_Group cg ON dg.id = cg.custId
        JOIN Customer c ON c.id = cg.custId
        JOIN Cust_Cuisine cc ON cc.custId = c.id
        JOIN Cuisine cui ON cui.id = cc.custId
        WHERE dg.id = """ + str(group_id) + """
        GROUP BY cui.id, cui.name
        ORDER BY COUNT(c.id)
        LIMIT 1;
        """
    with get_cursor() as cursor:
        logger.error(sql)
        try:
            with get_cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                logger.error(data)
                logger.info(f"Retrieved recommendations for group {data}")
                return jsonify(data), 200
        except Exception as e:
            logger.error(f"Failed to get recommendation: {str(e)}")
            return jsonify({"error": "Failed to get recommendation details " + str(e) + " " + sql}), 500
