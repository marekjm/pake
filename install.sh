#!/usr/bin/bash

   
if [ ${EUID} == 0 ]; then
    echo "Installing pake"
else
    echo "fail: you must be root to do this!"
    exit 1
fi


if [ $1 == '']; then
    echo "fail: you have to give Python version (eg. 3.3 for python 3.3) as an argument."
else
    make clean
    cp -Rv ./pake/ /usr/lib/python$1/site-packages/
fi
