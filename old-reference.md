# workshop-ai-gke

A workshop for building out a AI application using Google Kubernetes Engine

## Initial Setup

This lab builds upon the previous example and assumes you already have a GKE cluster deployed.

## Workshop Steps

Now we can deploy our own custom LLM model to run entirely within our GKE cluster.

### Prepare vLLM image

In order to deploy vLLM on Arm based Axion processors, we need to rebuild it from course code.

To do this, we can [follow the instructions from the official documentation](https://docs.vllm.ai/en/latest/getting_started/installation/cpu.html).

Clone the vLLM repo:

<ql-code-block templated bash>
git clone https://github.com/vllm-project/vllm.git vllm_source
cd vllm_source
</ql-code-block>

Now we can build the vLLM image using Docker

<ql-code-block templated bash>
docker build -f docker/Dockerfile.cpu --tag vllm-cpu-env .
</ql-code-block>

Next, in the real world we would push our image to our GCP Project's Artifact Repo. Ensuring that your user account has READ access.

However, we have done the work for you, so we can move onto the next step.

### Prepare Model

Download locally a model using Hugging Face. I did gemma-3-270m for first test just because it was so small made it faster.

Do optimizations for it here.

Ensure it downloads the model do you hugging face cache folder.

<ql-code-block>
~/.cache/huggingface/hub/models--google--gemma-3-270m/
</ql-code-block>

### Prepare Kubernetes

We need to create a Storage Class, a Persistent Volume Claim, a Compute Class, and a Secret.

Let's review each file:

#### `k8s/1-setup/c4a-cc.yml`

Defines a compute class of c4a with a minimum of 4 cores.

<ql-code-block templated bash>
kubectl apply -f k8s/1-setup/c4a-cc.yml
</ql-code-block>

#### `k8s/1-setup/storage-class.yml`

Make a storage class that works with c4a. "persistent" not available on c4a, needs to be "hyperdisk"

<ql-code-block templated bash>
kubectl apply -f k8s/1-setup/storage-class.yml
</ql-code-block>

#### `k8s/1-setup/pvc.yml`

Set up our model persistent volume storage we will mount to our vLLM pod.

<ql-code-block templated bash>
kubectl apply -f k8s/1-setup/pvc.yml
</ql-code-block>

#### `k8s/1-setup/secret.yml`

Set our Hugging Face secret. Note you will need to modify this to include your unqiue secret read access token

TODO: Flesh out this step with more specifics and maybe google variables.

<ql-code-block templated bash>
kubectl apply -f k8s/1-setup/secret.yml
</ql-code-block>

### Upload model to Kubernetes

We now need to make a basic pod that mounts our persistent storage we just created. Then we can copy our local model file into our kubernetes cluster.

<ql-code-block templated bash>
kubectl apply -f k8s/2-temp-loader.yml
</ql-code-block>

Now we need to copy the file:

<ql-code-block templated bash>
kubectl cp ~/.cache/huggingface/hub/models--google--gemma-3-270m/ init-storage-pod:/data/hub/models--google--gemma-3-270m/

Ensure your paths are correct. Give it a minute for the command to upload the file, this may take a moment due to size.

Once the file is updated successfully, we no longer want our temporary pod.

<ql-code-block templated bash>
kubectl delete -f k8s/2-temp-loader.yml
</ql-code-block>

TODO: Note that this whole section doesn't matter if the model we want quantized how we want it is publicly available on HuggingFace and GKE can download from outside.

### Deploy vLLM to Kubernetes

Now it's time to deploy our service and pod for vLLM itself, using a publicly available version of the image we made earlier.

First, ensure the environment variables defined here are correct

TODO: Go through environment variables for vLLM pod. Needed to pass `--disable-sliding-window` but that may depend on model

<ql-code-block templated bash>
kubectl apply -f k8s/3-deploy.yml
</ql-code-block>

### Deploy Microservice to Kubernetes

Deploy our microservice we need to connect to existing project.

Also make sure we set variables correctly in project to point to this microservice, and the microservice has variable to point to vllm instance

TODO: Write section on Microservice

## Testing

TODO: Write section on Testing

Insert pod name here and run curl locally on pod

```bash
kubectl exec vllm-server-f98779f6b-66mdr -- curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "/root/.cache/huggingface/models--google--gemma-3-270m/snapshots/9b0cfec892e2bc2afd938c98eabe4e4a7b1e0ca1",
        "prompt": "San Francisco is a",
        "max_tokens": 7,
        "temperature": 0
    }'
```
