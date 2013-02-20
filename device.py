import serial
import string
import time

import settings


# Connect to the serial port
serial_connection = serial.Serial(
    port = settings.SERIAL_PORT,
    baudrate = settings.SERIAL_BAUDRATE,
    parity = settings.SERIAL_PARITY,
    stopbits = settings.SERIAL_STOPBITS,
    bytesize = settings.SERIAL_BYTESIZE,
    timeout = 1
    )

def read_weight():
    """Read weight from serial device.

    Read a line from serial connection and make sure it complies with
    this structure:
    
     $    +0.123      +0.123   kg   0210 r n
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

    Return the weight in grams, tell if it is a significant (over
    threshold) value and if it has been stable for a while.
    """

    # Clean serial device input
    serial_connection.flushInput()

    # Read a line from serial connection
    line = serial_connection.readline()

    first_char = line[0]
    weight = line[1:10]
    unit = line[21:23]
    status = line[24:28]
    last_char = line[29]

    if first_char != '$' or unit != 'kg' or last_char != '\n':
        raise ValueError

    weight = weight.strip()
    weight = weight.replace(',', '.')
    weight = float(weight)
    # Convert kilograms to grams
    weight *= 1000

    is_stable_over_threshold = False
    is_stable_under_threshold = False
    if status[1] == '2':
        if status[0] == '0':
            is_stable_over_threshold = True
        else:
            is_stable_under_threshold = True

    return weight, is_stable_over_threshold, is_stable_under_threshold
