# workshop-ai-gke

A workshop for building out a AI application using Google Kubernetes Engine

## 0. Requirements

This lab builds upon the previous example and assumes you already have a GKE cluster deployed running the [Online Boutique microservices demo application](https://github.com/GoogleCloudPlatform/microservices-demo).

If you do not, please run the previous lab first and then return to this lab.

## 1. Prepare work environment

TODO MICHAEL: Explain this

We will be building Llama.cpp optimized specifically for Axion CPUs.

To do that, we'll first create a VM in Google Cloud on an Axion instance to use as our build environment.

### Create build environment VM

Get a Virtual Machine running Axion that we can work in

(THIS MAY ALREADY BE PART OF FIRST WORKSHOP?)

<ql-code-block templated bash>
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
</ql-code-block>

### Connect to build VM

<ql-code-block templated bash>
gcloud compute ssh $INSTANCE_NAME --zone $ZONE --ssh-flag='-l cos'
</ql-code-block>

## 2. Prepare Llama.cpp

TODO MICHAEL: Write section about making llama cpp image

Build from docker file in that repo (Should build both full and Server images from one docker file)

<ql-code-block templated bash>
export DOCKER_IMAGE="armsoftwaredev/llama-cpp"
docker buildx build -f llm/Dockerfile --target full --tag ${DOCKER_IMAGE}:latest .
docker buildx build -f llm/Dockerfile --target server --tag ${DOCKER_IMAGE}-server:latest .
</ql-code-block>

Upload JUST THE SERVER image to Google Artifact Registry

Make an image from docker template to be included in this repo, using command that ensures it makes an arm64 ONLY build

## 3. Prepare Model

TODO MICHAEL: Finalize this section

Get a hugging face token and save it for this step
Download locally `google/gemma-3-4b-it` using Hugging Face.

<ql-code-block templated bash>
export HF_TOKEN=<your_hf_token>
huggingface-cli download google/gemma-3-4b-it-qat-q4_0-gguf
</ql-code-block>

Using Llama.cpp CLI image we just built, optimize it for Axion architecture

<ql-code-block templated bash>
docker run -v ~/.cache/huggingface/hub/:/app/hfmodels -v ./:/app/localdir ${DOCKER_IMAGE} --quantize --allow-requantize /app/hfmodels/models--google--gemma-3-4b-it-qat-q4_0-gguf/snapshots/15f73f5eee9c28f53afefef5723e29680c2fc78a/gemma-3-4b-it-q4_0.gguf /app/localdir/gemma-3-4b-it-q4_0_arm.gguf Q4_0
cp ~/.cache/huggingface/hub/models--google--gemma-3-4b-it-qat-q4_0-gguf/snapshots/15f73f5eee9c28f53afefef5723e29680c2fc78a/mmproj-model-f16-4B.gguf ./
</ql-code-block>

TODO Michael: Make sure file path is correct to be able to easily copy files into pod running server

## 3. Deploy Llama.cpp kubernetes

Now it is time to deploy our server to our Kubernetes cluster.

### Storage

Before we can deploy our service however, need to create a Storage Class and Persistent Volume Claim to store our model files.

Let's review the two files:

#### `server/k8s/storage-class.yml`

Make a storage class that works with `C4A` class compute. "`persistent`" storage is not available on `C4A`, needs to be "`hyperdisk`"

Deploy the storage class first:

<ql-code-block templated bash>
kubectl apply -f server/k8s/storage-class.yml
</ql-code-block>

#### `server/k8s/pvc.yml`

This sets up our model persistent volume storage we will mount to our server pod.

Deploy it after defining the storage class:

<ql-code-block templated bash>
kubectl apply -f server/k8s/pvc.yml
</ql-code-block>

### Deploy service

Now it's time to deploy our service and pod for the server, using a publicly available version of the image we made earlier.

<ql-code-block templated bash>
kubectl apply -f server/k8s/deploy.yml
</ql-code-block>

TODO AVIN: Explain this further
TODO MICHAEL: Confirm server arguments, where model file(s) need to be.

### Deploy model file

Now we need to load our model files into the persistent storage in our GKE.

Since we already deployed our service, we can get the name of the pod and copy the files directly into the storage. This storage will be shared by all pods as things scale or restart.

<ql-code-block templated bash>
kubectl cp ./models/ llm-server:/models/
</ql-code-block>

TODO AVIN: Ensure pod name and file paths are correct here

Ensure your paths are correct. Give it a minute for the command to upload the file, this may take a moment due to size.

Once the file is updated successfully, we may need to restart the pod.

## 4. Test AI

TODO MICHAEL: Run a curl command and make sure it works

```bash
kubectl exec llm-server -- curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
  "model": "google/gemma-3-4b-it",
    "messages": [
    {
        "role": "user",
        "content": [
        {
            "type": "text",
            "text": "Describe what a pizza is."
        }]
    }]
  }'
```

## 5. Prepare Shopping Assistant

TODO MICHAEL: Finalize code to remove hard coded database
TODO AVIN: Fill out this section

Make an image for shopping assistant based on files in this repo

Ensure environment variable is hard coded to internal URL of already deployed llama.cpp

## 6. Deploy Shopping Assistant

TODO AVIN: Fill out this

Deploy the shopping assistant to existing kubernetes cluster

## 7. Test

TODO MICHAEL: fill out section

Make sure it works!
