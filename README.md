# workshop-ai-gke

A workshop for building out a AI application using Google Kubernetes Engine

## Prepare cluster

TODO AVIN: Make sure original microservice repo is fully deployed and working

## Prepare work environment

TODO MICHAEL: Explain this

Get a Virtual Machine running Axion that we can work in

(THIS MAY ALREADY BE PART OF FIRST WORKSHOP?)

## Prepare Llama.cpp

TODO MICHAEL: Write section about making llama cpp image

1. Download llama.cpp repo (NOTE COMMIT/VERSION IN DOCUMENTATION)
1. Build from docker file in that repo (Should build both CLI and Server images from one docker file)
1. Upload JUST THE SERVER image to Google Artifact Registry

Make an image from docker template to be included in this repo, using command that ensures it makes an arm64 ONLY build

## Prepare Model

TODO MICHAEL: Finalize this section

Using Llama.cpp CLI image we just built

Get a hugging face token and save it for this step

Download locally `google/gemma-3-4b-it` using Hugging Face.

Optimize it for Axion architecture

## Deploy Llama.cpp kubernetes

TODO AVIN: Fill out section to deploy llama.cpp image

## Deploy model file

TODO AVIN: Fill out section

Upload file into persistent file storage in our existing GKE.

## Test AI

TODO MICHAEL: Run a curl command and make sure it works

## Prepare Shopping Assistant

TODO AVIN: Move code into this repo
TODO MICHAEL: Finalize code to remove hard coded database
TODO AVIN: Fill out this section

Make an image for shopping assistant based on files in this repo

Ensure environment variable is hard coded to internal URL of already deployed llama.cpp

## Deploy Shopping Assistant

TODO AVIN: Fill out this

Deploy the shopping assistant to existing kubernetes cluster

## Test

TODO MICHAEL: fill out section

Make sure it works!
