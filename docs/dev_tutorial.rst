.. _dev_tutorial:

Spell Development Tutorial
##########################

.. note::
    A "Spell", in `The Wizard Of Troz <http://thetroz.com>`_ vernacular
    is a module that extends the core functionality of Troz.
    Other projects might call them plug-ins, extensions, or add-ons.

This guide will walk you through the process of creating your first spell.
In order to use a real life example, we will be re-creating the "Awesome" spell
that is already part of the standard Troz distribution.

Planning
========

For this spell we will be leveraging the `Internet Chuck Noris Database <http://icndb.com>`_
(because really, where else would you look for awesome but Chuck Noris?)

API Research
-------------

Looking at `<http://www.icndb.com/api/>`_ , we see that the API URL is
`<http://api.icndb.com/jokes/random>`_ and the following get
parameters are accepted (there are others but we'll only be
using the following two):

    * ``firstName``
    * ``lastName``

Now we can do a quick test run of the API:

.. code-block:: shell-session

   [user@host]$ curl "http://api.icndb.com/jokes/random"
   { "type": "success", "value": { "id": 326, "joke": "As an infant, Chuck Norris' parents gave him a toy hammer. He gave the world Stonehenge.", "categories": [] } }

As per the API, we can supply ``firstName`` and ``lastName`` to replace `Chuck Norris` with
a custom name

.. code-block:: shell-session

   [user@host]$ curl "http://api.icndb.com/jokes/random?firstName=Peter&lastName=Naudus"
   { "type": "success", "value": { "id": 476, "joke": "Peter Naudus doesn't need a debugger, he just stares down the bug until the code confesses.", "categories": ["nerdy"] } }

Accepted Queries
----------------

Next, after determining the web service requests that will need to be made,
we need to determine what query strings will trigger this spell.

    * `How awesome is Peter Naudus?`
    * `How awesome is The Batman?`

We can then use this to create the following regular expression:

.. code-block:: python

    "How awesome is ([^?]+)\?*"

Introduction to Spell Writing
=============================

Now that we have everything mapped out, we can begin coding. First we start with
a basic template. There are two things that every spell must comply with:

    #. Each spell must exist in its own module under ``spells``. This means that it must be in its own directory and be importable (have an ``__init__.py`` file among other things)
    #. Spells must inherit from ``lib.spell.BaseSpell``

Structure
---------

.. code-block:: python

    import lib.spell

    class Awesome(lib.spell.BaseSpell):
        """ docstring """
        weight = 100
        pattern = r"""
            How\s+
            awesome\s+
            is\s+
            ([^?]+)
            \?*
        """
        config = {}

        def incantation(self, query, config, state):
            return query, state

We'll go through each of these settings:

    * ``docstring``: This is a short description of what the spell does
    * ``weight``: If a query matches more than one spell, they are called in order of their weight. Our pattern will be fairly specific so we'll give a relatively large weight of ``100``.
    * ``pattern``: This string will be compiled into a regular expression and will be used to determine if a query matches or not. The regular expression is compiled with the ``VERBOSE`` flag which is why we needed to put in the ``\s+``'s (which makes our regular expression more robust anyways)
    * ``config``: This defines required configurations. We don't have any at the moment, so we'll leave this empty
    * ``incantation``: This is the function that is called when the spell is executed. We'll go over that next
        
Incantation
-----------

Now that we have the preliminary details out of the way we can get to work.

The incantation takes three arguments (not including `self`):

    * ``query``: If the spell's pattern has groups (which ours does), then ``query`` will be the first group found. If not, it will the user's query, verbatim
    * ``config``: The user's configuration deserialized into a dictionary
    * ``state``: An object containing the previously saved state or ``None`` if there was no previously saved state

Then, the incantation must return a tuple containing two items:

    * A string containing the spell's response or ``None`` if the spell was unsuccessful
    * The spell's state which will be persisted across sessions. This object must be serializable to JSON

