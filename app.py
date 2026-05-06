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

def get_multiplier(package):
    if package == "Solo Explorer":
        return 1
    elif package == "Couple Escape":
        return 1.8
    elif package == "Elite Experience":
        return 2.5
    return 1


def calculate_price(destination, package, people):
    conn = sqlite3.connect("pricing.db")
    cursor = conn.cursor()

    cursor.execute("SELECT regular_price FROM pricing WHERE destination = ?", (destination,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        return 0

    base_price = data[0]
    multiplier = get_multiplier(package)

    return int(base_price * multiplier * people)

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
            <option>Solo Explorer</option>
            <option>Couple Escape</option>
            <option>Elite Experience</option>
        </select><br><br>

        <button type="submit">Submit</button>
    </form>
    """

# ---------------- ADMIN PAGE ----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, destination, date, people, package FROM bookings")
    data = cursor.fetchall()
    conn.close()

    total_revenue = 0
    rows_html = ""

    for row in data:
        name, phone, destination, date, people, package = row
        people = int(people)
        total = calculate_price(destination, package, people)
        total_revenue += total

        rows_html += f"""
        <p>
        <b>{name}</b> | {phone} | {destination} | {date} | {people} people | {package} | GHS {total}
        </p>
        <hr>
        """

    output = f"<h1>Rich Republic Admin Dashboard</h1><hr><h2>Total Revenue: GHS {total_revenue}</h2><hr>"
    output += rows_html
