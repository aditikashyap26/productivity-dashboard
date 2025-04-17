from flask import Flask,render_template, request, redirect, jsonify
import requests
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

tasks = []


# MySQL Configuration


app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

@app.route("/", methods = ['GET' , 'POST'])
def index():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        task =  request.form.get('task')
        if task:
            cur.execute(f"INSERT INTO tasks (name) VALUES ('{task}')")
            mysql.connection.commit()
        return redirect("/")
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    cur.close()
    return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:task_id>', methods=["POST"])
def delete(task_id):
    if task_id:
        cur = mysql.connection.cursor()
        cur.execute(f"DELETE FROM tasks WHERE id = {task_id}")
        mysql.connection.commit()
        cur.close()
    return redirect("/")

@app.route('/update/<int:task_id>', methods=["POST"])
def update(task_id):
    task_name = request.form.get('task')
    if task_name:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks SET name = %s WHERE id = %s", (task_name, task_id))
        mysql.connection.commit()
        cur.close()
    return redirect('/')



@app.route('/weather')
def weather():
    city = request.args.get('city')
    if not city:
        return {"error": "City required"}, 400

    API_KEY = '95f49a53b0a318bb11b2722a24c90e83'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        return {"error": "City not found"}, 404

    data = res.json()
    return {
        "temp": data['main']['temp'],
        "description": data['weather'][0]['description'].capitalize(),
        "icon": data['weather'][0]['icon']  # This line enables icon support
    }


@app.route('/quote')
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        data = response.json()
        return jsonify(quote=data[0]['q'], author=data[0]['a'])
    except Exception as e:
        return jsonify(error="Could not fetch a quote")

if __name__ == "__main__":
    app.run(debug=True)