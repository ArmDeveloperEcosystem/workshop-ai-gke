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

TODO MICHAEL: Find out how to inject GCP environment variables into this script
TODO MICHAEL: Verify that the c4a-standard-16 and 20GB disk is enough to build and test-run llama.cpp

(THIS MAY ALREADY BE PART OF FIRST WORKSHOP?)

<ql-code-block templated bash>

# Ensure the SSH key exists for gcloud at ~/.ssh/google_compute_engine.pub; generate one with empty passphrase if missing.
if [ ! -f "$HOME/.ssh/google_compute_engine.pub" ]; then
  echo "No SSH key found at ~/.ssh/google_compute_engine.pub. Generating one with an empty passphrase..."
  ssh-keygen -t rsa -b 3072 -N "" -f "$HOME/.ssh/google_compute_engine"
fi
PUB_KEY=$(cat "$HOME/.ssh/google_compute_engine.pub")

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
# INSTANCE_NAME="arm-vm-$(date +%s)"
INSTANCE_NAME="mhall-workshop-build-server"
echo "Creating ARM-based instance $INSTANCE_NAME (machine type: c4a-standard-16)..."
gcloud compute instances create "$INSTANCE_NAME" \
  --zone "$ZONE" \
  --machine-type=c4a-standard-16 \
  --image-family="$IMAGE_FAMILY" \
  --image-project="$IMAGE_PROJECT" \
  --boot-disk-size 200GB \
  --tags=arm-vm \
  --metadata=ssh-keys="cos:${PUB_KEY}" \
  --network="dev-eco-nw-pb" \
  --subet="dev-eco-nw-subnet" \
  --quiet
</ql-code-block>

### Connect to build VM

First we need to copy our build files to the VM instance:

<ql-code-block templated bash>
gcloud compute scp --recurse ./server/ $INSTANCE_NAME:./server/
gcloud compute scp --recurse ./shoppingassistantservice/ $INSTANCE_NAME:./shoppingassistantservice/
</ql-code-block>

Now we can connect to the VM

<ql-code-block templated bash>
gcloud compute ssh $INSTANCE_NAME --zone $ZONE
</ql-code-block>

## 2. Prepare Llama.cpp

TODO MICHAEL: Write section about making llama cpp image

Build from docker file in that repo (Should build both full and Server images from one docker file)

<ql-code-block templated bash>
sudo snap install docker

export DOCKER_IMAGE="llama-cpp"
cd server/
sudo docker buildx build -f Dockerfile --target full --tag ${DOCKER_IMAGE}:latest .
sudo docker buildx build -f Dockerfile --target server --tag ${DOCKER_IMAGE}-server:latest .
</ql-code-block>

Upload JUST THE SERVER image to Google Artifact Registry

Make an image from docker template to be included in this repo, using command that ensures it makes an arm64 ONLY build

### Push llm server image to artifact repository

TODO Michael: This section isn't needed, as we will provide images. But for reference:

<ql-code-block templated bash>
ARTIFACT_REGISTRY="us-east4-docker.pkg.dev/arm-deveco-stedvsl-prd/boutique"

sudo docker tag ${DOCKER_IMAGE}-server ${ARTIFACT_REGISTRY}/${DOCKER_IMAGE}-server
gcloud auth configure-docker us-east4-docker.pkg.dev
sudo docker push ${ARTIFACT_REGISTRY}/${DOCKER_IMAGE}-server
</ql-code-block>

## 3. Prepare Model

TODO MICHAEL: Simplify things by downloading directly to ./models/ instead of HF cache

Get a hugging face token and save it for this step
Download locally `google/gemma-3-4b-it` using Hugging Face.

<ql-code-block templated bash>
sudo apt update && sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate

export HF_TOKEN=<your_hf_token>
mkdir ./models/

huggingface-cli download --local-dir ./models/ google/gemma-3-4b-it-qat-q4_0-gguf
</ql-code-block>

Using Llama.cpp CLI image we just built, optimize it for Axion architecture

<ql-code-block templated bash>
sudo docker run -v ./models:/app/models ${DOCKER_IMAGE} --quantize --allow-requantize /app/models/gemma-3-4b-it-q4_0.gguf /app/models/gemma-3-4b-it-q4_0_arm.gguf Q4_0
</ql-code-block>

### Test quantized model

Test run the model using the llama-cpp-server docker image:

