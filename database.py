from collections import namedtuple
import datetime
import pyodbc
import string

import settings


# A useful namedtuple to handle database items
DbTuple = namedtuple('DbTuple', ['id', 'description'], verbose=True)

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
            settings.DB_SERVER_IP,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD
            )
        )
cursor = db_connection.cursor().execute(
    "select %s from %s" % (
        settings.DB_TABLE_FIELDS,
        settings.DB_TABLE
        )
    )

# Store database items in a list
item_list = [DbClass(i[0], i[1]) for i in cursor]

# Create statistics table if missing
cursor = db_connection.cursor().execute(
"""
IF NOT EXISTS (
  SELECT * FROM sysobjects WHERE id = object_id(N'%s')
  AND OBJECTPROPERTY(id, N'IsUserTable') = 1
)
CREATE TABLE %s (
  item_id uniqueidentifier NOT NULL,
  date date NOT NULL,
  counter int NOT NULL,
  weight int NOT NULL,
  CONSTRAINT pk PRIMARY KEY (item_id, date),
  FOREIGN KEY (item_id) REFERENCES %s(%s)
);
""" % (
        settings.DB_STATS_TABLE,
        settings.DB_STATS_TABLE,
        settings.DB_TABLE,
        settings.DB_TABLE_PK
        )
)
db_connection.commit()

def update_stats(item_id, date, weight):
    """Update daily statistics on the database.

    Statistics are weight and counter summaries which are calculated
    and saved to the database for each item on a daily basis.

    Input date format is ``'%d-%m-%Y'`` and must be changed to
    ``'%d-%m-%Y'`` before database insert/update.
    """

    # Format date to fit database
    date = datetime.datetime.strptime(date, '%d-%m-%Y').date()
    date = date.strftime('%Y-%m-%d')

    # Insert new values or update old ones
    cursor = db_connection.cursor().execute(
"""
update %s set counter=counter+1, weight=weight+? where item_id=? and date=?
if (@@rowcount = 0)
begin
    insert into %s (counter, weight, item_id, date) values (1, ?, ?, ?)
end
""" % (settings.DB_STATS_TABLE, settings.DB_STATS_TABLE),
(weight, item_id, date,
 weight, item_id, date,)
)
    db_connection.commit()
