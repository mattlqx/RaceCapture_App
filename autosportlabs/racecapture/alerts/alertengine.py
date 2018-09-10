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

from autosportlabs.racecapture.alerts.alertcontrollers import AlertActionControllerFactory

class AlertEngine(object):

    def __init__(self, dashboard_state, **kwargs):
        self.dashboard_state = dashboard_state
        # Map of AlertRuleCollection by channel name
        self.rule_collections = {}

        self.alert_controllers = {}

        def process_rules(channel, value):
            alertrule_collection = self.rule_collections.get(channel)

            if alertrule_collection is None:
                # no rules defined for this channel
                return

            # check what might be activated or deactivated
            active_rules, deactive_rules = alertrule_collection.check_rules(value)

            for rule in active_rules:
                for alertaction in rule.alert_actions:
                    if not alertaction.is_active:
                        # trigger the action once
                        controller = self._get_alert_controller(alertaction)
                        controller.activate(alertaction)
                        alertaction.is_active = True

            for rule in deactive_rules:
                for alertaction in rule.alert_actions:
                    if alertaction.is_active:
                        # disable the action once
                        controller = self._get_alert_controller(alertaction)
                        controller.deactivate(alertaction)
                        alertaction.is_active = False

        def _get_alert_controller(self, alertaction):
            name = alertaction.__class__.___name__
            controller = self.alert_controllers.get(name)
            if controller is None:
                controller = AlertActionControllerFactory.create_controller(dashboard_state)
                self.alert_controllers.set(dashboard_state)

            return controller

