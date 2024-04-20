from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import mysql.connector
import random
from mysql.connector import Error
from flask import Flask

app = Flask(__name__)
app.secret_key = '0979c7dfd41e7a83bcbe57a001d258cb'

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="expense_tracker"
)
cursor = db.cursor()
groups = {}

def generate_group_code():
    return str(random.randint(1000, 9999))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return render_template('signup.html', exists=True)
        else:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('primary_goal'))
        else:
            return render_template('login.html', invalid=True)
    return render_template('login.html')

@app.route('/primary_goal')
def primary_goal():
    return render_template('primary_goal.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = request.form['amount']
        currency = request.form['currency']
        date = request.form['date']
        category = request.form['category']
        
        cursor.execute("INSERT INTO expenses (user_id, amount, currency, date, category) VALUES (%s, %s, %s, %s, %s)", 
                       (session['user_id'], amount, currency, date, category))
        db.commit()
        return redirect(url_for('display_expenses'))
    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        
        cursor.execute("INSERT INTO incomes (user_id, amount, category, date) VALUES (%s, %s, %s, %s)", 
                       (session['user_id'], amount, category, date))
        db.commit()
        return redirect(url_for('home'))
    return render_template('add_income.html')

@app.route('/display_expenses')
def display_expenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (session['user_id'],))
    expenses = cursor.fetchall()
    return render_template('display_expenses.html', expenses=expenses)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, session['user_id']))
    db.commit()
    return redirect(url_for('display_expenses'))

def fetch_daily_expenses_from_database():
    try:
        
        query = "SELECT category, SUM(amount) as total_amount FROM expenses GROUP BY category"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        daily_expenses = {}
        for row in rows:
            category, total_amount = row
            daily_expenses[category] = total_amount

        
        return daily_expenses
    except Error as e:
        print(f"Error fetching daily expenses from the database: {e}")
        return None

# Fetch total income from the database
def fetch_total_income_from_database():
    try:
        query = "SELECT SUM(amount) as total_income FROM incomes"
        cursor.execute(query)
        row = cursor.fetchone()
        total_income = row[0] if row else 0
        return total_income
    except Error as e:
        print(f"Error fetching total income from the database: {e}")
        return None

@app.route('/get-financial-data')
def get_financial_data():
    try:
        # Query to fetch total income
        cursor.execute("SELECT SUM(amount) FROM incomes")
        total_income = cursor.fetchone()[0]

        # Query to fetch total expenses
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = cursor.fetchone()[0]
        

        # Return the data as JSON
        return jsonify({
            'totalIncome': total_income,
            'totalExpenses': total_expenses
        })
    except Error as e:
        print(f"Error fetching financial data from the database: {e}")
        return jsonify({'error': str(e)}), 


@app.route('/analysis')
def analysis():
    # Use the existing database connection
    # Replace `db` with the variable name of your existing connection
    daily_expenses = fetch_daily_expenses_from_database()

    if daily_expenses is None:
        return render_template('error.html', error_message="Error fetching data from the database.")

    total_income = fetch_total_income_from_database()

    if total_income is None:
        return render_template('error.html', error_message="Error fetching data from the database.")
    
    categories = list(daily_expenses.keys())
    amounts = list(daily_expenses.values())

    total_expenses = sum(amounts)

    # Calculate the balance amount and balance percentage
    balance_amount = total_income - total_expenses
    balance_percentage = (balance_amount / total_income) * 100 if total_income > 0 else 0

    return render_template('analysis.html', categories=categories, amounts=amounts,
                           balance_amount=balance_amount, balance_percentage=balance_percentage)

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        group_code = generate_group_code()
        groups[group_code] = {'name': group_name, 'members': []}
        return render_template('group_created.html', group_name=group_name, group_code=group_code)
    return render_template('create_group.html')


# Function to generate a random group code
def generate_group_code():
    return str(random.randint(1000, 9999))

# Route for joining a group
@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
    if request.method == 'POST':
        group_code = request.form['group_code']
        

        # Check if the group code exists in the database
        cursor.execute("SELECT * FROM groups WHERE group_code = %s", (group_code,))
        group = cursor.fetchone()

        if group:
            group_name = group[1]  # Assuming the second column contains the group name
            num_people = int(request.form['num_people'])
            group_members = []

            # Extract group member names from the form
            for i in range(1, num_people + 1):
                group_members.append(request.form.get(f'person_{i}_name'))

            try:
                # Insert group details into the database
                cursor.execute("INSERT INTO groups (group_name, group_code) VALUES (%s, %s)", (group_name, group_code))
                group_id = cursor.lastrowid

                # Insert group members into the database
                for member in group_members:
                    cursor.execute("INSERT INTO group_members (group_id, member_name) VALUES (%s, %s)", (group_id, member))

                # Commit the changes to the database
                db.commit()

                # Redirect to the add_group_expense page
                return redirect(url_for('add_group_expense', group_name=group_name))

            except mysql.connector.Error as err:
                # Handle database errors
                print("Database error:", err)
                db.rollback()
                return render_template('join_group.html', error=True)

        else:
            # Group code does not exist in the database
            return render_template('join_group.html', invalid_code=True)

    return render_template('join_group.html')

# Route for adding group expenses
@app.route('/add_group_expense', methods=['GET', 'POST'])
def add_group_expense():
    if request.method == 'POST':
        group_id = request.form['group_id']
        amount = request.form['amount']
        currency = request.form['currency']
        date = request.form['date']
        category = request.form['category']

        try:
            
            cursor.execute("INSERT INTO expenses (group_id, amount, currency, date, category) VALUES (%s, %s, %s, %s, %s)", 
                           (group_id, amount, currency, date, category))
            db.commit()
            return redirect(url_for('display_expenses', group_id=group_id))
        except mysql.connector.Error as err:
            # Handle database errors
            print("Database error:", err)
            db.rollback()
            return render_template('add_group_expense.html', error=True)

    group_id = request.args.get('group_id')
    return render_template('add_group_expense.html', group_id=group_id)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
