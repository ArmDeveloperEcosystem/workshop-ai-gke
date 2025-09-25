# workshop-ai-gke

A workshop for building out a AI application using Google Kubernetes Engine

## Prepare cluster

TODO AVIN: Make sure original microservice repo is fully deployed and working

## Prepare work environment

TODO MICHAEL: Explain this

We will be building Llama.cpp optimized specifically for Axion CPUs. 

To do that, we'll first create a VM in Google Cloud on an Axion instance to use as our build environment.

### Create build environment VM
Get a Virtual Machine running Axion that we can work in

(THIS MAY ALREADY BE PART OF FIRST WORKSHOP?)
```
# Retrieve project from gcloud config.
PROJECT=$(gcloud config get-value project)

# Set zone to us-central1-a and derive region.
ZONE="${ZONE:-us-central1-a}"
REGION="${ZONE%-*}"

echo "GCP Project: $PROJECT"
echo "Zone: $ZONE, Region: $REGION"

# Set Ubuntu image variables for ARM64.
IMAGE_FAMILY="ubuntu-2204-lts-arm64"
IMAGE_PROJECT="ubuntu-os-cloud"

# Create an ARM-based VM using the Ubuntu ARM image.
INSTANCE_NAME="arm-vm-$(date +%s)"
echo "Creating ARM-based instance $INSTANCE_NAME (machine type: c4a-standard-16)..."
gcloud compute instances create "$INSTANCE_NAME" \
  --zone "$ZONE" \
  --machine-type=c4a-standard-16 \
  --image-family="$IMAGE_FAMILY" \
  --image-project="$IMAGE_PROJECT" \
  --boot-disk-size 20GB \
  --tags=arm-vm \
  --metadata=ssh-keys="cos:${PUB_KEY}" \
  --quiet
  ```

### Connect to build VM

```
gcloud compute ssh $INSTANCE_NAME --zone $ZONE --ssh-flag='-l cos'
```


## Prepare Llama.cpp

TODO MICHAEL: Write section about making llama cpp image

Build from docker file in that repo (Should build both full and Server images from one docker file)
```
export DOCKER_IMAGE="armsoftwaredev/llama-cpp"
docker buildx build -f llm/Dockerfile --target full --tag ${DOCKER_IMAGE}:latest .
docker buildx build -f llm/Dockerfile --target server --tag ${DOCKER_IMAGE}-server:latest .
```

Upload JUST THE SERVER image to Google Artifact Registry

Make an image from docker template to be included in this repo, using command that ensures it makes an arm64 ONLY build

## Prepare Model

TODO MICHAEL: Finalize this section

Get a hugging face token and save it for this step
Download locally `google/gemma-3-4b-it` using Hugging Face.
```
export HF_TOKEN=<your_hf_token>
huggingface-cli download google/gemma-3-4b-it-qat-q4_0-gguf
```

Using Llama.cpp CLI image we just built, optimize it for Axion architecture
```
docker run -v ~/.cache/huggingface/hub/:/app/hfmodels -v ./:/app/localdir ${DOCKER_IMAGE} --quantize --allow-requantize /app/hfmodels/models--google--gemma-3-4b-it-qat-q4_0-gguf/snapshots/15f73f5eee9c28f53afefef5723e29680c2fc78a/gemma-3-4b-it-q4_0.gguf /app/localdir/gemma-3-4b-it-q4_0_arm.gguf Q4_0 
cp ~/.cache/huggingface/hub/models--google--gemma-3-4b-it-qat-q4_0-gguf/snapshots/15f73f5eee9c28f53afefef5723e29680c2fc78a/mmproj-model-f16-4B.gguf ./
```

## Deploy Llama.cpp kubernetes

TODO AVIN: Fill out section to deploy llama.cpp image

## Deploy model file

TODO AVIN: Fill out section

Upload file into persistent file storage in our existing GKE.

## Test AI

TODO MICHAEL: Run a curl command and make sure it works

## Prepare Shopping Assistant

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
