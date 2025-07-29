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

Example core functionality
"""

__license__ = "GPLv3"
__author__ = "Lina Krisztian"
__copyright__ = "Copyright 2025 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


import requests
from cloudevents.conversion import to_binary, to_structured
from cloudevents.http import CloudEvent, from_http
from flask import request


def receive_cloud_event():
    """Return cloudevent from postpody."""
    # Parses CloudEvent 'data' and 'headers' into a CloudEvent.
    event = from_http(request.headers, request.get_data())

    # ? TODO
    # eventually Filter the event (see example below)
    event_type = event["type"]
    if event_type == "com.example.object.created":
        print("Object created event received!")

    return event


def cloud_event_to_process_chain(event) -> str:
    """Return queue name for process chain of event."""
    # (Remove ruff-exception, when pc variable used)
    pc = event.get_data()["list"][0]  # noqa: F841
    # !! TODO !!: pc to job
    # NOTE: as standalone app -> consider for queue name creation
    # HTTP POST pc to actinia-module plugin processing endpoint
    # # # include an identifier for grouping cloudevents of same actinia process (?)
    # # # (e.g. new metadata field "queue_name", or within data, or use existign id)
    # -> actinia core returns resource-url, including resource_id  (and queue name)
    #   (queuename = xx_<resource_id>; if configured accordingly within actinia -> each job own queue)
    # via knative jobsink: start actinia worker (with queue name)
    # (https://knative.dev/docs/eventing/sinks/job-sink/#usage)
    # e.g. HTTP POST with queue name
    # kubectl run curl --image=curlimages/curl --rm=true --restart=Never -ti -- -X POST -v \
    #    -H "content-type: application/json"  \
    #    -H "ce-specversion: 1.0" \
    #    -H "ce-source: my/curl/command" \
    #    -H "ce-type: my.demo.event" \
    #    -H "ce-id: 123" \
    #    -d '{"details":"queuename"}' \
    #    http://job-sink.knative-eventing.svc.cluster.local/default/job-sink-logger
    return "<queue_name>_<resource_id>"  # queue name and resource id


def send_binary_cloud_event(event, actinia_job, url):
    """Return posted binary event with actinia_job."""
    attributes = {
        "specversion": event["specversion"],
        "source": "/actinia-cloudevent-plugin",
        "type": "com.mundialis.actinia.process.started",
        "subject": event["subject"],
        "datacontenttype": "application/json",
    }
    data = {"actinia_job": actinia_job}

    event = CloudEvent(attributes, data)
    headers, body = to_binary(event)
    # send event
    requests.post(url, headers=headers, data=body)

    return event


def send_structured_cloud_event(event, actinia_job, url):
    """Return posted structured event with actinia_job."""
    attributes = {
        "specversion": event["specversion"],
        "source": "/actinia-cloudevent-plugin",
        "type": "com.mundialis.actinia.process.started",
        "subject": event["subject"],
        "datacontenttype": "application/json",
    }
    data = {"actinia_job": actinia_job}

    event = CloudEvent(attributes, data)
    headers, body = to_structured(event)
    # send event
    requests.post(url, headers=headers, data=body)

    return event
