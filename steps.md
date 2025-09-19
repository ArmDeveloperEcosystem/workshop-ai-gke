# Initial Steps

This is a rough breakdown of manually creating a vLLM deployment on Arm based GKE.

## Prepare vLLM

https://docs.vllm.ai/en/latest/getting_started/installation/cpu.html

1. Clone vLLM repo
1. Build via docker

```bash
docker build -f docker/Dockerfile.cpu --tag vllm-cpu-env .
```

Push to GKE Artifact Repo

1. Ensure it is in correct project
1. Ensure that your user account has READ access, not just admin access. (Public is also good)

## Prepare cluster

1. Deploy manual Cluster

On Arm internal subscription, must not use IP to connect. Ensure "Private" is check and IP address is unchecked

## Prepare Model

Download locally a model using Hugging Face. I did gemma-3-270m for first test just because it was so small made it faster.

Ideally do optimizations for it here.

## Kubernetes Apply

In order.

- c4a-cc.yaml
    NOT USED, but need if doing auto. Will have working example in final workshop

- hdb-example-class.yaml
    Make a storage that works with c4a ("persistent" not available, needs to be "hyperdisk")

- pvc.yml
    Connect to storage and also set secret
    Will need to set secret in "proper" way in final workshop. This is secure, but may be better to not manually set. Or manual may be fine, we'll see.

- init.yml
    Load the files into persistent storage.

    Can't access it directly so making a simple pod that can copy the files locally into.

    ```bash
    kubectl cp ~/.cache/huggingface/hub/models--google--gemma-3-270m/ init-storage-pod:/data/hub/models--google--gemma-3-270m/
    ```

    Ensure paths are correct, but above by default should be right.

- service.yaml
    Actually deploy vLLM!

    Note the required environment variables.

    Needed to pass `--disable-sliding-window` but that may depend on model

    Using a specfic image name from my local downloaded hugging face. In final form will need to confirm that is right snapshot id.

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
