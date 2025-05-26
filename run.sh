#!/usr/bin/env bash

./py313stable/bin/python controller.py \
  --server-type threaded multiprocess \
  --server-threads 1 2 3 4 \
  --max-client-threads 4 \
  --benchmark-duration 15 \
  --mode compute
