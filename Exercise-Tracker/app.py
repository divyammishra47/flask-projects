from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Durga@2001'
app.config['MYSQL_DB'] = 'workout_tracker'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Check if user exists in the database
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cur.execute(query, (username, password))
        user = cur.fetchone()

        if user:
            # Store the user_id in the session
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Retrieve exercise names from the database for the logged-in user
    user_id = session['user_id']
    query = "SELECT DISTINCT exercise_name FROM exercises WHERE user_id = %s"
    cur.execute(query, (user_id,))
    exercise_names = cur.fetchall()

    exercise_options = [exercise[0] for exercise in exercise_names]

    if request.method == 'POST':
        if 'add_exercise' in request.form:
            new_exercise_name = request.form['new_exercise']

            # Insert the new exercise into the database
            query = "INSERT INTO exercises (user_id, exercise_name, sets, weight) VALUES (%s, %s, %s, %s)"
            cur.execute(query, (user_id, new_exercise_name, 0, 0))
            mysql.connection.commit()

            flash('New exercise added successfully!', 'success')
        else:
            exercise_name = request.form['exercise_name']
            sets = request.form['sets']
            weight = request.form['weight']

            # Insert exercise data into the database
            query = "INSERT INTO exercises (user_id, exercise_name, sets, weight) VALUES (%s, %s, %s, %s)"
            cur.execute(query, (user_id, exercise_name, sets, weight))
            mysql.connection.commit()

            # Check if the user has done 5 exercises with at least 3 sets each
            query = "SELECT COUNT(*) FROM exercises WHERE user_id = %s"
            cur.execute(query, (user_id,))
            exercise_count = cur.fetchone()[0]

            query = "SELECT COUNT(*) FROM exercises WHERE user_id = %s AND sets >= 3"
            cur.execute(query, (user_id,))
            exercise_sets_count = cur.fetchone()[0]

            if exercise_count >= 5 and exercise_sets_count >= 5:
                flash('Congratulations! You have completed 5 exercises with at least 3 sets each!', 'success')

    return render_template('home.html', exercise_options=exercise_options)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Retrieve workout history for the logged-in user, excluding exercises with sets = 0
    user_id = session['user_id']
    query = "SELECT exercise_name, sets, weight FROM exercises WHERE user_id = %s AND sets > 0"
    cur.execute(query, (user_id,))
    workout_history = cur.fetchall()

    return render_template('history.html', workout_history=workout_history)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Check if the username is already taken
        query = "SELECT * FROM users WHERE username = %s"
        cur.execute(query, (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error_signup')
        else:
            # Insert the new user into the database
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cur.execute(query, (username, password))
            mysql.connection.commit()

            flash('Account created successfully! You can now log in.', 'success_signup')
            return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)

