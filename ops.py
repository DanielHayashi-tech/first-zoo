import flask
from datetime import datetime
from flask import jsonify, request
from db import create_connection, execute_query, execute_read_query
from mysql.connector import Error

conn = create_connection('coogs.cypiz5agmq0c.us-east-1.rds.amazonaws.com', 'admin', 'phoebe123', 'coogs_db')

# setting up an application name
app = flask.Flask(__name__)  # sets up the application
app.config["DEBUG"] = True  # allow to show errors in browser


# in this function we are calling the logs table and making an insert depending on what values are returned from the user
def logging_animals(date, animalid, comment):
    # this is the query that inserts in to logs table
    query = f"INSERT INTO logs (date, animalid, comment) VALUES ('{date}', {animalid}, '{comment}')"
    try:
        execute_query(conn, query)
        # we imported Error to be able to return any errors that return from this executed query
    except Error as e:
        return f" The error '{e}' has occurred!"


@app.route('/api/animals', methods=['POST'])
def add_animal():
    request_data = request.get_json()
    new_animal = request_data['animal']
    new_gender = request_data['gender']
    new_subtype = request_data['subtype']
    new_age = request_data['age']
    new_color = request_data['color']

    insert_animal = f"INSERT INTO zoo (animal, gender, subtype, age, color) VALUES " \
                    f"('{new_animal}', '{new_gender}', '{new_subtype}', {new_age},'{new_color}')"
    try:
        execute_query(conn, insert_animal)

        log_animal = f"You added a {new_animal} to the Zoo"
        log_date = datetime.today().strftime('%Y-%m-%d')
        log_animalid = 2

        logging_animals(date=log_date, animalid=log_animalid, comment=log_animal)

        return f"Congratulations, you have successfully added a {new_animal} to the Zoo!"
    except Error as e:
        return f"the error {e} occurred"



@app.route('/api/animals', methods=['GET'])
def show_zoo():
    query = "SELECT * FROM zoo"
    try:
        animals = execute_read_query(conn, query)
        return jsonify(animals)
    except Error as e:
        return f" The error '{e}' has occurred!"


@app.route('/api/logs', methods=['GET'])
def show_logs():
    query = "SELECT * FROM logs"
    try:
        animals = execute_read_query(conn, query)
        return jsonify(animals)
    except Error as e:
        return f" The error '{e}' has occurred!"


@app.route('/api/animals', methods=['PUT'])  # add an animal as POST: http://127.0.0.1:5000
def update_animal():
    request_data = request.get_json()
    new_id = request_data['id']
    new_animal = request_data['animal']
    new_gender = request_data['gender']
    new_subtype = request_data['subtype']
    new_age = request_data['age']
    new_color = request_data['color']

    update_criteria = f"UPDATE zoo SET animal='{new_animal}', gender='{new_gender}', subtype='{new_subtype}', " \
                      f"age='{new_age}', color='{new_color}' WHERE id={new_id}"
    try:
        execute_query(conn, update_criteria)
        return f'Congratulations, you have successfully updated ID #{new_id}!'
    except Error as e:
        return f"The error '{e}' has occurred"


@app.route('/api/animals', methods=['DELETE'])
def remove_animal():
    request_data = request.get_json()
    new_id = request_data['id']

    delete = f'DELETE FROM zoo WHERE id={new_id}'
    try:
        execute_query(conn, delete)

        log_animal = f"{new_id} was deleted from the Zoo"
        log_date = datetime.today().strftime('%Y-%m-%d')
        log_animalid = new_id

        logging_animals(date=log_date, animalid=log_animalid, comment=log_animal)

        return f"Congratulations, you have successfully removed {new_id} from the zoo"
    except Error as e:
        return f"the error {e} occurred"


# endpoint to delete contents from log table
@app.route('/api/logs', methods=['DELETE'])
def reset_logs():
    try:
        if 'reset' in request.args:
            reset = request.args['reset']
            # be sure to write 'TRUE' in all caps when clearing the logs table!
            if reset == "TRUE":
                query = "DELETE FROM logs;"
                execute_query(conn, query)
            return "you have cleared the logs table "
        else:
            return 'ERROR'
    except Error as e:
        return f"The error '{e}' has occurred"


app.run()
