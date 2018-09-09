#
# Race Capture App
#
# Copyright (C) 2014-2017 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.

class BaseAlertAction(object):
    def __init__(self):
        self.is_active = False
"""
Describes an an alert action that specifies a color to activate
"""

class ColorAlertAction(object):
    def __init__(self, color_rgb, **kwargs):
        super(ColorAlertAction, self).__init__(**kwargs)
        """
        :param array color_rgb: array of R,G,B values
        """
        self.color_rgb = color_rgb

    @property
    def title(self):
        return 'Set Gauge Color'

"""
Describes an alert action that takes the form of a popup message
"""
class PopupAlertAction(ColorAlertAction):
    def __init__(self, color_rgb, message, shape, **kwargs):
        """
        :param string message: The message to display
        :param string shape: the name of the shape to display('triangle', 'octagon'). if None, no shape will be displayed
        :param array color_rgb: array of R,G,B values
        """
        super(PopupAlertAction, self).__init__(color_rgb, **kwargs)
        self.message = message
        self.shape = shape

    @property
    def title(self):
        return 'Popup: "{}"'.format(self.message)

class LedAlertAction(ColorAlertAction):
    def __init__(self, color_rgb, led_position, flash_rate, **kwargs):
        """
        :param string led_position: The position of the led('left', 'right')
        :param integer flash_rate: The Rate of flash in Hz. 0 = solid (no flash)
        :param array color_rgb: array of R,G,B values
        """
        super(LedAlertAction, self).__init__(color_rgb, **kwargs)
        self.led_position = led_position
        self.flash_rate = flash_rate

    @property
    def title(self):
        return 'Set Alert LED'


class ShiftLightAlertAction(ColorAlertAction):
    def __init__(self, color_rgb, flash_rate, **kwargs):
        """
        :param integer flash_rate: The Rate of flash in Hz. 0 = solid (no flash)        
        :param array color_rgb: array of R,G,B values
        """
        super(ShiftLightAlertAction, self).__init__(color_rgb, **kwargs)
        self.flash_rate = flash_rate

    @property
    def title(self):
        return 'Set Shift Light'

def get_alertaction_default_collection():
    return [
        PopupAlertAction(message='Alert', shape=None, color_rgb=[1, 0, 0]),
        ColorAlertAction(color_rgb=[1, 0, 0]),
        ShiftLightAlertAction(flash_rate=0, color_rgb=[1, 0, 0]),
        LedAlertAction(led_position='left', flash_rate=0, color_rgb=[1, 0, 0])
        ]
