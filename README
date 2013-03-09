Introduction
============

The Wizard of Troz aims to be an intelligent personal assistant that is both easily extendable and easy to use. Features that make it unique are:

    * **Open source**: All the source code is freely available and licensed under the permissive `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_.
    * **Easily Extendable**: The core functionality can easily be extended by addition additional plugins, called spells. See "dev tutorial" for a tutorial
    * **Natural Language**: Rather than requiring a rigid language syntax, a natural and flexible language is accepted

..    Accessible: Troz works over existing communication channels (call, text, email, IM, etc), never requiring an app to be installed.

Installation
============

.. warning::
   The project hasn't been submitted to PyPI, yet. Coming soon!

Installation is simple:

``easy_install troz`` or ``pip install troz``

Usage
=====

To use Troz, simply ask it a question:

.. code-block:: shell-session

   [user@host]$ python troz.py "What is Pinky and the Brain?"
   Pinky and the Brain is an American animated television series.

Listing and Inspecting Spells
-----------------------------

To list the installed spells, use the ``--spell-list`` flag

.. code-block:: shell-session

   [user@host]$ python troz.py --spell-list

   The following spells are currently installed:
        * Awesome --  Raves on how awesome something is 
        * DDG --  Queries DuckDuckGo 
        * [needs config] OpenWeatherMap --  Gets the current weather conditions and forecast 
        * WolframAlpha --  Queries WolframAlpha 

Spells that are marked with ``[needs config]`` are missing configuration values.

To get information on a specific spell, use the ``--spell-info`` flag

.. code-block:: shell-session

   [user@host]$ python troz.py --spell-info WolframAlpha

        * Name: WolframAlpha
        * Description:  Queries WolframAlpha
        * Required configs:
            - WolframAlpha.AppID
        * Example usage:
            >>> 15 USD in RMB
            ... yuan93.44  (Chinese yuan)
            >>> How many cups are in a gallon?
            ... 16 cups
            >>> Where was George Washington born?
            ... Westmoreland County, Virginia
            >>> When is Easter?
            ... Sunday, March 31, 2013
            >>> How much is 15 miles in feet?
            ... 79200 feet
            >>> What is the tallest building in the world?
            ... Burj Khalifa (2717 feet)

Getting Help
------------

    * **Documentation**:  http://thetroz.com/docs
    * **Development Mailing List**: troz-devs@lists.sourceforge.net
