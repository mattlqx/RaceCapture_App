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

from datetime import datetime

"""
Describes a rule for an individual alert. Defines the sensor channel 
low and high threshold value (inclusive) as well as the timing 
activation / deactivation thresholds for used for triggering
"""
class AlertRule(object):
    def __init__(self, enabled, low_threshold, high_threshold, activate_sec, deactivate_sec):
        self._enabled = enabled
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.activate_sec = activate_sec
        self.deactivate_sec = deactivate_sec

        self.activate_start = None
        self.deactivate_start = None
        self._is_active = False

    """ Test for alert activation, sets the is_active property if active
    :param float value: The value to test
    :return: True if the alert rule is activated
    :rtype bool
    """
    def should_activate(self, value):
        if not self.enabled:
            return False

        if not self.is_within_threshold(value):
            self.activate_start = None
            return False

        if not self.activate_start:
            self.activate_start = datetime.now()
            return False

        should_activate = (datetime.now() - self.activate_start).total_seconds() > self.activate_sec
        if not self.is_active and should_activate:
            self._is_active = True

        return should_activate


    """ Test for alert de-activation
    :param float value: The value to test
    :return: True if the alert rule is de-activated
    :rtype bool
    """
    def should_deactivate(self, value):
        if self.is_within_threshold(value):
            self.deactivate_start = None
            return False

        if not self.deactivate_start:
            self.deactivate_start = datetime.now()
            return False

        should_deactivate = (datetime.now() - self.deactivate_start).total_seconds() > self.deactivate_sec
        if self.is_active and should_deactivate:
            self._is_active = False

        return should_deactivate

    """ Test if the value is within the alert threshold
    :param float value: The value to test
    :return: True if the value is within the threshold
    :rtype bool 
    """
    def is_within_threshold(self, value):
        return value <= self.high_threshold and value >= self.low_threshold

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        self._is_active = False

    @property
    def is_active(self):
        return self._is_active

"""
Describes an an alert action that specifies a color to activate
"""
class ColorAlertAction(object):
    def __init__(self, color_rgb):
        self.color_rgb = color_rgb

"""
Describes an alert action that takes the form of a popup message
"""
class PopupAlertAction(object):
    def __init__(self, message, shape, color_rgb, alarm_sound):
        self.message = message
        self.shape = shape
        self.color_rgb = color_rgb
        self.alarm_sound = alarm_sound

"""
Describes a collection of rules for a specified channel
"""
class AlertRuleCollection(object):
    def __init__(self, channel_name, enabled, alert_rules=[]):
        self.channel_name = channel_name
        self.enabled = enabled
        self.alert_rules = alert_rules

    def get_active_alert_rules(self, value):
        active_rules = []
        for alert_rule in self.alert_rules:
            if alert_rule.should_activate(value):
                active_rules.append(alert_rule)
        return active_rules

