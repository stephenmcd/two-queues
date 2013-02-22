#!/usr/bin/env python

import argparse
import multiprocessing
import random
import time

import redis

import buffered_redis
import zmq_pubsub


def new_client():
    """
    Returns a new pubsub client instance - either the Redis or ZeroMQ
    client, based on command-line arg.
    """
    if args.redis:
        if args.unbuffered:
            Client = redis.Redis
        else:
            Client = buffered_redis.BufferedRedis
    else:
        Client = zmq_pubsub.ZMQPubSub
    return Client(host=args.host)


def publisher():
    """
    Loops forever, publishing messages to random channels.
    """
    client = new_client()
    message = u"x" * args.message_size
    while True:
        client.publish(random.choice(channels), message)


def subscriber():
    """
    Subscribes to all channels, keeping a count of the number of
    messages received. Publishes and resets the total every second.
    """
    client = new_client()
    pubsub = client.pubsub()
    for channel in channels:
        pubsub.subscribe(channel)
    last = time.time()
    messages = 0
    for message in pubsub.listen():
        messages += 1
        now = time.time()
        if now - last > 1:
            if not args.quiet:
                print messages, "msg/sec"
            client.publish("metrics", str(messages))
            last = now
            messages = 0


def run_workers(target):
    """
    Creates processes * --num-clients, running the given target
    function for each.
    """
    for _ in range(args.num_clients):
        proc = multiprocessing.Process(target=target)
        proc.daemon = True
        proc.start()


def get_metrics():
    """
    Subscribes to the metrics channel and returns messages from
    it until --num-seconds has passed.
    """
    client = new_client().pubsub()
    client.subscribe("metrics")
    start = time.time()
    while time.time() - start <= args.num_seconds:
        message = client.listen().next()
        if message["type"] == "message":
            yield int(message["data"])


if __name__ == "__main__":

    # Set up and parse command-line args.
    global args, channels
    default_num_clients = multiprocessing.cpu_count() / 2
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--num-clients", type=int, default=default_num_clients)
    parser.add_argument("--num-seconds", type=int, default=10)
    parser.add_argument("--num-channels", type=int, default=50)
    parser.add_argument("--message-size", type=int, default=20)
    parser.add_argument("--redis", action="store_true")
    parser.add_argument("--unbuffered", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    channels = [str(i) for i in range(args.num_channels)]

    # Create publisher/subscriber goroutines, pausing to allow
    # publishers to hit full throttle
    run_workers(publisher)
    time.sleep(1)
    run_workers(subscriber)

    # Consume metrics until --num-seconds has passed, and display
    # the median value.
    metrics = sorted(get_metrics())
    print metrics[len(metrics) / 2], "median msg/sec"
