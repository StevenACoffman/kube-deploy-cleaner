
### Kubernetes Deployment Cleaner

Very simple script to delete all expired deployments after they pass their annotated expiration time.

In our continuous integration (aka c20n) environment, we wish to have the deployments be deleted after about 4 hours. We annotated these ephemeral deployments with a key `deploymentExpirationTime` that contains a value four hours in the future, like `2018-07-19T16:29:38Z`.

Building the Docker image:

```bash
    $ make
```

Deploying:

```bash

    $ kubectl apply -f deploy/
```

###### There are a few options:

+ `--dry-run` - Do not actually remove any deployments, only print what would be done


#### Credit Where Credit is Due

This code was very lightly modified from [kube-job-cleaner](https://github.com/hjacobs/kube-job-cleaner) (aka rip off). 