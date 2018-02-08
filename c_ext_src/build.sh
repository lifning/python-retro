#!/bin/bash
gcc $(python3.6-config --cflags) -shared -fPIC -o log_wrapper.so log_wrapper.c
