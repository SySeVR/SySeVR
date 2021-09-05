Contributing to Py2neo
======================

Third party contributions are always welcome. Please make sure you look through the details below
before submitting a pull request.


Cloning the Repository
----------------------

To get a copy of the py2neo repository, first create a fork within your own GitHub account and then
run the git clone command:

```bash
$ git clone git@github.com:«account»/py2neo.git
```


Dependencies
------------

Py2neo has no third party dependencies (except for testing). This policy helps to keep the code
portable and self-contained. If you feel that a third-party library is required for an extension
you are building then get in touch.


Support
-------

Any code written must work with Python 2.7, 3.3 and 3.4. Neo4j versions 1.8, 1.9, 2.0 and 2.1 must
also either be supported or must fail gracefully if a required feature is not available in that
version. The **Graph** class provides a number of **supports_** methods that may be useful for this
purpose.


Directory Structure
-------------------

Within the py2neo directory are the following files and directories:

- **art/** - artwork
- **bau** - build script
- **book/** - documentation (Sphinx)
- **.coveragerc** - coverage configuration for unit tests
- **py2neo/** - source code
- **setup.py** - package setup script
- **test/** - tests
- **.travis.yml** - configuration for Travis CI


Package Structure
-----------------

The py2neo package structure is as follows:

- **py2neo** - core functionality
  - **py2neo.batch** - batch support
  - **py2neo.cypher** - Cypher language support
  - **py2neo.ext** - non-core extensions
  - **py2neo.legacy** - legacy functionality
  - **py2neo.packages** - bundled dependencies
    - **py2neo.httpstream** - HTTP client for RESTful web services (use this for any HTTP work)

If you are in doubt as to where to add something, just ask.


Extensions
----------

If you are building a non-core extension for py2neo, this should live within a **py2neo.ext**
sub-package and may make use of the following classes:

- **Resource** - represents a remote REST resource
- **ResourceTemplate** - maintains a URI template for remote REST resources
- **ServerPlugin** - base class for Neo4j [server plugins](http://neo4j.com/docs/stable/server-plugins.html)
- **Service** - a wrapper object that may be bound to a remote resource
- **ServiceRoot** - the root service for a Neo4j server
- **UnmanagedExtension** - base class for Neo4j [unmanaged extensions](http://neo4j.com/docs/stable/server-unmanaged-extensions.html)


Naming
------

Be careful over naming. This is one of the hardest things to get right but one of the most
important.


Coding Style
------------

- Code should generally adhere to [PEP-8](http://legacy.python.org/dev/peps/pep-0008/) and can use
a maximum line length of 100 characters
- All public methods should have a docstring


Testing
-------

To run the test suite, issue the following command:

```bash
$ ONLINE=1 ./bau test
```

This will download and install all required versions of Neo4j and will run the tests against each
in turn. Ensure you are not already running a server on port 7474 before doing this.

If the test script has already been run at least once in online mode, it should be possible to run
it in offline mode:

```bash
$ ./bau test
```

This is useful if working somewhere without an Internet connection, such as when commuting on a
[Southeastern](http://www.southeasternrailway.co.uk/) train :-(

Instead of running against every supported Neo4j version, you can also choose to run against the
latest version only:

```bash
$ ./bau test-latest
```


Building the Docs
-----------------

The documentation can also be built with the ``bau`` script:

```bash
$ ./bau book
```
