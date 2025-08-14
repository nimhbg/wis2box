.. _public-services-setup:

Public services setup
=====================

Before you can proceed to register your WIS2 Node to share your data with the WIS2 network, you need to ensure that certain services are available to the public Internet:

* The Global Broker needs to be able to subscribe to your MQTT endpoint to receive and republish WIS2 notifications published by the MQTT broker running in your wis2box instance
* The Global Cache needs to be able to access your HTTP endpoint to download data published by the wis2box instance (to access **core** data (per the WMO Unified Data Policy) and metadata records).

Security considerations
-----------------------

When exposing your services to the public Internet, it is important to consider the security implications of doing so.

Please ensure that you follow these best practices to ensure your wis2box-instance is secure:

* Ensure that your wis2box instance runs behind a firewall and only exposes the necessary ports to the public internet (e.g. 80 or 443 for HTTP, 1883 or 8883 for MQTT)
* MQTT subscribers should use ``everyone/everyone`` as the username/password to subscribe to the WIS2 notifications published by your wis2box instance
* Never share the values of ``WIS2BOX_BROKER_PASSWORD`` and ``WIS2BOX_STORAGE_PASSWORD`` as they are only for internal use
* Store the authentication tokens used in the wis2box-webapp securely and do not share them with unauthorized users
* Use SSL/TLS encryption to secure your services
* Consider customizing the default web configuration defined in ``nginx/nginx.conf`` to expose only the services to be shared with the public

The wis2box development team is not responsible for the security of your wis2box-instance and it is your responsibility to ensure that your wis2box instance is secure.

GitHub issues and discussions provide a resource and forum to discuss general wis2box features, bugs and updates.  For specific security related questions, please write to ``wis2-support at wmo.int``.

Connecting your instance to the WIS2 network
--------------------------------------------

Once the wis2box instance is available to the public Internet, you can proceed to request this instance to be registered as a WIS2 Node, see :ref:`wis2node-operations`.


Public services in wis2box
---------------------------

The next sections describe the public services available in wis2box and how to configure them.

web-proxy (nginx)
^^^^^^^^^^^^^^^^^

wis2box runs a local nginx container allowing access to the following HTTP based services:

.. csv-table::
   :header: Function, URL
   :align: left

   API (wis2box-api),`WIS2BOX_URL/oapi`
   UI (wis2box-ui),`WIS2BOX_URL/`
   wis2box-webapp,`WIS2BOX_URL/wis2box-webapp`
   Storage (incoming data) (minio:wis2box-incoming),`WIS2BOX_URL/wis2box-incoming`
   Storage (public data) (minio:wis2box-public),`WIS2BOX_URL/data`
   Websockets (WIS2 notifications),`WIS2BOX_URL/mqtt`

You can edit ``nginx/nginx.conf`` to control which services are exposed through the nginx-container include in your stack.

By default the web-proxy service is exposed on port 80 on the host running wis2box.

SSL can be enabled by setting the ``WIS2BOX_SSL_CERT`` and ``WIS2BOX_SSL_KEY`` environment variables to the location of your SSL certificate and private key respectively.

When SSL is enabled, the web-proxy service is exposed on port 443 on the host running wis2box and uses the configuration defined in ``nginx/nginx-ssl.conf``.

.. note::
    The canonical link referenced in WIS2 notification messages by your wis2box will use the basepath ``WIS2BOX_URL/data``.
    This path has to be publicly accessible by the client receiving the WIS2 notifications, or the data referenced cannot be downloaded

To share your data with the WIS2 network, ensure that ``WIS2BOX_URL`` as defined in ``wis2box.env`` points to the externally accessible URL for your HTTP services. 

After updating ``WIS2BOX_URL``, please stop and start wis2box using ``wis2box-ctl.py`` and republish your data using the command ``wis2box metadata discovery republish``:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start
  python3 wis2box-ctl.py login
  wis2box metadata discovery republish

API (wis2box-api)
-----------------

The wis2box API uses `pygeoapi`_,  which implements the `OGC API`_ suite of standards, to provide programmatic access to the data collections hosted in wis2box.

.. image:: ../_static/wis2box-api.png
  :width: 800
  :alt: wis2box API-api

