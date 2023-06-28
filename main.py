
import threading
import re
# telegram bot modules
import telebot
from telebot import types
# SQL modules
import mysql.connector
from mysql.connector import Error
# datetime and time
import time
import datetime
# scraping tools
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# Internal
from config import TELEGRAM_API_KEY, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
import user
import notification
import commands

# from mysql.connector import MySQLConnector
# mysql_connector = MySQLConnector(
#     MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)


class MySQLConnector:
    def __init__(self, host, user, password, database):
        # self.connection = mysql.connector.connect(
        #     host=host,
        #     user=user,
        #     password=password,
        #     database=database
        # )
        # self.cursor = self.connection.cursor(buffered=True)
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print('Connected to MySQL database')

        except Error as e:
            print('Error:', e)

    def create_tables(self):
        # Create the 'users' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chat_id INT NOT NULL,
                username VARCHAR(255),
                name VARCHAR(255),
                last_online DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY(chat_id)
            )
        """)

        self.cursor.nextset()
        self.cursor.fetchall()

        # Create the 'favorites' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id),
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        self.cursor.nextset()
        self.cursor.fetchall()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                favorite_id INT,
                last_notification_time DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (favorite_id) REFERENCES favorites(id)
            )
        """)

        self.cursor.nextset()
        self.cursor.fetchall()

        # Create a table to store the items (if it doesn't exist)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                description LONGTEXT,
                type VARCHAR(10),
                image VARCHAR(255),
                link VARCHAR(255),
                season VARCHAR(50),
                episode VARCHAR(50),
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        self.cursor.nextset()
        self.cursor.fetchall()

        # No longer needed for now. Need to implement something in future
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS fmovies_homepage_content (
        #         id INT AUTO_INCREMENT PRIMARY KEY,
        #         content LONGTEXT,
        #         date_added DATETIME,
        #         createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        #         updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        #     );
        # """)

        # self.cursor.nextset()
        # self.cursor.fetchall()

        self.connection.commit()


bot = telebot.TeleBot(TELEGRAM_API_KEY)

# Set up commands and menu options
commands.set_bot_commands(bot)


def bot_polling():
    bot.polling()


def get_homepage_content(url):
    # Create ChromeOptions instance
    chrome_options = Options()

    # Set headless mode
    chrome_options.add_argument("--headless")

    # Initialize the Chrome driver with the headless option
    driver = webdriver.Chrome(options=chrome_options)
    # Set up the Selenium WebDriver (you need to install the appropriate browser driver)
    print('Launching browser to get content...')
    # driver = webdriver.Chrome()

    # Load the webpage
    driver.get(url)

    # Wait for the page to load completely
    wait = WebDriverWait(driver, 60000)
    wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="mw-home"]/div/div[4]')))

    driver.find_element(By.XPATH, '//*[@id="mw-home"]/div/div[4]').click()

    # Wait for the page to load completely
    wait = WebDriverWait(driver, 60000)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'film-poster')))

    # Get the page source after the JavaScript execution
    page_source = driver.page_source
    print('Got content...')

    # Close the browser
    driver.quit()
    print('Closed browser')
    return page_source


