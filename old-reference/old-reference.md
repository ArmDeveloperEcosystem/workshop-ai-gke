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

TODO: Note that this whole section doesn't matter if the model is able to be copied in through the main llm server pod deployment
