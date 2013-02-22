package main

import (
	"./pubsub"
	"flag"
	"fmt"
	"math/rand"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"time"
)

var (
	host        string
	numSeconds  float64
	numClients  int
	numChannels int
	messageSize int
	useRedis    bool
	quiet       bool
	channels    []string
)

// Returns a new pubsub client instance - either the Redis or ZeroMQ
// client, based on command-line arg.
func NewClient() pubsub.Client {
	var client pubsub.Client
	if useRedis {
		client = pubsub.NewRedisClient(host)
	} else {
		client = pubsub.NewZMQClient(host)
	}
	return client
}

// Loops forever, publishing messages to random channels.
func Publisher() {
	client := NewClient()
	message := strings.Repeat("x", messageSize)
	for {
		channel := channels[rand.Intn(len(channels))]
		client.Publish(channel, message)
	}
}

// Subscribes to all channels, keeping a count of the number of
// messages received. Publishes and resets the total every second.
func Subscriber() {
	client := NewClient()
	for _, channel := range channels {
		client.Subscribe(channel)
	}
	last := time.Now()
	messages := 0
	for {
		client.Receive()
		messages += 1
		now := time.Now()
		if now.Sub(last).Seconds() > 1 {
			if !quiet {
				println(messages, "msg/sec")
			}
			client.Publish("metrics", strconv.Itoa(messages))
			last = now
			messages = 0
		}
	}
}

// Creates goroutines * --num-clients, running the given target
// function for each.
func RunWorkers(target func()) {
	for i := 0; i < numClients; i++ {
		go target()
	}
}

// Subscribes to the metrics channel and returns messages from
// it until --num-seconds has passed.
func GetMetrics() []int {
	client := NewClient()
	client.Subscribe("metrics")
	metrics := []int{}
	start := time.Now()
	for time.Now().Sub(start).Seconds() <= numSeconds {
		message := client.Receive()
		if message.Type == "message" {
			messages, _ := strconv.Atoi(message.Data)
			metrics = append(metrics, messages)
		}
	}
	return metrics
}

func main() {

	// Set up and parse command-line args.
	runtime.GOMAXPROCS(runtime.NumCPU())
	flag.StringVar(&host, "host", "127.0.0.1", "")
	flag.Float64Var(&numSeconds, "num-seconds", 10, "")
	flag.IntVar(&numClients, "num-clients", 1, "")
	flag.IntVar(&numChannels, "num-channels", 50, "")
	flag.IntVar(&messageSize, "message-size", 20, "")
	flag.BoolVar(&useRedis, "redis", false, "")
	flag.BoolVar(&quiet, "quiet", false, "")
	flag.Parse()
	for i := 0; i < numChannels; i++ {
		channels = append(channels, strconv.Itoa(i))
	}

	// Create publisher/subscriber goroutines, pausing to allow
	// publishers to hit full throttle
	RunWorkers(Publisher)
	time.Sleep(1 * time.Second)
	RunWorkers(Subscriber)

	// Consume metrics until --num-seconds has passed, and display
	// the median value.
	metrics := GetMetrics()
	sort.Ints(metrics)
	fmt.Println(metrics[len(metrics)/2], "median msg/sec")

}
