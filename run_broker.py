#!/usr/bin/env python

import argparse
import zmq_pubsub

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    zmq_pubsub.serve(args.quiet)