def parse_content(content, base_url):
    # Implement your logic to parse the content and extract relevant information
    # Return a list of dictionaries, where each dictionary represents a movie or TV show
    # Example: [{'title': 'Movie 1', 'type': 'Movie', 'image': 'https://example.com/image1.jpg'}, ...]

    # <div class="flw-item"><div class="film-poster"><div class="pick film-poster-quality">HD</div> <img data-src="/_sf/267/84717201.jpg" title="Fast X" alt="hd-Fast X" class="film-poster-img lazyloaded" src="/_sf/267/84717201.jpg"> <a href="https://hd.fmoviesto.site/fast-x" title="Fast X" class="film-poster-ahref flw-item-tip"><i class="fa fa-play"></i></a></div> <div class="film-detail"><h3 class="film-name"><a href="https://hd.fmoviesto.site/fast-x" title="Fast X">Fast X</a></h3> <div class="fd-infor"><span class="fdi-item">2023</span> <span class="dot"></span> <span class="fdi-item fdi-duration">142 min</span> <span class="float-right fdi-type">Movie</span></div> <div class="clearfix"></div></div> <div class="clearfix"></div> <div class="card-movie-info "><div class="title">Fast X</div> <div class="meta"><span class="imdb"><i class="fa fa-star"></i> 6.3</span> <span>2023</span> <span>142 min</span> <span class="text-right"><span class="quality">HD</span></span></div> <div class="desc">Over many missions and against impossible odds, Dom Toretto and his family have outsmarted, out-nerved and outdriven every foe in their path. Now, they confront the most lethal opponent they've ever faced:.</div> <div class="meta"><div><span>Country:</span> <span><a title="United States movies">United States</a></span></div> <div><span>Genre:</span> <span><a title="Action, Adventure, Crime">Action, Adventure, Crime</a></span></div></div> <div class="actions"><a href="https://hd.fmoviesto.site/fast-x" class="watchnow"><i class="fa fa-play"></i> Watch now</a> <div class="clearfix"></div></div></div></div>

    # <div class="flw-item"><div class="film-poster"><div class="pick film-poster-quality">HD</div> <img data-src="/_sf/271/04791654.jpg" title="Let's Get Divorced Season 1" alt="hd-Let's Get Divorced Season 1" class="film-poster-img ls-is-cached lazyloaded" src="/_sf/271/04791654.jpg"> <a href="https://hd.fmoviesto.site/lets-get-divorced-season-1" title="Let's Get Divorced Season 1" class="film-poster-ahref flw-item-tip"><i class="fa fa-play"></i></a></div> <div class="film-detail"><h3 class="film-name"><a href="https://hd.fmoviesto.site/lets-get-divorced-season-1" title="Let's Get Divorced Season 1">Let's Get Divorced Season 1</a></h3> <div class="fd-infor"><span class="fdi-item">SS 1</span> <span class="dot"></span> <span class="fdi-item">EP 9</span> <span class="float-right fdi-type">TV</span></div> <div class="clearfix"></div></div> <div class="clearfix"></div> <div class="card-movie-info "><div class="title">Let's Get Divorced Season 1</div> <div class="meta"><span class="imdb"><i class="fa fa-star"></i> 8.6</span> <span>2023</span> <span>45 min</span> <span class="text-right"><span class="quality">HD</span></span></div> <div class="desc">A mediatised married couple who no longer love each other is highly optimistic about getting a divorce. However, external circumstances will get in their way and they will have no other choice but to work .</div> <div class="meta"><div><span>Country:</span> <span><a title="Japan movies">Japan</a></span></div> <div><span>Genre:</span> <span><a title="Comedy, Drama, Romance">Comedy, Drama, Romance</a></span></div></div> <div class="actions"><a href="https://hd.fmoviesto.site/lets-get-divorced-season-1" class="watchnow"><i class="fa fa-play"></i> Watch now</a> <div class="clearfix"></div></div></div></div>

    items = []

    # # Parse the page source with Beautiful Soup
    # soup = BeautifulSoup(page_source, 'html.parser')

    soup = BeautifulSoup(content, 'html.parser')
    movie_elements = soup.find_all('div', class_='flw-item')

    for element in movie_elements:
        title_element = element.find('h3', class_='film-name').find('a')
        title = title_element.get('title')

        type_element = element.find('span', class_='fdi-type')
        media_type = type_element.text.strip().lower()

        image_element = element.find('img', class_='film-poster-img')
        image_url = base_url + image_element.get('data-src')

        link_element = element.find('a', class_='film-poster-ahref')
        link_url = link_element.get('href')

        description_element = element.find(
            'div', class_='card-movie-info').find('div', class_='desc')
        desc = description_element.text.strip() if description_element else ""

        item = {
            'title': title,
            'description': desc,
            'type': media_type,
            'image': image_url,
            'link': link_url
        }

        if media_type == 'tv':
            fd_infor = element.find('div', class_='fd-infor')
            if fd_infor:
                fdi_items = fd_infor.find_all('span', class_='fdi-item')
                if len(fdi_items) >= 2:
                    # item['season'] = fdi_items[0].text.strip()
                    # item['episode'] = fdi_items[1].text.strip()
                    season_text = fdi_items[0].text.strip()
                    episode_text = fdi_items[1].text.strip()

                    season = re.search(r'\d+', season_text)
                    episode = re.search(r'\d+', episode_text)

                    if season:
                        item['season'] = int(season.group())
                    if episode:
                        item['episode'] = int(episode.group())

        items.append(item)

    return items


