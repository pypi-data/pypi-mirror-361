Getting started
===============

This section will give you basic information how to use the **CoolString** class.

=======================
Installation and Import
=======================

Installing the module is done using pip:

.. code-block:: bash

   pip install -U coolstring

or, to install for a specific python interpreter, for example python3.11, do:

.. code-block:: bash

   python3.11 -m pip install -U coolstring


Now, let's import the module in python and create a CoolString object from a string:

.. code-block:: python

   >>> from coolstring import CoolString
   
   >>> foo = CoolString("Hello world!")

Great! Now we have a CoolString!

===========
Basic Usage
===========

The aim of CoolString is to add compatibility with as many operators as possible.
Of course, CoolString can still do basic things like addition or multiplication:

.. code-block:: python
   
   >>> from coolstring import CoolString
   >>> foo = CoolString("Hello world!")
   >>> print(foo + 3)
   'Hello world!3'
   >>> print(foo + "bar")
   'Hello world!bar'
   >>> print(foo * 3)
   'Hello world!Hello world!Hello world!'

But it also includes subtraction and division:

.. code-block:: python
   
   >>> from coolstring import CoolString
   >>> foo = CoolString("Hello world!")
   >>> print(foo - " world")
   'Hello!'
   >>> foo//3
   [CoolString('Hell'), CoolString('o wo'), CoolString('rld!')]
   >>> foo/3
   [CoolString('Hell'), CoolString('o wo'), CoolString('rld!'), CoolString('')]
   >>> foo%3
   CoolString('')

There are many more, check the :doc:`reference` for more details.

===========
Configuring
===========

For some operations, it is possible to set a mode in which they operate.
This applies to the compare operators as well as the shifting operators.

Configuring a CoolString is done with the **configure**-method:

.. code-block:: python
   
   >>> from coolstring import CoolString
   >>> foo = CoolString("Hello World!")
   >>> foo.configure(shiftmode=bitshift,compmode=length) #...

When a new CoolString object is created from this CoolString object, the configuration is copied to the new CoolString.

See the :doc:`reference` for the specific configuration values.

Additionally, you can configure the key "verbose" with a boolean.
If enabled, some operations will print information about what they do in operation.

Default modes are shiftmode="stringshift", compmode="content" and verbose=False.

===========
Information
===========

Because this is still in early stage, I cannot ensure that there are no bugs.
