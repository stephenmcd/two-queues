package main

import (
	"./pubsub"
	"flag"
)

func main() {
	var quiet bool
	flag.BoolVar(&quiet, "quiet", false, "")
	flag.Parse()
	pubsub.Serve(quiet)
}