def store_items(items):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            print('saving items...')

            length = len(items)
            print('found:', length, 'items')

            # Insert or update the items in the table
            for item in items:
                title = item['title']
                description = item['description']
                item_type = item['type']
                image = item['image']
                link = item['link']
                season = item.get('season', None)
                episode = item.get('episode', None)

                select_query = '''
                SELECT * FROM items WHERE title = %s
                '''
                cursor.execute(select_query, (title,))
                existing_item = cursor.fetchone()

                if existing_item:
                    # Check if the data has changed
                    if (existing_item[3] != description or
                        existing_item[4] != image or
                            existing_item[5] != link or
                            existing_item[6] != season or
                            existing_item[7] != episode):
                        # Item data has changed, update the record
                        update_query = '''
                        UPDATE items SET description = %s, image = %s, link = %s, season = %s, episode = %s, updatedAt = %s WHERE id = %s
                        '''
                        cursor.execute(
                            update_query, (description, image, link, season, episode, datetime.datetime.now(), existing_item[0]))
                        print('existing item updated with data:', item)
                    else:
                        print('existing item data has not changed:', item)
                else:
                    # Item does not exist, insert a new record with createdAt and updatedAt
                    insert_query = '''
                    INSERT INTO items (title, description, type, image, link, season, episode, createdAt, updatedAt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    current_time = datetime.datetime.now()
                    cursor.execute(insert_query, (title, description, item_type, image,
                                                  link, season, episode, current_time, current_time))
                    print('new item saved with data:', item)

            connection.commit()
            cursor.close()

    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            connection.close()


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    last_online = datetime.datetime.fromtimestamp(message.date)

    print(
        f'/start message data: username: {username}, name: {first_name} {last_name}, last_online: {last_online}')

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
                # Add the user to the 'users' table
                insert_query = '''
                INSERT INTO users (chat_id, username, name, last_online) VALUES (%s, %s, %s, %s)
                '''
                cursor.execute(
                    insert_query, (chat_id, username, f"{first_name} {last_name}", last_online))
                connection.commit()

            # Ask the user for their favorite shows
            bot.send_message(chat_id, "What are your favorite shows?")

            user.update_last_online(chat_id)

            cursor.close()
            connection.commit()  # Commit the changes

    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            # Clear any remaining results
            while connection.next_result():
                pass
            connection.close()


def check_new_items():
    print('Starting to check new items')
    base_url = 'https://hd.fmoviesto.site'

    while True:
        current_content = get_homepage_content(base_url)
        new_items = parse_content(current_content, base_url)
        store_items(new_items)
        notification.notify_users(bot)

        # Get the current date and time
        current_datetime = datetime.datetime.now()
        print('Completed one loop of checking the data at:', current_datetime)

        # Wait for some time before checking again (e.g., every hour)
        time.sleep(10800)


def get_latest_saved_content():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Retrieve the latest saved content from the 'fmovies_homepage_content' table
            query = "SELECT content FROM fmovies_homepage_content ORDER BY id DESC LIMIT 1"

            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                content = result[0]
                return content

            return None
    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            # Clear any remaining results
            while connection.next_result():
                pass
            connection.close()


def save_content(content):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Save the content to the 'fmovies_homepage_content' table along with the current date
            query = "INSERT INTO fmovies_homepage_content (content, date_added) VALUES (%s, %s)"
            date_added = datetime.datetime.now()

            cursor = connection.cursor()
            cursor.execute(query, (content, date_added))
            connection.commit()

            print("Content saved successfully!")

    except Error as e:
        print('Error:', e)

    finally:
        if connection and connection.is_connected():
            # Clear any remaining results
            while connection.next_result():
                pass
            connection.close()


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    try:
        if "/add" in text:
            # Remove the "/add" prefix from the message text
            title = text.replace("/add", "").strip()

            # Add the favorite for the user
            add_favorite(chat_id, title)

            # Acknowledge the user's input
            bot.send_message(
                chat_id, f"New favorite show {title} has been added!")

        elif "/remove" in text:
            # Remove the "/remove" prefix from the message text
            title = text.replace("/remove", "").strip()

            # Remove the favorite for the user
            remove_favorite(chat_id, title)

            # Acknowledge the user's input
            bot.send_message(
                chat_id, f"Favorite show {title} has been removed!")

        elif "/list" in text:
            # Get all favorites for the user
            favorites = get_favorites(chat_id)

            if favorites:
                # Generate a formatted list of favorites
                favorites_list = "\n".join(favorites)

                # Send the list of favorites to the user
                bot.send_message(chat_id, "Your favorites:\n" + favorites_list)
            else:
                bot.send_message(chat_id, "You have no favorites yet!")

        else:
            # Print the message in the console
            print("Received message:", text)

    except Error as e:
        print('Error:', e)

    finally:
        user.update_last_online(chat_id)


if __name__ == '__main__':
    mysql_connector = MySQLConnector(
        MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
    mysql_connector.connect()
    # mysql_connector.create_tables()
    mysql_connector.create_tables()
    threading.Thread(target=bot_polling).start()
    check_new_items()
    # bot.polling()
    # try:
    # bot.polling()
    # except KeyboardInterrupt:
    #     bot.stop_polling()
