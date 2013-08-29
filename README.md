A Tale of Two Queues
====================

Related source code for my blog post
[A Tale of Two Queues](http://blog.jupo.org/2013/02/23/a-tale-of-two-queues/),
benchmarking [Redis](http://redis.io) and [ZeroMQ](http://www.zeromq.org)
pub-sub, using [Python](http://python.org) and Google's
[Go language](http://golang.org).

Software and Libraries
======================

Following are the software and library requirements for running these
benchmarks, using [homebrew](http://mxcl.github.com/homebrew) for OSX,
[pip](http://www.pip-installer.org) for Python and [go get](
http://golang.org/cmd/go/#hdr-Download_and_install_packages_and_dependencies)
for Go. Installation should be similar on various Linuxes using their respective
package managers rather than homebrew. You'll also need to run Redis once
installed.

    $ brew install zeromq [1]
    $ brew install redis [2]
    $ brew install gnuplot [3]
    $ pip install pyzmq [4]
    $ pip install redis [5]
    $ pip install hiredis [6]
    $ go get github.com/garyburd/redigo/redis [7]
    $ go get github.com/alecthomas/gozmq [8]

1. <http://www.zeromq.org>
2. <http://redis.io>
3. <http://www.gnuplot.info>
4. <https://github.com/zeromq/pyzmq>
5. <https://github.com/andymccurdy/redis-py>
6. <https://github.com/pietern/hiredis-py>
7. <https://github.com/garyburd/redigo>
8. <https://github.com/alecthomas/gozmq>

Contributions
=============

Here are some interesting additions others have contributed:

  * [Elixir on the Erlang VM](https://github.com/stephenmcd/two-queues/pull/2)
  * [Redis 2.6.10 vs ZeroMQ 3.2.3](https://github.com/stephenmcd/two-queues/issues/1)
  * [MQTT broker addition](https://github.com/stephenmcd/two-queues/pull/5)



