from flask import Flask, request, jsonify
import secrets
from functools import wraps

app = Flask(__name__)

# Demo user accounts
users = {
    "employee": {
        "password": "emp123",
        "role": "Employee"
    },
    "admin": {
        "password": "admin123",
        "role": "Administrator"
    }
}

# Store login tokens
tokens = {}

# Employee records
employees = [
    {"id": 1, "name": "Ali", "department": "IT"},
    {"id": 2, "name": "Ahmed", "department": "HR"}
]


# Authentication decorator
def login_required(role=None):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            token = request.headers.get("Authorization")

            if not token or token not in tokens:
                return jsonify({"error": "Unauthorized. Please login first"}), 401

            user_role = tokens[token]

            if role == "Administrator" and user_role != "Administrator":
                return jsonify({"error": "Forbidden. Admin access required"}), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Login endpoint
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if username not in users or users[username]["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    token = secrets.token_urlsafe(32)
    tokens[token] = users[username]["role"]

    return jsonify({
        "message": "Login successful",
        "username": username,
        "role": users[username]["role"],
        "token": token
    }), 200


# View employees - Both roles allowed
@app.route("/employees", methods=["GET"])
@login_required()
def view_employees():

    return jsonify({
        "employees": employees
    }), 200


# Add employee - Admin only
@app.route("/employees", methods=["POST"])
@login_required("Administrator")
def add_employee():

    data = request.get_json(silent=True) or {}

    if not data.get("name") or not data.get("department"):
        return jsonify({"error": "Name and department are required"}), 400

    new_employee = {
        "id": max([e["id"] for e in employees], default=0) + 1,
        "name": data["name"],
        "department": data["department"]
    }

    employees.append(new_employee)

    return jsonify({
        "message": "Employee added successfully",
        "employee": new_employee
    }), 201


# Update employee - Admin only
@app.route("/employees/<int:employee_id>", methods=["PUT"])
@login_required("Administrator")
def update_employee(employee_id):

    data = request.get_json(silent=True) or {}

    for employee in employees:
        if employee["id"] == employee_id:

            if "name" in data:
                employee["name"] = data["name"]

            if "department" in data:
                employee["department"] = data["department"]

            return jsonify({
                "message": "Employee updated successfully",
                "employee": employee
            }), 200

    return jsonify({"error": "Employee not found"}), 404


# Delete employee - Admin only
@app.route("/employees/<int:employee_id>", methods=["DELETE"])
@login_required("Administrator")
def delete_employee(employee_id):

    for employee in employees:
        if employee["id"] == employee_id:
            employees.remove(employee)

            return jsonify({
                "message": "Employee deleted successfully"
            }), 200

    return jsonify({"error": "Employee not found"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)