# Kubernetes Lite Walkthrough Via Jupyter Notebook

This example walks through using the kubernetes_lite library with a jupyer notebook. In addition to the client
operations described above, this notebook also showcases using `envtest` to start a cluster.

## Running this example

Install jupyter notebook and kubernetes_lite package on your workstation:

```
# Jupyter Install
pip3 install jupyter
# Remote Kubernetes Lite Install
pip3 install kubernetes_lite
# Local Kubernetes Lite Install
pip3 install -e "."
```

Start an instance of jupyter notebook.

```
python3 -m jupyter notebook
```

Download the [notebook.ipynb](./notebook.ipynb) file to the same local directory you started jupyter notebook in.

Execute the cells in the notebook from top to bottom. There is no need for a cluster connection since this notebook will handle starting an envtest instance 

## Troubleshooting

If you are getting the following error, make sure Kubernetes version of your
cluster is v1.13 or higher in `kubectl version`:

```python
kubernetes_lite.errors.UnknownError: no matches for kind "deployment" in version "apps/v1"
```

If you are getting the following error, the try to download the envtest binaries
before running the example e.g. `python3 -m kubernetes_lite.setup_envtest use`

```python
RuntimeError: unable to start control plane itself: failed to start the controlplane. retried 5 times: fork/exec etcd: no such file or directory
```


## Cleanup

Successfully running this program will correctly stop the envtest server.
If you terminate the program without completing, or an error occurs you can 
ensure all envtest subprocesses have been killed with:

```bash
pkill -9 -f "kubebuilder"
```