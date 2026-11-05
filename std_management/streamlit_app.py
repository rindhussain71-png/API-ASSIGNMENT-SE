import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000/students"

st.set_page_config(page_title="Student Management", page_icon="🎓")

st.title("Student Management System")
st.write("Manage University Student Records")

def get_students():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        st.error("Flask API is not running. Please start app.py first.")
        return []

students = get_students()

st.subheader("All Students")

if students:
    st.dataframe(students, use_container_width=True)
else:
    st.info("No student records found.")

st.divider()

st.subheader("Add New Student")

with st.form("add_student_form"):
    student_id = st.number_input(
        "Student ID", min_value=1, step=1
    )
    name = st.text_input("Student Name")
    department = st.text_input("Department")
    email = st.text_input("Email")

    add_button = st.form_submit_button("Add Student")

    if add_button:
        data = {
            "student_id": int(student_id),
            "name": name,
            "department": department,
            "email": email
        }

        if name and department and email:
            response = requests.post(API_URL, json=data)

            if response.status_code == 201:
                st.success("Student added successfully!")
                st.rerun()
            else:
                st.error(response.json().get("error", "Error adding student"))
        else:
            st.warning("Please fill all fields.")

st.divider()

st.subheader("Update Existing Student")

if students:
    student_ids = [s["student_id"] for s in students]

    selected_id = st.selectbox(
        "Select Student ID",
        student_ids
    )

    selected_student = next(
        s for s in students
        if s["student_id"] == selected_id
    )

    with st.form("update_student_form"):
        new_name = st.text_input(
            "Student Name",
            value=selected_student["name"]
        )

        new_department = st.text_input(
            "Department",
            value=selected_student["department"]
        )

        new_email = st.text_input(
            "Email",
            value=selected_student["email"]
        )

        update_button = st.form_submit_button("Update Student")

        if update_button:
            data = {
                "name": new_name,
                "department": new_department,
                "email": new_email
            }

            response = requests.put(
                f"{API_URL}/{selected_id}",
                json=data
            )

            if response.status_code == 200:
                st.success("Student updated successfully!")
                st.rerun()
            else:
                st.error(response.json().get("error", "Update failed"))

    st.divider()

    st.subheader("Delete Student")

    delete_id = st.selectbox(
        "Select Student to Delete",
        student_ids,
        key="delete_student"
    )

    if st.button("Delete Student"):
        response = requests.delete(f"{API_URL}/{delete_id}")

        if response.status_code == 200:
            st.success("Student deleted successfully!")
            st.rerun()
        else:
            st.error(response.json().get("error", "Delete failed"))

else:
    st.info("Add a student first to use update and delete options.")

if st.button("Refresh Records"):
    st.rerun()