Polarion client
===============

The polarion connects to the WSDL services of the Polarion service. These are listed at <polarion_url>/ws/services.
It is important that the url it the url where you normally login. So it should include /polarion in most cases.

Initialization
--------------
The class can be instantiated like this:

.. code:: python

    pol = polarion.Polarion('http://example.com/polarion', 'user', 'password')
    print(pol) # Polarion client for http://example.com/polarion/ws/services with user <user>


Services
--------
Typically you would not use any service directly, but it is an option. Using it this way would ensure the session is still valid. 

.. warning::
    The refreshing of the session is still an open issue and not yet implemented. Using this module for prolonged time will likely lead to an ended session.

.. code:: python

    pol = polarion.Polarion('http://example.com/polarion', 'user', 'password')
    s = pol.getService('Tracker')
    print(s) # <zeep.proxy.ServiceProxy object at 0x0000025C01BF3A48>


Polarion class
--------------

.. autoclass:: polarion.polarion.Polarion
    :members: