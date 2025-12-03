from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "change_this_to_a_strong_secret_key"   # required for sessions


def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="teacher"
    )
    return conn


@app.route("/")
def index():
    # Show login page
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    teacher_id = request.form.get("teacher_id")
    password = request.form.get("password")

    if not teacher_id or not password:
        flash("Please enter both Teacher ID and Password", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)   # dict rows
    cur.execute(
        "SELECT id, teacher_id, name, password_hash FROM teachers WHERE teacher_id = %s",
        (teacher_id,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        flash("Invalid Teacher ID or Password", "error")
        return redirect(url_for("index"))

    # verify password (stored as hash in DB)
    if user["password_hash"] != password:
        flash("Invalid Teacher ID or Password", "error")
        return redirect(url_for("index"))

    # Successful login → store in session
    session["teacher_id"] = user["teacher_id"]
    session["teacher_name"] = user["name"]

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("index"))

    return render_template("dashboard.html", name=session["teacher_name"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
