from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            destination TEXT,
            date TEXT,
            people INTEGER,
            package TEXT
        )
    """)
    conn.commit()
    conn.close()

def init_reviews_db():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_reviews_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/reviews", methods=["GET", "POST"])
def reviews_page():
    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]

        conn = sqlite3.connect("reviews.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (name, message) VALUES (?, ?)", (name, message))
        conn.commit()
        conn.close()

    html = """
    <h1>Customer Reviews</h1>

    <form method="POST">
        Name:<br>
        <input name="name" required><br><br>

        Review:<br>
        <textarea name="message" required></textarea><br><br>

        <button type="submit">Submit</button>
    </form>

    <hr>
    <h2>All Reviews</h2>
    """

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, message FROM reviews")
    data = cursor.fetchall()
    conn.close()

    for row in data:
        html += f"<p><b>{row[0]}</b>: {row[1]}</p><hr>"

    html += "<a href='/'>Back Home</a>"
    return html

# ---------------- BOOKING PAGE ----------------
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        destination = request.form["destination"]
        date = request.form["date"]
        people = request.form["people"]
        package = request.form["package"]

        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (name, phone, destination, date, people, package)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, destination, date, people, package))
        conn.commit()
        conn.close()

        return """
        <h2>Booking Successful 🎉</h2>
        <a href='/book'>Book Another</a><br>
        <a href='/'>Home</a>
        """

    return """
    <h1>Book a Trip</h1>
    <form method="POST">

        Name:<br>
        <input name="name" required><br><br>

        Phone:<br>
        <input name="phone" required><br><br>

        Destination:<br>
        <input name="destination" required><br><br>

        Date:<br>
        <input type="date" name="date" required><br><br>

        People:<br>
        <input type="number" name="people" required><br><br>

        Package:<br>
        <select name="package">
            <option>Regular</option>
            <option>VIP</option>
        </select><br><br>

        <button type="submit">Submit</button>
    </form>
    """

# ---------------- ADMIN PAGE ----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()
    conn.close()

    output = "<h1>All Bookings</h1>"

    for row in data:
        output += f"""
        <p>
        ID: {row[0]} <br>
        Name: {row[1]} <br>
        Phone: {row[2]} <br>
        Destination: {row[3]} <br>
        Date: {row[4]} <br>
        People: {row[5]} <br>
        Package: {row[6]}
        </p>
        <hr>
        """

    return output

if __name__ == "__main__":
    app.run(debug=True)
