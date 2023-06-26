import mysql.connector
from mysql.connector import Error
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def update_last_online(chat_id):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Check if the user exists in the 'users' table
            select_query = '''
            SELECT id FROM users WHERE chat_id = %s
            '''
            cursor.execute(select_query, (chat_id,))
            result = cursor.fetchone()

            if result:
                user_id = result[0]

                # Update the last online time for the user
                update_query = '''
                UPDATE users SET last_online = NOW() WHERE id = %s
                '''
                cursor.execute(update_query, (user_id,))
                connection.commit()

                print("Last online time updated successfully!")
            else:
                print("User not found!")

            cursor.close()

    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            connection.close()


def create_user(chat_id, username, name):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Check if the user already exists in the 'users' table
            select_query = '''
            SELECT * FROM users WHERE chat_id = %s
            '''
            cursor.execute(select_query, (chat_id,))
            user_exists = cursor.fetchone() is not None

            if not user_exists:
                # Insert the new user into the 'users' table
                insert_query = '''
                INSERT INTO users (chat_id, username, name, last_online) VALUES (%s, %s, %s, NOW())
                '''
                cursor.execute(insert_query, (chat_id, username, name))
                connection.commit()

                print("User created successfully!")
            else:
                print("User already exists!")

            cursor.close()

    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            connection.close()
