Installation
=============

Installing python-joern
------------------------

python-joern can be installed using pip::

	sudo pip2 install git+git://github.com/fabsx00/python-joern.git

This will (hopefully) automatically take care of installing
dependencies. If dependencies are not installed correctly, you can try
to manually install them as discussed in the following section.


Manually Installing Dependencies
-------------------------------------------

The following steps are only required if for some reason, installation
of python-joern fails due to unresolved dependencies.

Install *py2neo 1.6.1* from

https://pypi.python.org/packages/source/p/py2neo/py2neo-1.6.1.tar.gz

On Linux and BSD systems, executing the following commands will
typically suffice::

	wget https://pypi.python.org/packages/source/p/py2neo/py2neo-1.6.1.tar.gz;
	tar xfz py2neo-1.6.1.tar.gz;
	cd py2neo-1.6.1;
	sudo python2 setup.py install;

Install the gremlin-plugin for neo4j from
https://github.com/fabsx00/py2neo-gremlin/releases/tag/0.1::

	wget https://github.com/fabsx00/py2neo-gremlin/archive/0.1.tar.gz
	tar xfz 0.1.tar.gz
	cd py2neo-gremlin-0.1
	sudo python2 setup.py install
