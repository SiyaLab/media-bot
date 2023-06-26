# telegram bot modules
import telebot
from telebot.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
# SQL modules
import mysql.connector
from mysql.connector import Error
# internal
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# Define the commands and their descriptions
COMMANDS = [
    BotCommand(command='/start', description='Start the bot'),
    BotCommand(command='/add', description='Add favorite'),
    BotCommand(command='/remove', description='Remove favorite'),
    BotCommand(command='/remove_all', description='Remove all favorites'),
    BotCommand(command='/list', description='Your added favorites'),
    BotCommand(command='/tv_watch_list', description='TV Shows details'),
    BotCommand(command='/help', description='Help'),
    BotCommand(command='/settings', description='Show settings'),
    BotCommand(command='/feedback', description='Send feedback')
]

# Create a blank ReplyKeyboardMarkup
blank_keyboard = ReplyKeyboardMarkup()

# yes or no keyboard
# Define the confirm keyboard options
confirm_options = [
    KeyboardButton('Yes'),
    KeyboardButton('No')
]
# Create the confirm keyboard markup
confirm_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
# Add the confirm options to the keyboard
confirm_keyboard.add(*confirm_options)


def set_bot_commands(bot):
    bot.set_my_commands(COMMANDS)
    # bot.set_my_commands([])

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(
            message.chat.id, 'Please choose an option:', reply_markup=blank_keyboard)

    @bot.message_handler(commands=['add'])
    def add(message):
        bot.send_message(message.chat.id, 'Enter the favorite:')
        bot.register_next_step_handler(message, process_add_step, bot)

    @bot.message_handler(commands=['remove'])
    def remove(message):
        bot.send_message(message.chat.id, 'Enter the favorite to remove:')
        bot.register_next_step_handler(message, process_remove_step, bot)

    @bot.message_handler(commands=['remove_all'])
    def remove_all(message):
        bot.send_message(
            message.chat.id, 'Are you sure you want to remove all favorites?', reply_markup=confirm_keyboard)
        bot.register_next_step_handler(message, process_remove_all_step, bot)

    @bot.message_handler(commands=['list'])
    def list_favorites(message):
        chat_id = message.chat.id
        favorites = get_favorites(chat_id)
        if favorites:
            favorites_text = '\n'.join(favorites)
            bot.send_message(
                message.chat.id, f'Your added favorites:\n{favorites_text}')
        else:
            bot.send_message(message.chat.id, 'You have no favorites.')

    @bot.message_handler(commands=['tv_watch_list'])
    def watch_list(message):
        chat_id = message.chat.id
        watch_list = get_tv_watch_list(chat_id)

        if watch_list:
            response = "Your TV Show Watch List:\n\n"
            response += "\n".join(watch_list)
        else:
            response = "Your TV Show Watch List is empty."

        bot.send_message(chat_id, response)

    @bot.message_handler(commands=['help'])
    def help(message):
        help_message = '''The bot notifies you whenever your favorite shows or movies are added to https://hd.fmoviesto.site/.

            Commands:
            /add - Add favorite
            /remove - Remove favorite
            /remove_all - Remove all favorites
            /list - Your added favorites
            /tv_watch_list - TV Shows details
            /help - Help
            /settings - Show settings
            /feedback YOUR_MESSAGE - Send feedback
        '''
        bot.send_message(message.chat.id, help_message)

    @bot.message_handler(commands=['settings'])
    def settings(message):
        # Handle settings command
        # ...
        pass

    @bot.message_handler(commands=['feedback'])
    def feedback(message):
        # Handle feedback command
        # ...
        pass


def process_add_step(message, bot):
    chat_id = message.chat.id
    favorite = message.text
    add_favorite(chat_id, favorite)
    bot.send_message(chat_id, f"New favorite {favorite} has been added!")


def process_remove_step(message, bot):
    chat_id = message.chat.id
    favorite = message.text
    remove_favorite(chat_id, favorite)
    bot.send_message(chat_id, f"Favorite {favorite} has been removed!")


def process_remove_all_step(message, bot):
    chat_id = message.chat.id
    if message.text.lower() == 'yes':
        # Remove all favorites
        remove_all_favorites(chat_id)
        bot.send_message(chat_id, 'All favorites removed successfully.')
    else:
        bot.send_message(chat_id, 'Remove all favorites operation canceled.')


def add_favorite(chat_id, title):
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

            # Check if the favorite already exists for the user
            select_favorite_query = '''
            SELECT id FROM favorites WHERE user_id = %s AND title = %s
            '''
            cursor.execute(select_favorite_query, (user_id, title))
            existing_favorite = cursor.fetchone()

            if existing_favorite:
                print(
                    f"Favorite with title '{title}' already exists for {user_id} user")
            else:
                # Insert the favorite into the 'favorites' table
                insert_query = '''
                INSERT INTO favorites (user_id, title) VALUES (%s, %s)
                '''
                cursor.execute(insert_query, (user_id, title))
                connection.commit()

                print(
                    f"Favorite with title '{title}' added successfully for user {user_id}")
        else:
            print("User not found!")


def remove_favorite(chat_id, title):
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

            # Check if the favorite exists for the user
            select_favorite_query = '''
            SELECT id FROM favorites WHERE user_id = %s AND title = %s
            '''
            cursor.execute(select_favorite_query, (user_id, title))
            existing_favorite = cursor.fetchone()

            if existing_favorite:
                # Remove the favorite from the 'favorites' table
                delete_query = '''
                DELETE FROM favorites WHERE user_id = %s AND title = %s
                '''
                cursor.execute(delete_query, (user_id, title))
                connection.commit()

                print(
                    f"Favorite with title '{title}' removed successfully for user {user_id}")
            else:
                print("Favorite does not exist for this user!")
        else:
            print("User not found!")


def remove_all_favorites(chat_id):
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

                # Remove all favorites for the user from the 'favorites' table
                delete_query = '''
                DELETE FROM favorites WHERE user_id = %s
                '''
                cursor.execute(delete_query, (user_id,))
                connection.commit()

                print(f"All favorites removed successfully for user {user_id}")
            else:
                print("User not found!")
    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            # Clear any remaining results
            while connection.next_result():
                pass
            connection.close()


def get_favorites(chat_id):
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

            # Retrieve favorites for the user from the 'favorites' table
            select_query = '''
            SELECT title FROM favorites WHERE user_id = %s
            '''
            cursor.execute(select_query, (user_id,))
            favorites = cursor.fetchall()

            print(f'Providing user {user_id} thier favorites')
            # Extract the titles from the result and return as a list
            return [favorite[0] for favorite in favorites]

    return []


def get_tv_watch_list(chat_id):
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

            # Retrieve the latest TV show favorites for the user from the 'favorites' table
            select_query = '''
            SELECT title FROM favorites WHERE user_id = %s ORDER BY id DESC LIMIT 10
            '''
            cursor.execute(select_query, (user_id,))
            favorites = cursor.fetchall()

            watch_list = []
            for favorite in favorites:
                favorite_title = favorite[0]

                select_item_query = '''
                SELECT title, season, episode FROM items WHERE title LIKE %s AND type = 'tv'
                '''
                cursor.execute(select_item_query,
                               ('%' + favorite_title + '%',))
                item = cursor.fetchone()

                if item:
                    title = item[0]
                    season = item[1]
                    episode = item[2]
                    watch_list.append(
                        f"{title} - S{season}, E{episode}")

            return watch_list

    return []
