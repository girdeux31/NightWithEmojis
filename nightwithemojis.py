import os
import time
import tweepy
import numpy as np
from dotenv import load_dotenv

# load environment variables

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
SLEEPING_TIME = int(os.getenv('SLEEPING_TIME'))

# define some parameters

rows = 10    # canvas size
columns = 10

p_dark_bk_upper = 0.5  # probabilities
p_dinosaurs_upper = 0.2

stars_and_clouds = 14  # number of objects
people_bounds = [2, 4]
dinosaurs_bounds = [2, 4]
vegetation_bounds = [2, 4]
moon_bounds = [1, 1]

infinite_loop = True

################

# define classes

class Emoji:

    def __init__(self, emoji, name, p_low=0.0, p_high=1.0):

        self.text = emoji
        self.name = name
        self.p_low = p_low
        self.p_high = p_high

    def __str__(self):

        return f'{self.name}: {self.text}'


class Collection:

    def __init__(self, emojis, repetitions, rows, columns, diverse=False):

        self.emojis = emojis
        self.repetitions = repetitions
        self.rows = [rows[0], rows[1]] if isinstance(rows, list) else [rows, rows]
        self.columns = [columns[0], columns[1]] if isinstance(columns, list) else [columns, columns]
        self.diverse = diverse

    def get_emoji(self, p):

        for emoji in self.emojis:

            if emoji.p_low <= p < emoji.p_high:

                return emoji


class Canvas:

    def __init__(self, rows, columns):

        self.rows = rows
        self.columns = columns
        self.mesh = np.full([rows, columns], fill_value=emoji_background)  # initialize array with spaces

    def to_text(self):

        text = ''

        for idx in range(self.rows):

            for emoji in self.mesh[idx, :]:

                text += emoji.text

            text += '\n'

        return text

    def get_background_position_between(self, rows, columns):

        # return random integers from low (inclusive) to high (exclusive)
        row = np.random.randint(low=rows[0], high=rows[1]+1)
        column = np.random.randint(low=columns[0], high=columns[1]+1)

        while not self.is_background(row, column):

            row = np.random.randint(low=rows[0], high=rows[1]+1)
            column = np.random.randint(low=columns[0], high=columns[1]+1)

        return row, column

    def set_emoji(self, emoji, row, column):

        self.mesh[row - 1, column - 1] = emoji

    def get_emoji(self, row, column):

        return self.mesh[row - 1, column - 1]

    def is_background(self, row, column):

        return True if self.get_emoji(row, column).name == 'background' else False