<ql-code-block templated bash>
sudo  docker run -v ./models:/app/models -p 8000:8000 ${DOCKER_IMAGE}-server --model /app/models/gemma-3-4b-it-q4_0_arm.gguf --mmproj /app/models/mmproj-model-f16-4B.gguf --port 8000 --host 0.0.0.0
</ql-code-block>

Then, in another terminal, run:

<ql-code-block templated bash>
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"messages": [
			{
				"role": "user",
				"content": [
					{
						"type": "text",
						"text": "Describe this image in one sentence."
					},
					{
						"type": "image_url",
						"image_url": {
							"url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
						}
					}
				]
			}
		]
	}'
</ql-code-block>

You can see the Llama.cpp logs with the following command:
<ql-code-block templated bash>
sudo docker container logs <container_id> --since 10m
</ql-code-block>

TODO Michael: Make sure file path is correct to be able to easily copy files into pod running server

### Download quantized model

To download the quantized models from your VM to your normal development environment:

Get out of the ssh with `exit`, then copy the model files to your local machine:

<ql-code-block templated bash>
exit
gcloud compute scp --recurse $INSTANCE_NAME:~/models/ ./models/
</ql-code-block>

`$INSTANCE_NAME` is the name of the virtual machine we were just working in.

TODO Michael: Add alternate instructions to download from qwiklab storage?

## 3. Prepare Shopping Assistant

TODO MICHAEL: Finalize code to remove hard coded database

Now we need to build the shoppingassistantserver. Navigate to the folder we uploaded previously and build the docker image:

<ql-code-block templated bash>
cd shoppingassistantservice/src/
sudo docker buildx build -f Dockerfile --tag shoppingassistantservice:latest .
</ql-code-block>

### Push shopping assistant image to artifact repository

TODO Michael: This section isn't needed, as we will provide images. But for reference:

<ql-code-block templated bash>
ARTIFACT_REGISTRY="us-east4-docker.pkg.dev/arm-deveco-stedvsl-prd/boutique"

sudo docker tag shoppingassistantservice ${ARTIFACT_REGISTRY}/shoppingassistantservice
gcloud auth configure-docker us-east4-docker.pkg.dev
sudo docker push ${ARTIFACT_REGISTRY}/shoppingassistantservice
</ql-code-block>

## 4. Deploy Llama.cpp kubernetes

Now it is time to deploy our server to our Kubernetes cluster.

Leave the VM we were working in before using `exit` and get back to your console.

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

Now it's time to deploy our service and pod for the server.

<ql-code-block templated bash>
kubectl apply -f server/k8s/deploy.yml
</ql-code-block>

This will create an initial container that waits until the model files are uploaded, and then will run our llama.cpp server using an image just like the one we built earlier.

TODO MICHAEL: Confirm server arguments, where model file(s) need to be.

### Upload model to Kubernetes

Now we need to load our model files into the persistent storage we just created in our GKE.

We need to copy our model files into the `ensure-files` initContainer. Since the storage will be shared by all pods that mount it, once we copy the file in it will be accessible by our `llm` container.

<ql-code-block templated bash>
kubectl cp ./models/ temp-loader-pod:/ -c ensure-files --disable-compression
</ql-code-block>

Ensure your paths are correct. Give it a minute for the command to upload the file, this may take a moment due to size.

Once the folder is updated successfully, the initContainer should resolve itself and automatically start the server.

## 5. Test AI

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

## 6. Deploy Shopping Assistant

This will create the deployment and service in your cluster for the Shopping Assistant we built earlier.

Before deploying the Shopping Assistant service, you need to update the configuration to point to your running Llama.cpp server.

### Find the LLM Server Load Balancer IP**

To get the IP address of your llm service, run:

```bash
kubectl get svc llm-server
```

Look for the `EXTERNAL-IP` column in the output. Use this IP address in the next step.

### Update the LLM Server Endpoint

Open `shoppingassistantservice/k8s/shoppingassistantservice.yaml` and locate line 54:

```yaml
    value: "http://<internal IP of llm-server>:8000"
```

Replace `<internal IP of llm-server>` with the IP address of your deployed `llm-server` service. Make sure to keep the `:8000` part!

### Deploy the Shopping Assistant Service

Once everything is updated, apply the Kubernetes manifest:

```bash
kubectl apply -k shoppingassistantservice/k8s/
```

## 7. Test

TODO MICHAEL: fill out section

`http://<External IP>/assistant`

Make sure it works!
