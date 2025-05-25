#!/usr/bin/env bash

./py313stable/bin/python controller.py \
  --server-type multiprocess \
  --server-threads 1 2 3 4 \
  --max-client-threads 8 \
  --benchmark-duration 15 \
  --mode compute
