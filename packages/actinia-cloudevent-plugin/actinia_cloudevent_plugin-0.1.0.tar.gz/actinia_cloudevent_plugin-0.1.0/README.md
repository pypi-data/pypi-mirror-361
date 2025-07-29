# actinia-cloudevent-plugin

This is a plugin for [actinia-core](https://github.com/mundialis/actinia_core) which adds cloudevent endpoints and runs as standalone app.

## Installation and Setup

Use docker-compose for installation:
```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm --service-ports --entrypoint sh actinia-cloudevent
# within docker
gunicorn -b 0.0.0.0:5000 -w 8 --access-logfile=- -k gthread actinia_cloudevent_plugin.main:flask_app
```

### DEV setup
```bash
# Uncomment the volume mount of the cloud-event-plugin within docker/docker-compose.yml,
# then:
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm --service-ports --entrypoint sh actinia-cloudevent
# within docker:
# install the plugin
pip3 install .
# start flask app with actinia-cloudevent-plugin
python3 -m actinia_cloudevent_plugin.main
```

### Installation hints
* If you get an error like: `ERROR: for docker_kvdb_1  Cannot start service valkey: network xxx not found` you can try the following:
```bash
docker compose -f docker/docker-compose-dev.yml down
# remove all custom networks not used by a container
docker network prune
docker compose -f docker/docker-compose-dev.yml up -d
```

## Configuration

- the URL of the cloudevent receiver is defined within [config/mount/sample.ini](config/mount/sample.ini): `[EVENTRECEIVER]` (Default value defined within [src/actinia_cloudevent_plugin/resources/config.py](src/actinia_cloudevent_plugin/resources/config.py))

## Requesting endpoint

**Note**: Assuming cloudevent-plugin is running as described in previous setup.

You can test the plugin and request the `/` endpoint, e.g. with:
```bash
# Start server for receiving of cloudevents (which are returned as response)
# NOTE: as defined within config/mount/sample.ini: [EVENTRECEIVER]
python3 tests/cloudevent_receiver_server.py

# In another terminal
JSON=tests/examples/cloudevent_example.json
curl -X POST -H 'Content-Type: application/json' --data @$JSON localhost:5000/api/v1/ | jq
```

Exemplary returned cloudevent: [tests/examples/cloudevent_example_return.json](tests/examples/cloudevent_example_return.json)

## Hints

* If you have no `.git` folder in the plugin folder, you need to set the
`SETUPTOOLS_SCM_PRETEND_VERSION` before installing the plugin:
    ```bash
    export SETUPTOOLS_SCM_PRETEND_VERSION=0.0
    ```
    Otherwise you will get an error like this `LookupError: setuptools-scm was unable to detect version for '/src/actinia-cloudevent-plugin'.`.

* If you make changes in code and nothing changes you can try to uninstall the plugin:
    ```bash
    pip3 uninstall actinia-cloudevent-plugin.wsgi -y
    rm -rf /usr/lib/python3.8/site-packages/actinia_cloudevent_plugin.wsgi-*.egg
    ```

## Running tests
You can run the tests in the actinia test docker:

```bash
# Uncomment the volume mount of the cloud-event-plugin within docker/docker-compose.yml,
# then:
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm --service-ports --entrypoint sh actinia-cloudevent

# run all tests
make test

# # run only unittests
# make unittest

# run only integrationtests
make integrationtest

# run only tests which are marked for development with the decorator '@pytest.mark.dev'
make devtest
```

## Hint for the development of actinia plugins

### skip permission check
The parameter [`skip_permission_check`](https://github.com/mundialis/actinia_core/blob/main/src/actinia_core/processing/actinia_processing/ephemeral_processing.py#L1420-L1422) (see [example in actinia-statistic plugin](https://github.com/mundialis/actinia_statistic_plugin/blob/master/src/actinia_statistic_plugin/vector_sampling.py#L207))
should only be set to `True` if you are sure that you really don't want to check the permissions.

The skip of the permission check leads to a skipping of:
* [the module check](https://github.com/mundialis/actinia_core/blob/main/src/actinia_core/processing/actinia_processing/ephemeral_processing.py#L579-L589)
* [the limit of the number of processes](https://github.com/mundialis/actinia_core/blob/main/src/actinia_core/processing/actinia_processing/ephemeral_processing.py#L566-L570)
* the limit of the processing time

Not skipped are:
* the limit of the cells
* the mapset/project limitations of the user