.. note::
  
  Currently, the default API backend in wis2box uses `Elasticsearch`_.
  A dedicated Docker volume ``es-data`` is created on your host when you start wis2box. 
  As long as this volume is not deleted you can remove/update the containers in wis2box without losing data.

User Interface (wis2box-ui)
---------------------------

The wis2box user interface uses the wis2box API to visualize the data configured and shared through wis2box.

On the homepage you can see the datasets configured in your wis2box instance. For each dataset you can view the metadata and the messages published for that dataset:

.. image:: ../_static/wis2box-ui-datasets.png
  :width: 800
  :alt: wis2box UI homepage

Datasets that have a plugin configured to convert data to GeoJSON will also have the 'OBSERVATIONS' option that provides a link to the wis2box API to access the data in GeoJSON format.

For data published under the 'weather/surface-based-observations/synop' topic, the user interface provides the 'EXPLORE' option to visualize the data on a map and the 'MAP' to visualize Weather Observations per station, which requires the 'bufr2geojson' plugin to be configured for your dataset.

.. image:: ../_static/wis2box-map-view.png
  :width: 800
  :alt: wis2box UI map visualization

From the 'MAP' view, you can click on a station to view the data for that station in a graph:

.. image:: ../_static/wis2box-data-view.png
  :width: 800
  :alt: wis2box UI data graph visualization

You can set a custom logo and background color for the UI by setting the following environment variables in the ``wis2box.env`` file:

.. code-block:: bash

  WIS2BOX_UI_LOGO=http://example.com/logo.png
  WIS2BOX_UI_BANNER_COLOR="#014e9e"

wis2box-webapp
--------------

The wis2box-webapp provides a web interface to help you configure wis2box and view WIS2 notifications published by your wis2box instance, along with the ability to interactively submit data using forms.

The webapp is accessible at `WIS2BOX_URL/wis2box-webapp` and uses basic authentication to control access to the web interface. 
The credentials are defined in the ``wis2box.env`` file by the following environment variables:

.. code-block:: bash

  WIS2BOX_WEBAPP_USERNAME=wis2box-admin
  WIS2BOX_WEBAPP_PASSWORD=<your-password>

The wis2box-webapp provides access to the following interfaces:

- **SYNOP Form**: to interactively submit FM-12 data using a form
- **Dataset editor**: to create/edit/delete datasets along with their metadata and data mappings configuration
- **Station editor**: to create/edit/delete stations and associate stations with topics
- **Monitoring**: to monitor the WIS2 notifications published by your wis2box instance

See the section :ref:`setup` for more information on how to use the webapp to setup your wis2box instance.

Mosquitto (MQTT)
^^^^^^^^^^^^^^^^

By default, wis2box uses its own internal `Mosquitto`_ container to publish WIS2 notifications. 

To allow the WIS2 Global Broker to subscribe to WIS2 notifications from wis2box you have 2 options:

    * enable access to internal broker running in the MQTT container on wis2box host
    * configure wis2box to use an external broker

Internal broker
---------------

The internal MQTT broker is accessible on the host ``mosquitto`` within the Docker network used by wis2box.

By default port 1883 of the mosquitto container is mapped to port 1883 of the host running wis2box. 

By exposing port 1883 on your host, the Global Broker will be able to subscribe directly to the internal MQTT broker on wis2box.

