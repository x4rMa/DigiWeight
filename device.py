import serial
import string
import time

import settings


# Connect to the serial port
if settings.DEBUG:
    serial_connection = None
else:
    serial_connection = serial.Serial(
        port = settings.SERIAL_PORT,
        baudrate = settings.SERIAL_BAUDRATE,
        parity = settings.SERIAL_PARITY,
        stopbits = settings.SERIAL_STOPBITS,
        bytesize = settings.SERIAL_BYTESIZE,
        timeout = 1
        )


def is_valid_line(string):
    """Parse and validate a line from serial device.

    A valid line must be 30 chars long and is supposed to have this
    structure:
    
    $   +0.123     +0.123   kg 0210\r\n
    |-|---------|-|---------|-|--|-|----|-|-|

     ^ leading $
       ^ net weight
                 ^ space
                   ^ tare weight
                             ^ space
                               ^ unit of measure
                                  ^ space
                                    ^ status code
                                         ^ \r
                                           ^ \n

    Return the weight in grams or false if something goes wrong.
    """

    if len(string) != 30:
        return False

    first_char = string[0]
    weight = string[1:10]
    unit = string[21:23]
    status = string[24:28]
    last_char = string[29]

    if first_char != '$':
        return False

    weight = weight.strip()
    weight = weight.replace(',', '.')
    try:
        weight = float(weight)
    except ValueError:
        return False

    unit = unit.strip()
    if unit != 'kg':
        return False

    if status[0] == '9':
        return False
    if status[1] != '2':
        return False
    if last_char != '\n':
        return False

    # weight must be converted from kilo to gram
    weight *= 1000

    return weight


def read_weight():
    """Read weight from serial device. Output in grams."""

    if settings.DEBUG:
        return 0

    # Clean serial device input
    serial_connection.flushInput()
	
    # Listen to serial port until timeout is reached
    start_time = time.clock()
    timeout = 1
    while time.clock() - start_time < timeout:
        line = serial_connection.readline()
        weight = is_valid_line(line)
        if weight:
            break
    
    return weight
