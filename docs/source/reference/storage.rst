.. _storage:

Storage
=======

Overview
--------

The default wis2box storage capability is powered by `MinIO`_, which provides S3 compatible object storage.

The default wis2box MinIO administration user interface can be accessed locally at ``http://localhost:9001``.

The username/password for MinIO is configured through environment variables (see :ref:`configuration`). 

.. image:: ../_static/minio-login-screen.png
   :width: 600px
   :alt: MinIO login screen
   :align: center

Once logged in, buckets can be managed via the default "Buckets" menu item (click "Manage").  Click "Browse"
provides a browsing capability for a storage administrator.

.. image:: ../_static/minio-buckets.png
   :width: 800px
   :alt: MinIO default administration UI
   :align: center


Uploading data to MinIO
-----------------------

Files can uploaded to the MinIO bucket in a number of ways.  Any new file received on MinIO will trigger an MQTT notification
which is received by wis2box.

Below are basic examples on sending data to the MinIO ``wis2box-incoming`` bucket.  For more information and additional
examples, consult the `official MinIO documentation`_.


Using the boto3 Python Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the Python boto3 package via `pip`_:

.. code-block:: bash

    pip3 install boto3

The below example copies a local file (``myfile.csv``) to the ``wis2box-incoming`` bucket with topic ``foo.bar.baz``:

.. code-block:: python

    import boto3

    endpoint_url = 'http://localhost:9000'
    filename = 'myfile.csv'

    session = boto3.Session(
        aws_access_key_id='wis2box',
        aws_secret_access_key='XXXXX' # your wis2box storage password
    )

    s3client = session.client('s3', endpoint_url=endpoint_url)

    with open(filename, 'rb') as fh:
        s3client.upload_fileobj(fh, 'wis2box-incoming', f'foo/bar/baz/{filename}')

To allow uploading files into MinIO remotely, the ``wis2box-incoming`` bucket is proxied via Nginx. 

For example, to upload the local file (``WIGOS_0-454-2-AWSNAMITAMBO_2021-11-18T0955.csv with topic``) to the folder 
``mw-mw_met_centre-test/data/core/weather/surface-based-observations/synop``:

.. code-block:: python

    import boto3

    endpoint_url = '<your-wis2box-url>'
    filename = 'WIGOS_0-454-2-AWSNAMITAMBO_2021-11-18T0955.csv'

    session = boto3.Session(
        aws_access_key_id='wis2box',
        aws_secret_access_key='XXXXX' # your wis2box storage password
    )

    s3client = session.client('s3', endpoint_url=endpoint_url)

    folder = 'mw-mw_met_centre-test/data/core/weather/surface-based-observations/synop'
    with open(filename, 'rb') as fh:
        s3client.upload_fileobj(fh, 'wis2box-incoming', f'{folder}/{filename}')


Using the MinIO Python Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MinIO provides a Python client which can be used as follows:

Install the Python minio module via `pip`_:

.. code-block:: bash

    pip3 install minio

The below example copies a local file (``mydata.bin``) to the ``wis2box-incoming`` bucket to topic ``foo.bar.baz``:

.. code-block:: python

    from minio import Minio

    filepath = '/home/wis2box-user/local-data/mydata.bin'
    minio_path = '/it-meteoam/data/core/weather/surface-based-observations/synop/'

    endpoint = 'http://localhost:9000'
    WIS2BOX_STORAGE_USERNAME = 'wis2box'
    WIS2BOX_STORAGE_PASSWORD = 'XXXXX' # your wis2box storage password

    client = Minio(
        endpoint=endpoint,
        access_key=WIS2BOX_STORAGE_USERNAME,
        secret_key=WIS2BOX_STORAGE_PASSWORD,
        secure=is_secure=False)
    
    filename = filepath.split('/')[-1]
    client.fput_object('wis2box-incoming', minio_path+filename, filepath)


Using S3cmd
^^^^^^^^^^^

Given MinIO is S3 compatible, data can be uploaded using generic S3 tooling.  The below example uses `S3cmd`_ to upload
data to wis2box MinIO storage:

Edit the following fields in ``~/.s3cfg``:

.. code-block:: bash

    cat << EOF > ~/.s3cfg
    # Setup endpoint
    host_base = localhost:9000
    use_https = False

    # Setup access keys
    access_key = wis2box
    secret_key = XXXXX
    EOF


Below is a simple command line example to copy a local file called ``myfile.csv`` into the ``wis2box-incoming`` bucket,
to topic ``foo/bar/baz``:

.. code-block:: bash

    s3cmd myfile.csv s3://wis2box-incoming/foo/bar/baz

Using the MinIO UI
^^^^^^^^^^^^^^^^^^

Files can also be uploaded interactively via the MinIO adminstration interface.  The example below demonstrates this
capability when browsing the ``wis2box-incoming`` bucket:

.. image:: /_static/minio-upload-file.png
   :width: 800px
   :alt: Uploading files using the MinIO adminstration interface
   :align: center


.. _`MinIO`: https://min.io
.. _`official MinIO documentation`: https://docs.min.io
.. _`pip`: https://pip.pypa.io
.. _`S3cmd`: https://s3tools.org/s3cmd