Coding your First Spell
=======================

Now that we have the boilerplate code in place, we can create the incantation code:

.. code-block:: python
    
    import lib.spell

    class Awesome(lib.spell.BaseSpell):
        """ Ask to see just how awesome someone is """

        ...

        def incantation(self, query, config, state):

            # Take the query (for example "Peter Naudus") and split it
            # Into a first and last name
            first, _, last = query.strip().partition(' ')

            # Fetch a random joke from ICNDB, see below
            result = self.fetch(
                'http://api.icndb.com/jokes/random',
                get={
                    'firstName': first,
                    'lastName': last
                },
                format='json'
            )

            if result['type'] == 'success':
                # Success, return joke and state
                return result['value']['joke'], state
            else:
                # Return None to signify unsuccessful attempt
                return None, state

lib.spell.BaseSpell.fetch
-------------------------

The ``fetch`` function is the only new piece that we haven't gone over. This method takes
four arguments (but two are mutually exclusive):

    * ``url``: The base URL of the web service to query
    * ``get``: A dictionary that is used to build the query string. Cannot be used with ``post``.
    * ``post``: A dictionary that is used to build the post data. Cannot be used with ``get``.
    * ``format``: Instructs ``fetch`` on how to decode the response. Valid values are: ``json``, ``xml``, and ``raw``

Fire it up!
-----------

Finally we can test out our new spell

.. code-block:: shell-session

   [user@host]$ python troz.py "How awesome is The Batman?"
   That's not The Batman doing push-ups -- that's The Batman moving the Earth away from the path of a deadly asteroid.

Hurray it works!

Bonus: See it listed
--------------------

Now that we've created out spell, we can see that it has automatically be added to the list of available spells
and our docstring is used as the spell's description

.. code-block:: shell-session

   [user@host]$ python troz.py --spell-list
   The following spells are currently installed:
    * Awesome --  Ask to see just how awesome someone is 
    * DDG --  Queries DuckDuckGo 
    * OpenWeatherMap --  Gets the current weather conditions and forecast 

Introduction to Testing with Shaman
===================================

Now that we have the spell coded up, let's put together some regression tests. This will allow
us to quickly test any new changes and see if we've broken anything.

Enter the Shaman
----------------

Just as ``lib.spell.BaseSpell`` provides a framework to create spells, Troz
also has ``lib.test.Shaman`` which is a thin wrapper that sits on top of
``unittest2``.

Like with the spell, there are two things that every test must comply with:

    #. The test must exist in the same module as its corresponding spell
    #. Tests must inherit from ``lib.test.Shaman``

.. note:: Currently, Troz only supports one test class per spell
    (although one class can have many sub-tests)

Structure
---------

Just as with the spell, we'll start with a bare-bones class and then
go back and fill in the details

.. code-block:: python

    import lib.test

    class Awesome(lib.test.Shaman):

        def setUp(self):
            self.web.route( ... )                  #1

        def test_1(self):                          #2
            result = self.query( ... )             #3
            expected = ...
            self.assertLooksLike(result, expected) #4

We'll go through the main points of interest:

    #. ``self.web.route(...)``
        * ``lib.test.Shaman.web.route``, like it's sibling ``lib.spell.BaseSpell.fetch``, takes mostly the same arguments (``url``, ``get``, ``post``, and ``format``), with one additional one: ``file``.
        * The ``file`` argument must point to an existing file in the ``test_data``, under the spell's module directory
        * It intercepts requests made to the spell's ``fetch``, looking at the arguments being passed.
        * While intercepting, if it finds a route with the same arguments , it returns the contents of the file attached to the route. If no matching route is found, an error is raised
    #. ``test_1``. All test function names must be start with the ``test_`` prefix
    #. ``self.query(...)``. This executes the spell under test and returns the result
    #. ``self.assertLooksLike(...)``. This is very similar to unittest2's ``assertEqual``, except that it ignores differences in spacing and case

