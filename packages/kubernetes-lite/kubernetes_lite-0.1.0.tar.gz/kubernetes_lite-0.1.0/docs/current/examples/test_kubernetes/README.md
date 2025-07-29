# Pytest Example using EnvTest and the Official Kubernetes Python Client

This example walks through using the EnvTest module with pytest to test the official [kubernetes](https://github.com/kubernetes-client/python) library. This example showcases using both the kubernetes CoreV1Api and DynamicClient classes with envtest

## Running this example

Install kubernetes_lite, kubernetes, and pytest on your local machine

```
# Kubernetes Install
pip3 install kubernetes
# Pytest Install
pip3 install pytest
# Remote Kubernetes Lite Install
pip3 install kubernetes_lite
# Local Kubernetes Lite Install
pip3 install -e "."
```

Download the [test_kubernetes.py](./test_kubernetes.py) example file.

Run pytest against this example

```
python3 -m pytest test_kubernetes.py
```

You should see the following output from pytest:
```bash
❯ python3 -m pytest test_kubernetes.py
=============================================== test session starts ===============================================
platform darwin -- Python 3.11.5, pytest-8.3.2, pluggy-1.5.0
rootdir: <>
configfile: pyproject.toml
plugins: cov-5.0.0, anyio-4.8.0, typeguard-2.13.3, timeout-2.3.1
collected 2 items                                                                                                 

test_kubernetes.py ..                                                                              [100%]

================================================ 2 passed in 5.17s ================================================
```

## Troubleshooting

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