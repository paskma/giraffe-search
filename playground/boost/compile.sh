#!/bin/sh

g++ hello_ext.cpp -I/usr/include/python2.5 -shared -o hello_ext.so -lboost_python