Capture The Magic
-----------------

Trying to test a spell like ``awesome`` raises a couple challenges:

    #. Since the response is random, it's difficult to predict what the spell will return
    #. An Internet connections is required (can't test it off-line)

In order to work around these limitations, troz has a ``--capture`` flag
which will print out calls to ``lib.spell.BaseSpell.fetch`` and then save
the output to a temporary file.

We'll run two different queries and capture the results:


.. code-block:: shell-session

    [user@host]$ python troz.py --capture "How awesome is Peter Naudus?"
    url: http://api.icndb.com/jokes/random get: {'firstName': 'Peter', 'lastName': 'Naudus'} Output saved to /tmp/tmpG1pKIW
    Peter Naudus invented black. In fact, he invented the entire spectrum of visible light. Except pink. Tom Cruise invented pink.

    [user@host]$ python troz.py --capture "How awesome is Chuck Norris?"
    url: http://api.icndb.com/jokes/random get: {'firstName': 'Chuck', 'lastName': 'Norris'} Output saved to /tmp/tmpImni3o
    The Manhattan Project was not intended to create nuclear weapons, it was meant to recreate the destructive power in a Chuck Norris Roundhouse Kick. They didn't even come close.


Coding up Your First Test
=========================

Now we're ready to code up our first test!

The first thing we'll do is copy over the saved capture files to the ``test_data`` directory so that we can load them
via the ``route`` helper. We'll name the files something meaningful and with a ``.dat`` extension.

.. code-block:: shell-session

    [user@host]$ mkdir spells/awesome/test_data
    [user@host]$ mv /tmp/tmpG1pKIW spells/awesome/test_data/peter_naudus.dat
    [user@host]$ mv /tmp/tmpImni3o spells/awesome/test_data/chuck_norris.dat

Now we'll use the information returned by the capture session to build our test:

.. code-block:: python

    import lib.test

    class Awesome(lib.test.Shaman):

        def setUp(self):
            # Register URL for "How awesome is Peter Naudus?" query
            self.web.route(
                url='http://api.icndb.com/jokes/random',
                get={
                    'firstName': 'Peter',
                    'lastName': 'Naudus'
                },
                format='json',
                file='peter_naudus.dat'
            )

            # Register URL for "How awesome is Chuck Norris?" query
            self.web.route(
                url='http://api.icndb.com/jokes/random',
                get={
                    'firstName': 'Chuck',
                    'lastName': 'Norris'
                },
                format='json',
                file='chuck_norris.dat'
            )

        def test_peter_naudus(self):
            result = self.query("How awesome is Peter Naudus?")
            expected = """
                Peter Naudus invented black. In fact, he invented
                the entire spectrum of visible light. Except pink.
                Tom Cruise invented pink.
            """
            self.assertLooksLike(result, expected)

        def test_chuck_norris(self):
            result = self.query("How awesome is Chuck Norris?")
            expected = """
                The Manhattan Project was not intended to create
                nuclear weapons, it was meant to recreate the
                destructive power in a Chuck Norris Roundhouse
                Kick. They didn't even come close.
            """
            self.assertLooksLike(result, expected)

Now we can kick off the test by calling ``troz.py`` with the ``--test`` flag.


.. code-block:: shell-session

    [user@host]$ python troz.py --test
    test_chuck_norris (test.Awesome) ... ok
    test_peter_naudus (test.Awesome) ... ok

Sweet!

Bonus x2: See the info
----------------------

After we coded up the spell we saw that the spell was automatically listed and the docstring used
as the description. Now that we have a test in place, we can view the details of this spell by
calling ``troz.py`` with the ``--spell-info`` flag.

