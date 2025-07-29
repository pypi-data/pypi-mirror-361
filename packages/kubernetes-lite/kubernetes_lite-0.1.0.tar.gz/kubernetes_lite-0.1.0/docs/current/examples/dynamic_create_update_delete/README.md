# Create, Update & Delete Deployment with the Dynamic Client

This example is almost a direct copy of the [client-go](https://github.com/kubernetes/client-go/blob/master/examples/dynamic-create-update-delete-deployment/README.md) example of the same name. This demonstrates the fundamental operations for managing on Deployment resources, such as Create, List, Update and Delete using the kubernetes_lite client.


## Running this example

Make sure you have a Kubernetes cluster and `kubectl` is configured:
```
kubectl get nodes
```

Install the kubernetes_lite package on your workstation:

```
# Remote Install
pip3 install kubernetes_lite
# Local Install
pip3 install -e "."
```

Next, download [dynamic_create_update_delete_deployment.py](./dynamic_create_update_delete_deployment.py) onto your workstation and run it with your local kubeconfig file:

```
python3 dynamic_create_update_delete_deployment.py
# or specify a kubeconfig file with flag
python3 dynamic_create_update_delete_deployment.py -kubeconfig=$HOME/.kube/config
```

Running this command will execute the following operations on your cluster:

1. **Create Deployment:** This will create a 2 replica Deployment. Verify with
   `kubectl get pods`.
2. **Update Deployment:** This will update the Deployment resource created in
   previous step by setting the replica count to 1 and changing the container
   image to `nginx:1.13`. You are encouraged to inspect the retry loop that
   handles conflicts. Verify the new replica count and container image with
   `kubectl describe deployment demo`.
3. **List Deployments:** This will retrieve Deployments in the `default`
   namespace and print their names and replica counts.
4. **Delete Deployment:** This will delete the Deployment object and its
   dependent ReplicaSet resource. Verify with `kubectl get deployments`.

Each step is separated by an interactive prompt. You must hit the
<kbd>Return</kbd> key to proceed to the next step. You can use these prompts as
a break to take time to run `kubectl` and inspect the result of the operations
executed.

You should see an output like the following:

```
Creating deployment...
Created deployment "demo-deployment".
-> Press Return key to continue.
Updating deployment...
Updated deployment...
-> Press Return key to continue.
Listing deployments in namespace "default":
 * demo-deployment (1 replicas)
-> Press Return key to continue.
Deleting deployment...
Deleted deployment.
```

## Cleanup

Successfully running this program will clean the created artifacts. If you
terminate the program without completing, you can clean up the created
deployment with:

    kubectl delete -n default deploy demo-deployment

## Troubleshooting

If you are getting the following error, make sure Kubernetes version of your
cluster is v1.13 or higher in `kubectl version`:
```
    panic: the server could not find the requested resource
```