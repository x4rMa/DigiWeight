DigiWeight
==========

Intro
-----

DigiWeight software is used to manage a digital weighing device
through a touch panel computer. After each weighing, summary labels
can be printed reporting weight, date and item category.

Workflow
--------

At start-up DigiWeight software looks for possible item categories
from a database and displays them on the screen.

After selecting a category from the display, the user start the
weighing process.

As soon as an item is put on the scale, DigiWeight reads the weight
from the serial connection, produces a PDF label and sends it to the
printer.

Requirements
------------

DigiWeight is written in Python and makes use of the Kivy_
framework. Database connection requires the PyODBC_ library. Serial
device connection requires the PySerial_ library.

.. _Kivy: http://kivy.org/
.. _PyODBC: https://github.com/mkleehammer/pyodbc
.. _PySerial: https://pypi.python.org/pypi/pyserial
