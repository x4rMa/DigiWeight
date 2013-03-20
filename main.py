import datetime
import string
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import \
    ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import kivy

from database import db_connection, update_stats, item_list
from device import read_weight, serial_connection
from printer import print_label
import settings


# Kivy required version
kivy.require('1.5.1')


# Kivy config settings
if settings.DEBUG:
    Config.set('graphics', 'fullscreen', '0')
else:
    Config.set('graphics', 'fullscreen', 'auto')
Config.write()


class InfoPopup(Popup):
    """Display software info and credits."""

    pass


class ErrorPopup(Popup):
    """Display errors."""

    error = StringProperty('')


class PrintPopup(Popup):
    """A popup to ask confirm and send data to printer."""

    item = ObjectProperty(None)
    weight = NumericProperty(0)
    date = StringProperty('')
    is_ready_to_print = BooleanProperty(True)

    def update(self, dt):
        """Read weight, update popup, print label.

        As soon as the popup is created, start reading weight from
        serial device at regular intervals.

        If weight is greater than a minimum threshold and is stable,
        print a label.

        Before printing a second label, weight must become zero (first
        item away from the scales) and then non-zero again (a new item
        on the scales).
        """

        try:
            (weight,
             is_stable_over_threshold,
             is_stable_under_threshold) = read_weight()
        except (IndexError, ValueError) as e:
            return

        self.weight = weight

        if not self.is_ready_to_print and is_stable_under_threshold:
            self.is_ready_to_print = True

        elif self.is_ready_to_print and is_stable_over_threshold:
            data = {
                'product': self.item.slug(),
                'weight': self.weight,
                'date': self.date
                }
            self.is_ready_to_print = False
            # Microsoft Windows console can only display 256 chars and
            # will raise a ``UnicodeEncodeError`` exception for
            # certain product names. See
            # http://wiki.python.org/moin/PrintFails for details.
            try:
                print "Print label for product: %s with weight: %s" % (
                    data['product'], data['weight']
                    )
            except UnicodeEncodeError:
                print "Print label with weight: %s" % data['weight']
            print_label(data)
            update_stats(self.item.id, self.date, self.weight)

    def start(self, *args):
        """Start scheduled actions when popup opens."""

        Clock.schedule_interval(self.update, 1.0/60.0)

    def stop(self, *args):
        """Stop scheduled actions when popup closes."""

        Clock.unschedule(self.update)


class GridButton(Button):
    """A button to print a label."""

    item = ObjectProperty(None)
    
    def on_touch_down(self, touch):
        """Read weight data and open a confirm dialog."""

        if self.collide_point(*touch.pos) and touch.is_double_tap:
            current_date = datetime.date.today().strftime('%d-%m-%Y')
            print_popup = PrintPopup(item=self.item, date=current_date)
            print_popup.bind(on_open = print_popup.start)
            print_popup.bind(on_dismiss = print_popup.stop)
            print_popup.open()
            return True
        return super(GridButton, self).on_touch_down(touch)


class DigiWeightRoot(GridLayout):
    """The root widget.

    A nested GridLayout is created through the Kivy language file and
    then later populated with buttons. Look at this in `Kivy docs`_.

    `Kivy docs`_: http://kivy.org/docs/guide/designwithkv.html"""

    # An object property to link to the nested GridLayout
    container = ObjectProperty(None)
    
    def on_container(self, instance, value):
        """Populate the nested GridLayout with buttons.

        Look at this feature in `Kivy docs`_.

        `Kivy docs`_: http://kivy.org/docs/api-kivy.properties.html#observe-using-on-propname"""
        
        # The container has been set: buttons can be added
        for item in item_list:
            button = GridButton(item=item)
            self.container.add_widget(button)

    def open_info_popup(self):
        """Display info in a popup."""

        info_popup = InfoPopup()
        info_popup.open()


class DigiWeightApp(App):
    """The App class as needed by Kivy."""

    def build(self):
        return DigiWeightRoot()


if __name__ == '__main__':
    DigiWeightApp().run()
