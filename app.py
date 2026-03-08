from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("medmind.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        time TEXT,
        dosage TEXT,
        frequency TEXT,
        category TEXT,
        stock INTEGER,
        taken INTEGER DEFAULT 0,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("medmind.db")
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["medicine"]
        time = request.form["time"]
        dosage = request.form["dosage"]
        frequency = request.form["frequency"]
        category = request.form["category"]
        stock = request.form["stock"]

        c.execute("""
        INSERT INTO medicines
        (name,time,dosage,frequency,category,stock,date)
        VALUES(?,?,?,?,?,?,?)
        """,(name,time,dosage,frequency,category,stock,
             datetime.now().strftime("%Y-%m-%d")))

        conn.commit()

    c.execute("SELECT * FROM medicines")
    medicines = c.fetchall()

    total = len(medicines)
    taken = len([m for m in medicines if m[7] == 1])
    missed = len([m for m in medicines if m[7] == 0 and m[2] < datetime.now().strftime("%H:%M")])
    score = int((taken/total)*100) if total>0 else 0

    conn.close()

    return render_template("index.html",
                           medicines=medicines,
                           total=total,
                           taken=taken,
                           missed=missed,
                           score=score)


# ---------------- MARK ----------------
@app.route("/mark/<int:id>")
def mark(id):
    conn = sqlite3.connect("medmind.db")
    c = conn.cursor()

    c.execute("UPDATE medicines SET taken=1, stock=stock-1 WHERE id=?",(id,))
    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("medmind.db")
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/")


# ---------------- EMERGENCY ----------------
@app.route("/emergency")
def emergency():
    return "🚨 Emergency Alert Sent (Prototype)"


# ---------------- UPLOAD PRESCRIPTION ----------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if file:
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    return redirect("/")


# ---------------- AI SUGGESTION ----------------
@app.route("/ai")
def ai():
    hour = datetime.now().hour
    if hour < 12:
        message = "🌞 Morning tip: Stay hydrated with your medicine."
    elif hour < 18:
        message = "💪 Afternoon tip: Balanced diet improves medicine efficiency."
    else:
        message = "🌙 Night tip: Maintain consistent sleep schedule."

    return message


if __name__ == "__main__":
    app.run(debug=True)