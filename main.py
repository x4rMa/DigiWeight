import datetime
import string
import textwrap

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import kivy
import pyodbc

from database import db_connection, get_daily_stats, set_daily_stats, item_list
from device import read_weight
from printer import print_label
import settings


# Kivy required version
kivy.require('1.5.1')


# Kivy config settings
Config.set('graphics', 'fullscreen', 'auto')
Config.write()


class InfoPopup(Popup):
    """A popup to display usage statistics and credits."""
    daily_weight = NumericProperty(0)
    daily_counter = NumericProperty(0)
    date = StringProperty('')


class ErrorPopup(Popup):
    """A popup to display errors."""
    error = StringProperty('')


class PrintPopup(Popup):
    """A popup to ask confirm and send data to printer."""
    item = ObjectProperty(0)
    weight = NumericProperty(0)
    date = StringProperty('')

    def print_and_close(self):
        """Print data and close popup."""
        data = {
            'product': self.item.slug(),
            'weight': self.weight,
            'date': self.date
            }
        print_label(data)
        set_daily_stats(self.date, self.weight)
        self.dismiss()


class GridButton(Button):
    """A button to print a label."""
    item = ObjectProperty(None)
    
    def on_touch_down(self, touch):
        """Read weight data and open a confirm dialog."""
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            current_date = datetime.date.today().strftime('%d-%m-%Y')
            weight = read_weight()
            if weight:
                print_popup = PrintPopup(
                    item=self.item, weight=weight, date=current_date
                    )
                print_popup.open()
            else:
                error_popup = ErrorPopup(error='No serial device connected')
                error_popup.open()
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
        """Collect data and display them in a popup."""

        current_date = datetime.date.today().strftime('%d-%m-%Y')
        daily_stats = get_daily_stats(current_date)
        # Daily weight summary
        daily_weight = daily_stats['weight']
        # Daily label counter
        daily_counter = daily_stats['counter']
        # Display data in a popup
        info_popup = InfoPopup(
            daily_weight=daily_weight,
            daily_counter=daily_counter,
            date=current_date
            )
        info_popup.open()


class DigiWeightApp(App):
    """The App class as needed by Kivy."""

    def build(self):
        return DigiWeightRoot()


if __name__ == '__main__':
    DigiWeightApp().run()
