import time
import random

SAMPLE_STRING = "$    0,340     0,000 kg 0200"

while True:

    # Some random weight
    weight = "%.3f" % random.uniform(0, 20)
    is_over_threshold = "%d" % random.randint(0, 1)
    is_stable = "%d" % random.randint(1, 2)
    # Padding with spaces
    weight = weight.rjust(9)
    # Comma instead of a dot as a decimal separator
    weight = weight.replace('.', ',')

    counter = 0
    while counter < 3:
        print "$%s     0,000 kg %s%s00" % (weight, is_over_threshold, is_stable)
        time.sleep(.3)
        counter += 1
