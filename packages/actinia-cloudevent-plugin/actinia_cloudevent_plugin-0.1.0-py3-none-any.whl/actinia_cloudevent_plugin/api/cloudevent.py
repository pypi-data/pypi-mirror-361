#!/usr/bin/env python
"""Copyright (c) 2025 mundialis GmbH & Co. KG.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Hello World class
"""

__license__ = "GPLv3"
__author__ = "Lina Krisztian"
__copyright__ = "Copyright 2025 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"

from flask import jsonify, make_response
from flask_restful_swagger_2 import Resource, swagger
from requests.exceptions import ConnectionError  # noqa: A004

from actinia_cloudevent_plugin.apidocs import cloudevent
from actinia_cloudevent_plugin.core.processing import (
    cloud_event_to_process_chain,
    receive_cloud_event,
    send_binary_cloud_event,
    # send_structured_cloud_event,
)
from actinia_cloudevent_plugin.model.response_models import (
    SimpleStatusCodeResponseModel,
)
from actinia_cloudevent_plugin.resources.config import EVENTRECEIVER


class Cloudevent(Resource):
    """Cloudevent handling."""

    def __init__(self) -> None:
        """Cloudevent class initialisation."""
        self.msg = (
            "Received event <EVENT1> and returned event <EVENT2>"
            " with actinia-job <ACTINIA_JOB>."
        )

    def get(self):
        """Cloudevent get method: not allowed response."""
        res = jsonify(
            SimpleStatusCodeResponseModel(
                status=405,
                message="Method Not Allowed",
            ),
        )
        return make_response(res, 405)

    @swagger.doc(cloudevent.describe_cloudevent_post_docs)
    def post(self) -> SimpleStatusCodeResponseModel:
        """Cloudevent post method with cloudevent from postbody.

        Receives cloudevent, transforms to process chain (pc),
        sends pc to actinia + start process,
        and returns cloudevent with queue name.
        """
        # Transform postbody to cloudevent
        event_received = receive_cloud_event()
        # With received process chain start actinia process + return cloudevent
        actinia_job = cloud_event_to_process_chain(event_received)
        # URL to which the generated cloudevent is sent
        url = EVENTRECEIVER.url
        # TODO: binary or structured cloud event?
        # From https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md#message
        # A "structured-mode message" is one where the entire event (attributes and data)
        # are encoded in the message body, according to a specific event format.
        # A "binary-mode message" is one where the event data is stored in the message body,
        # and event attributes are stored as part of message metadata.
        # Often, binary mode is used when the producer of the CloudEvent wishes to add the
        # CloudEvent's metadata to an existing event without impacting the message's body.
        # In most cases a CloudEvent encoded as a binary-mode message will not break an
        # existing receiver's processing of the event because the message's metadata
        # typically allows for extension attributes.
        # In other words, a binary formatted CloudEvent would work for both
        # a CloudEvents enabled receiver as well as one that is unaware of CloudEvents.
        try:
            event_returned = send_binary_cloud_event(
                event_received,
                actinia_job,
                url,
            )
            return SimpleStatusCodeResponseModel(
                status=204,
                message=self.msg.replace("<EVENT1>", event_received["id"])
                .replace("<EVENT2>", event_returned["id"])
                .replace("<ACTINIA_JOB>", actinia_job),
            )
        except ConnectionError as e:
            return f"Connection ERROR when returning cloudevent: {e}"
        except Exception() as e:
            return f"ERROR when returning cloudevent: {e}"
