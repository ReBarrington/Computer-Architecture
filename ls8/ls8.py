#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

fileName = sys.argv[1]
cpu = CPU()

cpu.load(fileName)
cpu.trace()
cpu.run()