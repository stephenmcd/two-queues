#!/usr/bin/env python

from os import mkdir
from os.path import join
from multiprocessing import cpu_count
from subprocess import Popen, check_output, PIPE
from sys import stdout


def popen_args(filename, *args):
    """
    Returns the initial popen args for a given Python or Go file.
    """
    args = [filename, "--quiet"] + list(args)
    if filename.split(".")[-1] == "py":
        return ["python"] + args
    else:
        return ["go", "run"] + list(args)


def run_clients(lang, *args):
    """
    Runs the test_client program for Python or Go, for the range
    from 1 to cpus * 2 as the number of clients, returning the
    mediam messsages per second for each.
    """
    if "--redis" not in args:
        broker = Popen(popen_args("run_broker.%s" % lang), stderr=PIPE)
    args = popen_args("test_client.%s" % lang, *args)
    args.append("--num-seconds=3")
    results = []
    num_runs = cpu_count() * 2
    print " ".join(args)
    for clients in range(1, num_runs + 1):
        bar = ("#" * clients).ljust(num_runs)
        stdout.write("\r[%s] %s/%s " % (bar, clients, num_runs))
        stdout.flush()
        out = check_output(args + ["--num-clients=%s" % clients], stderr=PIPE)
        results.append(out.split(" ")[0].strip())
    stdout.write("\n")
    if "--redis" not in args:
        broker.kill()
    return results

# All test_client runs and their cli args.
runs = {
    "py_redis": ["py", "--redis", "--unbuffered"],
    "py_redis_buffered": ["py", "--redis"],
    "py_zmq": ["py"],
    "go_redis": ["go", "--redis"],
    "go_zmq": ["go"],
}

# Consistent graph colours defined for each of the runs.
colours = {
    "py_redis": "red",
    "py_redis_buffered": "green",
    "py_zmq": "blue",
    "go_redis": "violet",
    "go_zmq": "orange",
}

# Groups of runs mapped to each graph.
plots = {
    "two-queues-1": ["py_zmq", "py_redis"],
    "two-queues-2": ["py_zmq", "py_redis", "py_redis_buffered"],
    "two-queues-3": ["py_zmq", "py_redis", "py_redis_buffered",
                     "go_zmq", "go_redis"],
}

# Store all results in an output directory.
output_path = lambda s="": join("output", s)
try:
    mkdir(output_path())
except OSError:
    pass

# Store results from each test_client run into files.
for name, args in runs.items():
    with open(output_path(name + ".dat"), "w") as f:
        f.write("\n".join(run_clients(*args)))

# Generate graphs.
with open("plot.p", "r") as f:
    plotfile = f.read()
line = '"%s.dat" using ($0+1):1 with lines title "%s" lw 2 lt rgb "%s"'
for name, names in plots.items():
    name = output_path(name)
    with open(output_path(names[0] + ".dat"), "r") as f:
        clients = len(f.read().split())
    with open(name + ".p", "w") as f:
        lines = ", ".join([line % (l, l.replace("_", " "), colours[l])
                           for l in names])
        f.write(plotfile % {"name": name, "lines": lines, "clients": clients})
    Popen(["gnuplot", name + ".p"], stderr=PIPE)
