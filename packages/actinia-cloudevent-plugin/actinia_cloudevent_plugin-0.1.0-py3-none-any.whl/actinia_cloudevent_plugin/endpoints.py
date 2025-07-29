#!/usr/bin/env python
"""Copyright (c) 2018-2025 mundialis GmbH & Co. KG.

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

Add endpoints to flask app with endpoint definitions and routes
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann, Lina Krisztian"
__copyright__ = "Copyright 2022-2024 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


import sys

import werkzeug
from flask import current_app, send_from_directory
from flask_restful_swagger_2 import Api

from actinia_cloudevent_plugin.api.cloudevent import Cloudevent
from actinia_cloudevent_plugin.resources.logging import log


# endpoints loaded if run as actinia-core plugin as well as standalone app
def create_endpoints(flask_api: Api) -> None:
    """Create plugin endpoints."""
    app = flask_api.app
    apidoc = flask_api

    package = sys._getframe().f_back.f_globals["__package__"]  # noqa: SLF001
    if package != "actinia_core":

        @app.route("/")
        def index():
            try:
                return current_app.send_static_file("index.html")
            except werkzeug.exceptions.NotFound:
                log.debug("No index.html found. Serving backup.")
                # when actinia-cloudevent-plugin is installed in single mode,
                # the swagger endpoint would be "latest/api/swagger.json".
                # As api docs exist in single mode,
                # use this fallback for plugin mode.
                return """<h1 style='color:red'>actinia-metadata-plugin</h1>
                    <a href="api/v1/swagger.json">API docs</a>"""

        @app.route("/<path:filename>")
        def static_content(filename):
            # WARNING: all content from folder "static" will be accessible!
            return send_from_directory(app.static_folder, filename)

    apidoc.add_resource(Cloudevent, "/")
