
from flask import Flask, request, redirect, session, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"


def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # create users table if not there
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    # create notes table if not there
    cur.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, user_id INTEGER, note_info TEXT)")

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    return conn


init_db()
    
@app.route("/")
def get_login_page():
    return render_template("index.html")



@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        query=f"INSERT INTO users (username,password) VALUES ('{username}','{password}')" 
        cur.execute(query)
        conn.commit()
        conn.close()

        return redirect("/login")
    
    return render_template("register.html")
    


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cur.execute(query)
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/notes")
        else:
            return "login failed",401
    
    return render_template("login.html")



@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")



@app.route("/add_notes", methods=["POST", "GET"])
def add_note():
    if "user_id" not in session:
        return redirect("/login")
    
    if request.method == "POST":
        note_txt = request.form["note_info"]

        conn = get_db()
        cur = conn.cursor()

        query = f"INSERT INTO notes (user_id, note_info) VALUES ({session['user_id']}, '{note_txt}')"
        cur.execute(query)
        conn.commit()
        conn.close()
        return redirect("/notes")

    return render_template("add_note.html")



@app.route("/notes", methods=["GET","POST"])
def view():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    query =f"SELECT * FROM notes WHERE user_id={session['user_id']}"
    cur.execute(query)
    notes = cur.fetchall()
    conn.close()
    return render_template("notes.html",notes=notes)



@app.route("/delete/<id>", methods=["GET"])
def delete(id):
    
    conn = get_db()
    cur = conn.cursor()

    query =f"DELETE FROM notes WHERE id={id}"
    cur.execute(query)
    conn.commit()
    conn.close()
    return redirect("/notes")




if __name__ == "__main__":
    app.run(debug=True)








