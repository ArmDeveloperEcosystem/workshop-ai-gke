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

Ensure it downloads the model do you hugging face cache folder

<ql-code-block>
~/.cache/huggingface/hub/models--google--gemma-3-270m/
</ql-code-block>

### Prepare Kubernetes

We need to create a Storage Class, a Persistent Volume Claim, a Compute Class, and a Secret.

TODO: Give step by step lines of code to apply each of these

- k8s/1-setup/c4a-cc.yml
    Defines a compute class of c4a with a minimum of 4 cores

- k8s/1-setup/storage-class.yml
    Make a storage class that works with c4a ("persistent" not available, needs to be "hyperdisk")

- k8s/1-setup/pvc.yml
    Set up our model storage

- k8s/1-setup/secret.yml
    Set our Hugging Face secret
    Modify the file manually to include your unique secret token.
    TODO: Flesh out secret steps

### Upload model to Kubernetes

- init.yml
    Load the files into persistent storage.

    Can't access it directly so making a simple pod that can copy the files locally into.

    ```bash
    kubectl cp ~/.cache/huggingface/hub/models--google--gemma-3-270m/ init-storage-pod:/data/hub/models--google--gemma-3-270m/
    ```

    Ensure paths are correct, but above by default should be right.

### Deploy vLLM to Kubernetes

- service.yaml
    Actually deploy vLLM!

    Note the required environment variables.

    Needed to pass `--disable-sliding-window` but that may depend on model

    Using a specfic image name from my local downloaded hugging face. In final form will need to confirm that is right snapshot id.

### Deploy Microservice to Kubernetes

Deploy our microservice we need to connect to existing project.

Also make sure we set variables correctly in project to point to this microservice, and the microservice has variable to point to vllm instance

## Testing

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
