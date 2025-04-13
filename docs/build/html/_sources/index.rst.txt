Contact Management REST API Documentation
===========================================

Welcome to the Contact Management API documentation. This API provides a complete solution for managing contacts with user authentication, email verification, and avatar management.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Core Features
---------------
* User authentication and authorization
* Contact management (CRUD operations)
* Birthday notifications
* Email verification
* Avatar management
* Rate limiting protection

API Endpoints
--------------

Authentication
~~~~~~~~~~~~~~~
.. automodule:: src.api.auth
   :members:
   :undoc-members:
   :show-inheritance:

Contacts
~~~~~~~~~~~~
.. automodule:: src.api.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Users
~~~~~~~~~
.. automodule:: src.api.users
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
~~~~~~~~~~~~
.. automodule:: src.api.utils
   :members:
   :undoc-members:
   :show-inheritance:

Data Models
-------------

Database Models
~~~~~~~~~~~~~~~~~
.. automodule:: src.database.models
   :members:
   :undoc-members:
   :show-inheritance:

Schema Models
~~~~~~~~~~~~~~~
.. automodule:: src.schemas
   :members:
   :undoc-members:
   :show-inheritance:

Services
-----------

Authentication Service
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: src.services.auth
   :members:
   :undoc-members:
   :show-inheritance:

Contact Service
~~~~~~~~~~~~~~~~~
.. automodule:: src.services.contacts
   :members:
   :undoc-members:
   :show-inheritance:

User Service
~~~~~~~~~~~~~~
.. automodule:: src.services.users
   :members:
   :undoc-members:
   :show-inheritance:

Data Access Layer
------------------

Database Configuration
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: src.database.db
   :members:
   :undoc-members:
   :show-inheritance:

Contact Repository
~~~~~~~~~~~~~~~~~~~
.. automodule:: src.repository.contacts
   :members:
   :undoc-members:
   :show-inheritance:

User Repository
~~~~~~~~~~~~~~~~
.. automodule:: src.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

Application Entry Point
------------------------
.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
--------------
.. automodule:: src.conf.config
   :members:
   :undoc-members:
   :show-inheritance:

Indices and Search
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
