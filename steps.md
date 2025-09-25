# Initial Steps

This is a rough breakdown of manually creating a vLLM deployment on Arm based GKE.

## Prepare cluster

TODO: Make sure original microservice repo is fully deployed and working

## Prepare Llama.cpp

TODO: Write section about making llama cpp image

1. Download llama.cpp repo (NOTE COMMIT/VERSION IN DOCUMENTATION)
1. Build from docker file in that repo (Should build both CLI and Server images from one docker file)
1. Upload JUST THE SERVER image to Google Artifact Registry

Make an image from docker template to be included in this repo, using command that ensures it makes an arm64 ONLY build

## Prepare Model

TODO: Finalize this section

Using Llama.cpp CLI image we just built

Get a hugging face token and save it for this step

Download locally `google/gemma-3-4b-it` using Hugging Face.

Optimize it for Axion architecture

## Deploy Llama.cpp kubernetes

TODO: Fill out section to deploy llama.cpp image

## Deploy model file

TODO: Fill out section

Upload file into persistent file storage in our existing GKE.

## Test AI

TODO: Run a curl command and make sure it works

## Prepare Shopping Assistant

TODO: Fill out this section

Make an image for shopping assistant based on files in this repo

## Deploy Shopping Assistant

TODO: Fill out this

Deploy the shopping assistant to existing kubernetes cluster

## Test

TODO: fill out section

Make sure it works!



# Old sections, keeping for reference to fill out above

### OLD: Kubernetes Apply

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

### OLD Testing

Insert pod name here and run curl locally on pod

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
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
