from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = connect_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/students", methods=["GET"])
def get_students():
    conn = connect_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    conn = connect_db()
    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()

    if not data or not all(data.get(k) for k in
                           ["student_id", "name", "department", "email"]):
        return jsonify({"error": "All fields are required"}), 400

    conn = connect_db()

    try:
        conn.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?)",
            (
                data["student_id"],
                data["name"],
                data["department"],
                data["email"]
            )
        )
        conn.commit()
        return jsonify({"message": "Student added successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    finally:
        conn.close()


@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json()

    if not data or not all(data.get(k) for k in
                           ["name", "department", "email"]):
        return jsonify({"error": "All fields are required"}), 400

    conn = connect_db()

    result = conn.execute(
        """UPDATE students
           SET name = ?, department = ?, email = ?
           WHERE student_id = ?""",
        (
            data["name"],
            data["department"],
            data["email"],
            student_id
        )
    )

    conn.commit()
    conn.close()

    if result.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student updated successfully"})


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = connect_db()

    result = conn.execute(
        "DELETE FROM students WHERE student_id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    if result.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


if __name__ == "_main_":
    print ("flask is start")
    create_table()
    app.run(host="127.0.0.1",port=5000,debug=True)