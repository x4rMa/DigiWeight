from collections import namedtuple
import datetime
import pyodbc
import string

import settings


# A useful namedtuple to handle database items
DbTuple = namedtuple('DbTuple', ['code', 'description'], verbose=True)

class DbClass(DbTuple):
    """
    A class for database items.

    This class is meant to contain database items and is made out of a
    simple namedtuple plus a custom slug method.
    """

    def slug(self):
        slug = self.description.strip(' ,.\n\t\r')
        slug = string.capwords(slug)
        return slug

# Connect to the database
if settings.DEBUG:
    # Debug mode: suppose to be on GNU/Linux
    db_connection = pyodbc.connect(
        'DRIVER=%s;DSN=%s;UID=%s;PWD=%s' % (
            settings.DB_DRIVER_UNIX,
            settings.DB_DSN,
            settings.DB_USERNAME,
            settings.DB_PASSWORD
            )
        )
else:
    # Production mode: suppose to be on Windows
    db_connection = pyodbc.connect(
        'DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (
            settings.DB_DRIVER_WINDOWS,
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD
            )
        )
cursor = db_connection.cursor().execute(
    "select %s from %s" % (
        settings.DB_FIELDS,
        settings.DB_TABLE
        )
    )

# Store database items in a list
item_list = [DbClass(i[0], i[1]) for i in cursor]


def get_daily_stats(date):
    """Look up into the database and retrieve daily statistics.
    
    Retrieved statistics are weight and counter summaries which are
    calculated and saved to the database on a daily basis."""

    # Look up into the database for current values
    cursor = db_connection.cursor().execute(
        "select counter, weight, date from %s where date='%s'" % (
            settings.DB_STATS_TABLE,
            date
            )
        ).fetchall()
    # Are there any data available for current date?
    cursor_length = len(cursor)
    if cursor_length == 0: # No, there are not
        current_counter = 0
        current_weight = 0
    elif cursor_length == 1: # Yes, there is 1 match
        current_counter = cursor[0][0]
        current_weight = cursor[0][1]
    else: # There are too many matches!
        raise Exception("Date column must be unique in database stats table")
    
    try:
        current_weight = float(current_weight)
    except ValueError:
        current_weight = 0

    return {
        'counter': current_counter,
        'weight': current_weight,
        }


def set_daily_stats(date, weight):
    """Save daily statistics to the database.

    Retrieved statistics are weight and counter summaries which are
    calculated and saved to the database on a daily basis."""

    # Look up into the database for current values
    stats = get_daily_stats(date)

    # New values
    new_weight = stats['weight'] + weight
    new_counter = stats['counter'] + 1
    
    # Update the database
    cursor = db_connection.cursor().execute(
        "UPDATE %s SET counter=%s, weight=%s, date='%s'" % (
            settings.DB_STATS_TABLE,
            new_counter,
            new_weight,
            date
            )
        )
    db_connection.commit()
