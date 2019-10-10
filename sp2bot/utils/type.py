#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Convert string to int
def try_to_int(s):
    try:
        return int(s)
    except ValueError:
        return None
