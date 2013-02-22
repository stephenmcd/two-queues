package pubsub

import (
	zmq "github.com/alecthomas/gozmq"
	"time"
)

func Serve(quiet bool) {

	context, _ := zmq.NewContext()
	receiver, _ := context.NewSocket(zmq.PULL)
	receiver.Bind("tcp://*:5562")
	sender, _ := context.NewSocket(zmq.PUB)
	sender.Bind("tcp://*:5561")

	last := time.Now()
	messages := 0
	for {
		message, _ := receiver.Recv(0)
		sender.Send(message, 0)
		if !quiet {
			messages += 1
			now := time.Now()
			if now.Sub(last).Seconds() > 1 {
				println(messages, "msg/sec")
				last = now
				messages = 0
			}
		}
	}

}
