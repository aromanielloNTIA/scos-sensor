# -*- coding: utf-8 -*-

from django.apps import AppConfig
import logging
from scos_actions.actions.interfaces.signals import (
    location_action_completed,
    measurement_action_completed,
)

logger = logging.getLogger(__name__)


class HandlersConfig(AppConfig):
    name = "handlers"

    def ready(self):
        from handlers.measurement_handler import measurement_action_completed_callback
        from handlers.location_handler import location_action_completed_callback

        measurement_action_completed.connect(measurement_action_completed_callback)
        logger.debug(
            "measurement_action_completed_callback registered to measurement_action_completed"
        )
        location_action_completed.connect(location_action_completed_callback)
        logger.debug(
            "location_action_completed_callback registered to location_action_completed"
        )