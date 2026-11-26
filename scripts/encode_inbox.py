#!/usr/bin/env python3
"""Encode a form inbox for assets/js/config.js so the address never appears in any page.

Usage: python scripts/encode_inbox.py "name@example.com"  -> paste _k and _v into config.js
"""
import random
import sys

addr = sys.argv[1]
k = [random.randint(33, 250) for _ in range(9)]
v = [(ord(c) ^ k[i % len(k)]) + (i % 7) for i, c in enumerate(addr)]
print("_k:", k, ",")
print("_v:", v, ",")
