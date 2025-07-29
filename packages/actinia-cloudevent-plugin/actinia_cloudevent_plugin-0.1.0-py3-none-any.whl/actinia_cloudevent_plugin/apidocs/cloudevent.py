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


from actinia_cloudevent_plugin.model.response_models import (
    SimpleStatusCodeResponseModel,
)

describe_cloudevent_post_docs = {
    # "summary" is taken from the description of the get method
    "tags": ["cloudevent"],
    "description": (
        "Receives cloudevent, transforms and starts pc and returns cloudevent."
    ),
    "responses": {
        "200": {
            "description": (
                "This response returns received, and returned events, "
                "generated queue name and the status"
            ),
            "schema": SimpleStatusCodeResponseModel,
        },
        "400": {
            "description": "This response returns an error message",
            "schema": SimpleStatusCodeResponseModel,
        },
    },
}
