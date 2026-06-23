from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Aditya@2005",
    database="banking_db"
)

cursor = db.cursor()

@app.route('/')
def home():
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, password)
        )
        db.commit()

        return redirect('/login')

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]

            cursor.execute(
                "SELECT * FROM accounts WHERE user_id=%s",
                (user[0],)
            )

            account = cursor.fetchone()

            if not account:
                cursor.execute(
                    "INSERT INTO accounts(user_id,balance) VALUES(%s,%s)",
                    (user[0],0)
                )
                db.commit()

            return redirect('/dashboard')

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():

    user_id = session['user_id']

    cursor.execute(
        "SELECT * FROM accounts WHERE user_id=%s",
        (user_id,)
    )

    account = cursor.fetchone()

    return render_template(
        'dashboard.html',
        balance=account[2]
    )

# Deposit
@app.route('/deposit', methods=['POST'])
def deposit():

    amount = float(request.form['amount'])
    user_id = session['user_id']

    cursor.execute(
        "UPDATE accounts SET balance = balance + %s WHERE user_id=%s",
        (amount, user_id)
    )

    db.commit()

    return redirect('/dashboard')

# Withdraw
@app.route('/withdraw', methods=['POST'])
def withdraw():

    amount = float(request.form['amount'])
    user_id = session['user_id']

    cursor.execute(
        "SELECT balance FROM accounts WHERE user_id=%s",
        (user_id,)
    )

    balance = cursor.fetchone()[0]

    if balance >= amount:
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE user_id=%s",
            (amount, user_id)
        )

        db.commit()

    return redirect('/dashboard')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)