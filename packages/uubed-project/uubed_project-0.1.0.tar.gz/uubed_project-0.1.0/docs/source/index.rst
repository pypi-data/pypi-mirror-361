.. uubed documentation master file

Welcome to uubed's documentation!
==================================

**uubed** is a high-performance library for encoding embedding vectors into position-safe strings that solve the "substring pollution" problem in search systems.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   quickstart
   api-reference
   troubleshooting
   contributing

Key Features
------------

* **Position-Safe Encoding**: QuadB64 family prevents false substring matches
* **Blazing Fast**: 40-105x faster than pure Python with Rust acceleration
* **Multiple Encoding Methods**: Full precision, SimHash, Top-k, Z-order
* **Search Engine Friendly**: No more substring pollution in Elasticsearch/Solr
* **Easy Integration**: Simple API, works with any vector database

Quick Example
-------------

.. code-block:: python

   import numpy as np
   from uubed import encode

   # Create a sample embedding
   embedding = np.random.rand(384).astype(np.float32)
   
   # Encode to position-safe string
   encoded = encode(embedding, method="auto")
   print(f"Encoded: {encoded[:50]}...")

Project Structure
-----------------

The uubed project is organized across multiple repositories:

* `uubed <https://github.com/twardoch/uubed>`_ - Main project hub (this repository)
* `uubed-rs <https://github.com/twardoch/uubed-rs>`_ - High-performance Rust implementation
* `uubed-py <https://github.com/twardoch/uubed-py>`_ - Python bindings and API
* `uubed-docs <https://github.com/twardoch/uubed-docs>`_ - Comprehensive documentation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`