if __name__ == '__main__':

    # create emoji lists

    emoji_moons = list()
    emoji_moons.append(Emoji('🌑', 'new', p_low=0, p_high=2/10))
    emoji_moons.append(Emoji('🌕', 'full', p_low=2/10, p_high=4/10))
    emoji_moons.append(Emoji('🌗', 'last quarter', p_low=4/10, p_high=5/10))
    emoji_moons.append(Emoji('🌓', 'first quarter', p_low=5/10, p_high=6/10))
    emoji_moons.append(Emoji('🌖', 'waning gibbous', p_low=6/10, p_high=7/10))
    emoji_moons.append(Emoji('🌔', 'waxing gibbous', p_low=7/10, p_high=8/10))
    emoji_moons.append(Emoji('🌘', 'waning crescent', p_low=8/10, p_high=9/10))
    emoji_moons.append(Emoji('🌒', 'waxing crescent', p_low=9/10, p_high=10/10))

    emoji_stars = list()
    emoji_stars.append(Emoji('⭐', 'medium', p_low=0, p_high=2/7))
    emoji_stars.append(Emoji('🌟', 'glowing', p_low=2/7, p_high=4/7))
    emoji_stars.append(Emoji('✨', 'sparkles', p_low=4/7, p_high=6/7))
    emoji_stars.append(Emoji('️💫', 'dizzy', p_low=6/7, p_high=7/7))

    emoji_clouds = list()
    emoji_clouds.append(Emoji('☁', 'cloud', p_low=0, p_high=3/4))
    emoji_clouds.append(Emoji('️🌧', 'cloud rain', p_low=3/4, p_high=4/4))

    emoji_people = list()
    emoji_people.append(Emoji('🧍‍♂️', 'man standing', p_low=0, p_high=1/9))
    emoji_people.append(Emoji('🚶‍♂️', 'man walking', p_low=1/9, p_high=2/9))
    emoji_people.append(Emoji('🏃‍♂️', 'man running', p_low=2/9, p_high=3/9))
    emoji_people.append(Emoji('🧍‍♀️', 'woman standing', p_low=3/9, p_high=4/9))
    emoji_people.append(Emoji('🚶‍♀️', 'woman walking', p_low=4/9, p_high=5/9))
    emoji_people.append(Emoji('🏃‍♀️', 'woman running', p_low=5/9, p_high=6/9))
    emoji_people.append(Emoji('👬', 'couple gay', p_low=6/9, p_high=7/9))
    emoji_people.append(Emoji('👭', 'couple lesbian', p_low=7/9, p_high=8/9))
    emoji_people.append(Emoji('👫', 'couple hetero', p_low=8/9, p_high=9/9))

    emoji_dinosaurs = list()
    emoji_dinosaurs.append(Emoji('🦕', 'sauropod', p_low=0, p_high=1/2))
    emoji_dinosaurs.append(Emoji('🦖', 't-rex', p_low=1/2, p_high=2/2))

    emoji_vegetation = list()
    emoji_vegetation.append(Emoji('️️🌺', 'hibiscus', p_low=0, p_high=2/11))
    emoji_vegetation.append(Emoji('️🍄', 'mushroom', p_low=2/11, p_high=4/11))
    emoji_vegetation.append(Emoji('🌲', 'evergreen', p_low=4/11, p_high=6/11))
    emoji_vegetation.append(Emoji('🌴', 'palm', p_low=6/11, p_high=8/11))
    emoji_vegetation.append(Emoji('🌵', 'cactus', p_low=8/11, p_high=11/11))

    emoji_squares = list()
    emoji_squares.append(Emoji('🟥', 'red', p_low=0, p_high=1/6))
    emoji_squares.append(Emoji('🟧', 'orange', p_low=1/6, p_high=2/6))
    emoji_squares.append(Emoji('🟨', 'yellow', p_low=2/6, p_high=3/6))
    emoji_squares.append(Emoji('🟩', 'green', p_low=3/6, p_high=4/6))
    emoji_squares.append(Emoji('🟦', 'blue', p_low=4/6, p_high=5/6))
    emoji_squares.append(Emoji('🟪', 'purple', p_low=5/6, p_high=6/6))

    while True:

        # define more parameters

        stars = np.random.randint(low=0, high=stars_and_clouds+1)
        clouds = stars_and_clouds - stars
        people = np.random.randint(low=people_bounds[0], high=people_bounds[1]+1)
        dinosaurs = np.random.randint(low=dinosaurs_bounds[0], high=dinosaurs_bounds[1]+1)
        vegetations = np.random.randint(low=vegetation_bounds[0], high=vegetation_bounds[1]+1)
        moons = np.random.randint(low=moon_bounds[0], high=moon_bounds[1]+1)

        p_dinosaurs = np.random.uniform()
        p_dark_bk = np.random.uniform()

        # create collection of emoji lists

        collections = dict()
        collections['moons'] = Collection(emoji_moons, repetitions=moons, rows=[2, rows-4], columns=[2, columns-1])
        collections['stars'] = Collection(emoji_stars, repetitions=stars, rows=[1, rows-3], columns=[2, columns-1])
        collections['clouds'] = Collection(emoji_clouds, repetitions=clouds, rows=[2, rows-3], columns=[1, columns])
        collections['vegetation'] = Collection(emoji_vegetation, repetitions=vegetations, rows=rows-1, columns=[1, columns])
        collections['squares'] = Collection(emoji_squares, repetitions=columns, rows=rows, columns=[1, columns])

        # add people or dinosaurs

        if p_dinosaurs <= p_dinosaurs_upper:
            collections['dinosaurs'] = Collection(emoji_dinosaurs, repetitions=dinosaurs, rows=rows-1, columns=[1, columns], diverse=True)
        else:
            collections['people'] = Collection(emoji_people, repetitions=people, rows=rows-1, columns=[1, columns], diverse=True)

        # define background

        emoji_background = Emoji('⬛️', 'background') if p_dark_bk <= p_dark_bk_upper else Emoji('⬜️', 'background')

        # place objects in mesh

        canvas = Canvas(rows, columns)

        for collection in collections.values():

            for repetition in range(collection.repetitions):

                if repetition == 0 or collection.diverse:  # get a new emoji if this is first repetition or collection is diverse

                    probability = np.random.uniform()  # uniformly distributed over [0, 1) (includes low, but excludes high)
                    emoji = collection.get_emoji(probability)

                row, column = canvas.get_background_position_between(collection.rows, collection.columns)
                canvas.set_emoji(emoji, row, column)

        # convert object to tweet text

        tweet = canvas.to_text()

        # print(tweet)
        # print(len(tweet))

        try:

            # authenticate client and post tweet
            client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, 
                                   access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
            
            client.create_tweet(text=tweet)

            print(f'Tweet at {time.strftime("%Y-%m-%d %H:%M:%S")}')

        except Exception as error:

            print(f'Error sending tweet, its length is {len(tweet)}')
            print('Error is ' + str(error))

        # put to sleep

        if infinite_loop:
            time.sleep(SLEEPING_TIME)
        else:
            break
 