.. code-block:: shell-session

    [user@host]$ python troz.py --spell-info awesome
      * Name: Awesome
      * Description: Ask to see just how awesome someone is
      * Required configs: None
      * Example usage:
          >>> How awesome is Peter Naudus?
          ... Peter Naudus invented black. In fact, he invented the entire
              spectrum of visible light. Except pink. Tom Cruise invented
              pink.
          >>> How awesome is Chuck Norris?
          ... The Manhattan Project was not intended to create nuclear
              weapons, it was meant to recreate the destructive power in a
              Chuck Norris Roundhouse Kick. They didn't even come close.

Not only has the description been loaded from the spell, but the tests are automatically
extracted and used as documentation.

Using Configurations
====================

Now that we have a (literally) awesome spell coded up and tested, let's add an enhancement.
Instead of asking "How awesome is Peter Naudus?", I'd like to ask, "How awesome am I?". Then
the spell could load up my name from the configuration file. This is a simple change but
we'll walk through each step for clarity's sake.

Step 1: Change the regular expression
-------------------------------------

.. code-block:: python

        # Old pattern
        pattern = r"""
            How\s+
            awesome\s+
            (?:is|am)\s+
            ([^?]+)
            \?*
        """

        # New pattern
        pattern = r"""
            How\s+
            awesome\s+
            (?:is|am)\s+
            ([^?]+)
            \?*
        """

Step 2: Define the required configurations 
------------------------------------------

We'll store the first name in the config as ``personal.firstName`` and the
last name as ``personal.lastName``. Since both of these values will be strings
we'll define the config like this:

.. code-block:: python

    class Awesome(lib.spell.BaseSpell):
        ...
        config = {
            'Personal.FirstName': str,
            'Personal.LastName': str
        }

Now if view the spell's info again, we'll see the required configs listed

.. code-block:: shell-session

    [user@host]$ python troz.py --spell-info awesome
      * Name: Awesome
      * Description: Ask to see just how awesome someone is
      * Required configs:
          - Personal.FirstName
          - Personal.LastName
      ...

Step 3: Update the code
-----------------------

.. code-block:: python

    def incantation(self, query, config, state):
        first, _, last = query.strip().partition(' ')

        if first.upper() == 'I' and not last:
            first = config['Personal.FirstName']
            last = config['Personal.LastName']

        result = self.fetch(
            'http://api.icndb.com/jokes/random',
            get={
                'firstName': first,
                'lastName': last
            },
            format='json'
        )

        if result['type'] == 'success':
            return result['value']['joke'], state
        else:
            return None, state

Step 4: Update the test
-----------------------

When running the test, we don't know for sure what the user will have in their
configuration file, so during the ``setUp``, we'll provide our own config values:

.. code-block:: python

   ...

   def setUp(self):
        ...
        self.config['Personal.FirstName'] = 'Peter'
        self.config['Personal.LastName'] = 'Naudus'
    ...


To add the extra test, we could simply duplicate the ``test_peter_naudus`` function
and rename it as ``test_me`` and change the input. 

.. code-block:: python

   ...

    def test_me(self):
        result = self.query("How awesome am I?")
        expected = """
            Peter Naudus invented black. In fact, he invented
            the entire spectrum of visible light. Except pink.
            Tom Cruise invented pink.
        """

    def test_peter_naudus(self):
        result = self.query("How awesome is Peter Naudus?")
        expected = """
            Peter Naudus invented black. In fact, he invented
            the entire spectrum of visible light. Except pink.
            Tom Cruise invented pink.
        """
   ...

However, then we're just duplicating code. ``lib.test.Shaman`` provides a generate
decorator which allows us to group these two test functions together. It will generate
two new test cases one for each of the inputs, passing the input as the function's
``question`` argument.

.. code-block:: python

   ...

    lib.test.Shaman.generate("How awesome am I?", "How awesome is Peter Naudus?")
    def test_peter_naudus(self, question):
        result = self.query(question)
        expected = """
            Peter Naudus invented black. In fact, he invented
            the entire spectrum of visible light. Except pink.
            Tom Cruise invented pink.
        """
   ...

That's all folks!

Now go forth and build your own spells!
