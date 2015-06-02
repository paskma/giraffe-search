# Giraffe Search 

Quick and dirty filesystem indexer written in Python. GUI is provided by GTK. Running on Linux and Windows.

https://www.youtube.com/watch?v=FQxNsvBESgY


## Usage

Create index of interested locations.

``cd giraffe``
``python makeindex.py /data/mp3 /data/ebooks``

You can use simple command-line interface.

``python query.py alanis ironic``

And run GUI.

``python mainform.py``


## News
0.1.0

* Results with icons.
* Drag & Drop
* Multithreaded (responses even faster).

0.0.4

* Many small improvements and optimizations.
* Microsoft Windows support(!) (Requires Windows PyGTK port.)
