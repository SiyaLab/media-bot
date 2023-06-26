import mysql.connector
from mysql.connector import Error
import telebot
from telebot import types
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def notify_users(bot):
    print('Running notfiy user function...')
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Get the list of updated favorites
            updated_favorites = get_updated_favorites(cursor)

            # Notify users about updated favorites
            for user_id, favorite_id, title, chat_id in updated_favorites:
                # Get the item details for the notification
                items = search_items_by_title(cursor, title)
                for item in items:
                    item_details = {
                        'type': item[0],
                        'title': item[1],
                        'image': item[2],
                        'season': item[3],
                        'episode': item[4]
                    }

                    print(
                        f'Sending notification to user {user_id} about item {item}')
                    # Send the notification to the user with photo and caption
                    send_photo_with_caption(bot, chat_id, item_details)

                # Update the last notification time in the notifications table
                update_last_notification_time(cursor, user_id, favorite_id)

            cursor.close()

    except Error as e:
        print('Error:', e)

    finally:
        print('Done running notify users function.')
        if connection and connection.is_connected():
            connection.close()


def search_items_by_title(cursor, title):
    select_query = '''
    SELECT type, title, image, season, episode
    FROM items
    WHERE title LIKE %s
    '''
    cursor.execute(select_query, ('%' + title + '%',))
    return cursor.fetchall()


# def send_notification(bot, chat_id, title):
#     message = f"Your favorite show '{title}' is now available on the homepage!"
#     bot.send_message(chat_id, message)


def update_last_notification_time(cursor, user_id, favorite_id):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            print('Running update_last_notification_time...')
            update_query = '''
            INSERT INTO notifications (user_id, favorite_id, last_notification_time)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE last_notification_time = NOW()
            '''
            cursor.execute(update_query, (user_id, favorite_id))
            connection.commit()

            update_query = '''
            UPDATE favorites
            SET last_updated_time = NOW()
            WHERE id = %s
            '''
            cursor.execute(update_query, (favorite_id,))
            connection.commit()

            print('Done running update_last_notification_time')

    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            # Clear any remaining results
            while connection.next_result():
                pass
            connection.close()


def send_photo_with_caption(bot, chat_id, item):
    try:
        # Send the image as a photo with the caption message
        bot.send_photo(chat_id, item['image'], caption=get_item_caption(item))
    except Error as e:
        print('Error:', e)


def get_item_caption(item):
    caption = f"Your favorite {item['type']} is now available!\nTitle: {item['title']}"
    if item['type'] == 'tv':
        caption += f"\nSeason: {item['season']}, Episode: {item['episode']}"
    return caption


def get_updated_favorites(cursor):
    select_query = '''
    SELECT f.user_id, f.id, f.title, u.chat_id
    FROM favorites f
    INNER JOIN users u ON f.user_id = u.id
    WHERE f.last_updated_time > (
        SELECT MAX(n.last_notification_time)
        FROM notifications n
        WHERE n.favorite_id = f.id
    ) OR f.last_updated_time IS NULL
    '''
    cursor.execute(select_query)
    return cursor.fetchall()
