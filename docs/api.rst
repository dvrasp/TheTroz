.. _api:

API
###

.. module:: lib.spell

.. note::
    A "Spell", in `The Wizard Of Troz <http://thetroz.com>`_ vernacular
    is a module that extends the core functionality of Troz.
    Other projects might call them plug-ins, extensions, or add-ons.

Base Class for Spells
=====================

.. autoclass:: BaseSpell(self)
   :members:
   :show-inheritance:

Shaman Test Helper
==================

.. module:: lib.test

.. autoclass:: Shaman(self)
   :members:
   :show-inheritance:

.. autoclass:: WebMock(self, root)
   :members:

For Core Developers
===================

.. tip::
    Unless you're making core changes, you don't need to know about these

Registry
--------

.. automodule:: lib.registry
    :members:

Config
------

.. automodule:: lib.config
    :members:

Testing Helpers
---------------

.. module:: lib.test

.. autoclass:: WebCapture
    :members:
