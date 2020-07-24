# Development guide with Skaffold

Skaffold allows for a fast development workflow on Kubernetes, it builds images with Kaniko and deploys the Stackl containers using Helm.
After saving changes it will synchronize the changed files with the running containers instead of building new images when possible.

## Prerequisites:

Follow the installation guides for your operating system.

- microk8s: https://microk8s.io/docs/
- skaffold: https://skaffold.dev/


## Enable pulling from registry

Enable the required add-ons:
```shell script
microk8s.enable dns
microk8s.enable registry
```

Connect to the vm on Windows/Mac

```shell
multipass shell microk8s-vm
```

Edit the containerd settings:

```shell script
vim /var/snap/microk8s/current/args/containerd-template.toml
```

Add this to the existing `[plugins.cri.registry]` section.
```toml
[plugins.cri.registry.mirrors."registry.container-registry.svc.cluster.local:5000"]
  endpoint = ["http://registry.container-registry.svc.cluster.local:5000"]
```

*optional*: Kaniko warmer: to build the images the RUN layers are stored in the registry, you can also cache base-images by storing them locally.

Linux

```shell script
make kaniko-warmer
```

Windows/Mac

```shell script
podman run -v /var/snap/microk8s/common/kaniko/:/workspace gcr.io/kaniko-project/warmer:latest --cache-dir=/workspace/cache --image=stacklio/grpc-base:latest --image=registry.access.redhat.com/ubi8/ubi-minimal:8.2-301
exit
```

# Configuring access to the cluster and kubectl
```sh
microk8s.config > $HOME/.kube/config-microk8s
export KUBECONFIG=$HOME/.kube/config-microk8s
```

You can now see your single node cluster:
```shell script
kubectl get nodes
```

## Add DNS resolver for enterprise networks

When you connect to an enterprise network, Microk8s doesn't automatically add the DNS-servers like your VPN client does.

You can add these to the K8s dns resolvers by updating a configmap.

```shell script
kubectl apply -f stackl/docs/devel/coredns-configmap.yml
```

for every domain you can add a section as can be seen [coredns-configmap.yml](coredns-configmap.yml).

The pods restart automatically after detecting the configuration changes.

## Circumventing registry lookups from Skaffold

By default Skaffold checks if images are created on the registry from the host instead of inside the k8s cluster.

This can be solved by adding an entry to `/etc/hosts`:

```shell script
127.0.0.1 registry.container-registry.svc.cluster.local
```

and port-forwarding to the registry service

```shell script
kubectl port-forward service/registry -n container-registry 5000:5000 &
```

## Engines ready

You can start `skaffold` now and starting developing new features/fixes.
```shell script
skaffold dev --force=false --port-forward
```

You can visit the Stackl REST API by going to http://127.0.0.1:8080/docs

## FAQ

