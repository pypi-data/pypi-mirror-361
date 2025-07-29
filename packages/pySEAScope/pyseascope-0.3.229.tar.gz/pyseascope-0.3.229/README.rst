Overview
--------

This project aims to provide Python bindings to interact with the `SEAScope`_
application developed by `OceanDataLab`_.

These bindings allow users to control the application remotely and to transfer
data between Python and SEAScope. These features can be used to create scripted
animations (e.g. to illustrate a study during a conference) or to analyse and
visualise data interactively.

.. _SEAScope: https://seascope.oceandatalab.com
.. _OceanDataLab: https://www.oceandatalab.com

Installation
------------

You have two options to install the package, you can either:

 * use the default options, in which case pip will only install the
   dependencies required to translate data between Python and SEAScope:

   .. code:: bash

     pip install pySEAScope


   This can be useful on systems where installing the packages required by the
   extended capabilities (data extraction, plotting) might prove difficult to
   install (matplotlib on Windows for example)

 * install the dependencies required to enable all the capabilities of the
   package:

   .. code:: bash

     pip install "pySEAScope[processor]"


Quickstart
----------

In order to use the Python bindings for SEAScope you first have to establish a
connection between SEAScope and Python, then you can use it to transfer data
and issue commands.

Establishing a connection
^^^^^^^^^^^^^^^^^^^^^^^^^

 1. Start the SEAScope application

 2. Open a Python console or a Jupyter notebook

 3. First you need to create a connection between Python and SEAScope. You
    should use a context (using the `with` keyword) so that Python closes the
    connection automatically:

    .. code:: python

      import SEAScope.upload

      # Connection settings
      host = '127.0.0.1'
      port = 11155

      with SEAScope.upload.connect(host, port) as link:
          # code that uses the connection will go there
          # ...

 4. You can now interact with SEAScope from you Python console / Jupyter
    notebook.


Example 1: manipulating rendering settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 1. Select a variable to display in SEAScope catalogue menu

 2. Note the names of both the selected collection and variable

 3. In your Python console / Jupyter notebook

    .. code:: python

      import SEAScope.upload

      # Connection settings
      host = '127.0.0.1'
      port = 11155

      collection_name = 'The collection you selected'
      variable_name = 'The variable you selected'

      with SEAScope.upload.connect(host, port) as link:
          # Get the identifier that SEAScope uses for the selected variable
          variable_id = SEAScope.upload.get_id_for(link, collection_name,
                                                   variable_name)

          # Fetch the current rendering settings for this variable
          rendering_config = SEAScope.upload.rendering_config_for(link,
                                                                  variable_id)

          # Modify rendering configuration, add some transparency for example
          rendering_config['opacity'] = 0.3

          # Apply modifications by sending the configuration back to SEAScope
          SEAScope.upload.rendering_cfg(link, rendering_config)


.. warning::

    Many Python bindings require numerical identifiers: do not create them by
    hand, always use the :func:`SEAScope.upload.get_id_for` to obtain the
    actual identifiers from the application.


Example 2: Extracting data from SEAScope
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 1. Select a variable to display in SEAScope catalogue menu

 2. Create new vertices using either the middle click or Ctrl + right click

 3. Complete the extraction shape by pressing Enter for a polyline or Shift +
    Enter for a polygon

 4. A contextual menu will appear, click on the extraction button |extraction|

 5. In your Python console / Jupyter notebook

    .. code:: python

      import SEAScope.upload
      import SEAScope.lib
      import json

      # Connection settings
      host = '127.0.0.1'
      port = 11155

      with SEAScope.upload.connect(host, port) as link:
          extraction = SEAScope.lib.get_extracted_data()

      for granule_path, granule_info in extraction.items():
          print('=> Granule path: {}'.format(granule_path))
          print('\tMetadata: {}'.format(granule_info['meta']))
          print('\tData: {}'.format(granule_info['data']))

.. |extraction| image:: /_static/extraction_button.png

Design choices
--------------
The SEAScope application can be configured to communicate with external
applications in order to extend its capabilities and let users manipulate data
with their preferred tools.

The communication pipeline between SEAScope and these applications has been
designed to be as simple and as portable as possible while maintaining good
performance.

Data must be serialized before they can be exchanged between SEAScope and the
external applications, i.e. they must be translated into a format that the
operating system can store on disk or send through the network. Several
serialization formats exist, we chose `FlatBuffers`_ because it is performant,
has support for many programming languages and has no dependencies.

In order to achieve the portability goal, we decided to have SEAScope listen to
a `stream socket`_, a low-level network endpoint abstraction that is
implemented by all major operating systems. This choice has a very useful
side-effect: it allows external applications to communicate with SEAScope over
the network, which paves the way for new methods to use SEAScope (remote
control, shared SEAScope instance, etc...).

.. image:: /_static/design.png

.. _stream socket: https://en.wikipedia.org/wiki/Network_socket#Stream_socket
.. _flatbuffers: https://google.github.io/flatbuffers/


Controlling SEAScope remotely
-----------------------------
By default SEAScope only listens to connections from the local computer
(IP address 127.0.0.1). In order for SEAScope to communicate with other
applications over the network, you must provide the `-l` option with the IP
address and port that SEAScope will listen to.

.. note::
  You have to start SEAScope from the command line to do this, or create a
  launcher/shortcut depending on you operating system.

For example, if your IP address on the local network is 192.168.1.5/24 and if
port 5000 is not used by another application, you can start SEAScope (on Linux)
with:

.. code:: bash

  ./seascope -l 192.168.1.5:5000

You should then be able to reach SEAScope from another computer on the same
local network (with IP address 192.168.1.28/24 for example) with the following
Python code:

.. code:: python

  import SEAScope.upload

  # Connection settings
  host = '192.168.1.5'
  port = 5000

  with SEAScope.upload.connect(host, port) as link:
      # code that uses the connection will go there
      # ...
  

Licence
-------

The licence that applies to this project is the GNU Lesser General Public
License v3.0. Please look at the
:download:`licence file </_static/licence.txt>` for more information.

The content of the SEAScope/API directory has been generated by a third-party
software (flatc) and is therefore subject to the licenses that apply for the
FlatBuffers project (Apache 2.0).


Development
-----------

Dev environment:

.. code:: bash

    pip install -r dev_requirements.txt

Linting:

.. code:: bash

    flake8 --exclude=.tox,.eggs,env,SEAScope/API

Documentation:

.. code:: bash

    cd docs
    make apiref
    make html
    ${BROWSER} build/html/index.html