.. note::

   The ``everyone`` user is defined by default for public readonly access (``origin/#``) as per WIS2 Node requirements.

When you add SSL to your wis2box instance, the internal MQTT broker will be accessible on port 8883 on the host running wis2box using the MQTT over SSL protocol (MQTTS).

The mosquitto service within wis2box also has websockets enabled and is proxied on '/mqtt' by the nginx container. 

The broker address for the Global Broker to subscribe to WIS2 notifications using the mosquitto service within wis2box is as follows:

- `mqtt://everyone:everyone@WIS2BOX_HOST:1883` - for MQTT without SSL
- `mqtts://everyone:everyone@WIS2BOX_HOST:8883` - for MQTT with SSL
- `ws://everyone:everyone@WIS2BOX_HOST/mqtt:80` - for MQTT over websockets without SSL
- `wss://everyone:everyone@WIS2BOX_HOST/mqtt:443` - for MQTT over websockets with SSL

Where ``WIS2BOX_HOST`` is the hostname or IP address of the host running wis2box.

.. note::

   The Global Broker will use the ``everyone`` user to subscribe to the internal MQTT broker on wis2box.

If you want to create additional users for the internal MQTT broker, you can do so by logging into the mosquitto container and using the ``mosquitto_passwd`` command:

.. code-block:: bash

  docker exec -it mosquitto /bin/sh

Then, to add a new user, use the following command:

.. code-block:: bash

  mosquitto_passwd -b /mosquitto/config/password.txt <username> <password>

After adding a new user, you can edit the file ``/mosquitto/config/acl.conf`` to add or change access rights for mosquitto users. 

For example to allow a user to publish to the topic ``wis2box/cap/publication``, you would add the following line to the ``acl.conf`` file:

.. code-block:: bash

  user <username>
  topic readwrite wis2box/cap/publication

External broker
---------------

By default, wis2box uses its own internal MQTT broker to also function as a public broker to publish WIS2 notifications.

If you do not wish to expose the internal MQTT broker on wis2box, you can configure wis2box to publish WIS2 notifications to an external broker by setting the environment variable ``WIS2BOX_BROKER_PUBLIC``.

.. code-block:: bash

    # For example to use an external broker at host=example.org
    WIS2BOX_BROKER_PUBLIC=mqtts://username:password@example.org:8883  

.. note::

   The ``everyone`` user is defined by default for public readonly access (``origin/#``) as per WIS2 Node requirements.

SSL
^^^

In order to ensure the security of your data, it is recommended to enable SSL on your wis2box instance.

There are multiple ways to expose the wis2box services over SSL:

- using a reverse proxy (recommended)
- using the built-in SSL support in the ``wis2box-ctl.py`` script

The recommended way to expose the wis2box services over SSL is to use a reverse proxy such as `nginx`_ or `traefik`_. Discuss with your IT team to determine which reverse proxy is best suited for your environment.

Please remember to update the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` environment variable after enabling SSL, ensuring your URL starts with ``https://``.

Please note that after changing the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` environment variables, you will need to restart wis2box:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start

After restarting wis2box, repeat the commands for adding your dataset and publishing your metadata, to ensure that URLs are updated accordingly:

.. code-block:: bash

  python3 wis2box-ctl.py login
  wis2box dataset publish /data/wis2box/metadata/discovery/metadata-synop.yml

Built-in SSL support
--------------------

You can also enable HTTPS and MQTTS directly in the nginx and mosquitto containers running in wis2box.
In this case, the certificate and private key must be available on the host running wis2box

The location of your SSL certificate and private key are defined by the environment variables ``WIS2BOX_SSL_CERT`` and ``WIS2BOX_SSL_KEY`` respectively.

.. code-block:: bash

  WIS2BOX_SSL_CERT=/etc/letsencrypt/live/example.wis2box.io/fullchain.pem
  WIS2BOX_SSL_KEY=/etc/letsencrypt/live/example.wis2box.io/privkey.pem

Please remember to update the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` environment variable after enabling SSL, ensuring your URL starts with ``https://``.

You will need to restart your wis2box instance after enabling SSL:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start

Your wis2box instance will now apply TLS encryption to the HTTP and MQTT services, exposing them on HTTPS (port 443) and MQTTS (port 8883). 
When setting up the network routing of your wis2box instance, only ports 443 and 8883 need to be exposed to the public internet.

After restarting wis2box, repeat the commands for adding your dataset and publishing your metadata, to ensure that URLs are updated accordingly:

.. code-block:: bash

  python3 wis2box-ctl.py login
  wis2box data add-collection ${WIS2BOX_HOST_DATADIR}/surface-weather-observations.yml
  wis2box metadata discovery publish ${WIS2BOX_HOST_DATADIR}/surface-weather-observations.yml

.. _`Mosquitto`: https://mosquitto.org/
.. _`pygeoapi`: https://pygeoapi.io/
.. _`Elasticsearch`: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
.. _`OGC API`: https://ogcapi.ogc.org
.. _`nginx`: https://www.nginx.com/
.. _`traefik`: https://traefik.io/
