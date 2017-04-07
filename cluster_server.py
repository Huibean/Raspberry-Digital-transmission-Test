from flask import Flask
import sqlite3

database_connection = sqlite3.connect('transmission_test.db')
app_c = database_connection.cursor()

try:
    app_c.execute('''CREATE TABLE test_results (test_id integer, delay real, date text)''')
except Exception as e:
    pass

app = Flask(__name__)

@app.route("/get_records")

def get_records():
    for row in c.execute('SELECT * FROM test_results'):
        print(row)
        return "hello"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
