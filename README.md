# GKE-Blog

In this repository, we use the Google Kubernetes Engine (GKE) to create an application with two services in the same cluster.
The goal is to display communication between two service applications within the cluster.


## Getting started

Be sure to *[install](https://cloud.google.com/sdk/docs/install)* and *[initialize](https://cloud.google.com/sdk/docs/initializing)* the SDK offered by Google.
Allow billing and start a project.
The Google Cloud Platform (GCP) offers a free trial!
Replace your `YOUR_PROJECT_ID` with your actualy project ID in all of the following.


## Create the cluster

We create a cluster with a single node on GKE to host our application.
This cluster is named blog-cluster
```
gcloud container clusters create blog-cluster \
    --num-nodes 1 \
    --zone us-central1
```
On the Google Cloud Console under the Kubernetes tab, you should see something like the following:

![Cluster](https://github.com/scm-enfuse/GKE-Project/blob/master/images/cluster.png)

After creating the cluster, configure Kubectl.

```
gcloud container clusters get-credentials blog-cluster
```

## Containerized Service Application

One application we host on GKE simply returns a value (in this case the string "success") upon  request.

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "success"

if __name__ == '__main__':
    app.run(host='127.0.0.1', use_reloader=True, port=7000, debug=True)
```

Containerize the application and push to the Container Registry on GCP.
We will name the container `serv`. The next command requires you to be in the `serv` directory.
```
cd serv
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/serv .
cd ..
```

This application can now be tested on Cloud Run.
To do so, go to the Container Registry tab on Google Cloud Console.
Our `serv` container should be there.
Click on the latest pushed image.
You should see something like the following.

![Cloud Run](https://github.com/scm-enfuse/GKE-Project/blob/master/images/run.png)

Click on `Deploy` and select `Deploy to Cloud Run`.
You will then be prompted to create the service.
Be sure, under the Advanced settings, to change the container port to 7000.
Select the option to allow unauthenticated access.
If everything has been done properly, "success" should be displayed.

The deployment configuration for the workload are as follows:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: serv-app.0.0.0
spec:
  replicas: 1
  selector:
    matchLabels:
      app: blog
  template:
    metadata:
      labels:
        app: blog
    spec:
      containers:
      - name: serv
        image: gcr.io/YOUR_PROJECT_ID/serv:latest
        # This app listens on port 8080 for web traffic by default.
        ports:
        - containerPort: 7000
        env:
          - name: PORT
            value: "7000"
```
The `blog` labels bind applications with the same label so they are able to communicate.
The port values should match the port exposed on the Flask Application (in this case, 7000).
Deploy the workload to kubernetes.

```
kubectl apply -f serv/deployment.yaml
```
![Workload](https://github.com/scm-enfuse/GKE-Project/blob/master/images/cluster.png/workload.png)

Now it's time to create our service.
To expose the service to the cluster only, we need to label the service as type `ClusterIP`.

```
apiVersion: v1
kind: Service
metadata:
  name: serv-service000
  labels:
    app: blog
spec:
  type: ClusterIP
  selector:
    app: blog
  ports:
  - port: 80 # any port other pods use to access the Service
    targetPort: 7000 # the port the container accepts traffic on (default is 8080)
```

The service will be granted its unique ClusterIP address and exposes the service on port 80 to any workload in the cluster with the blog label.
Apply the service.
```
g
```
Check to see if the service configuration was successfull.
```
kubectl get services
```
Notice a new IP address was assigned to our service.
We will use the serv-service000 entrypoint on port 80 in our next application.

```
NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)        AGE
serv-service000      ClusterIP      10.83.252.229   <none>         80/TCP         19h
kubernetes           ClusterIP      10.83.240.1     <none>         443/TCP        19h
```

## LoadBalancer to Display Query


Now our focus shifts to containerizing an application accessible outside the cluster with an external ip address.
This application will make a request to the `serv`.

```
from flask import Flask
import json
import requests

cluster_ip_address = "SERV-CLUSTER-IP"
service_port = "80"

app = Flask(__name__)

@app.route('/')
def home():
    doc = requests.get(f"http://{cluster_ip_address}:{service_port}/")
    return f"Value from service: {doc.text}"

if __name__ == '__main__':
    app.run(host='127.0.0.1', use_reloader=True, port=8000, debug=True)
```
An edit is needed in the above file (`display/appy.py`).
Replace `SERV-CLUSTER-IP` with the ClusterIP of the previous service.
Push the image to the GCP Container Registry.
This container will be called `display`.

```
cd display
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/display .
cd ..
```

Deployment configurations are similar to the previous application.
The service differs because we wish to create an entrypoint for this application.
To make this change, this service will be of type LoadBalancer.

```
apiVersion: v1
kind: Service
metadata:
  name: display-service001
spec:
  type: LoadBalancer
  selector:
    app: blog
  ports:
  - port: 80
    targetPort: 8000
```

Apply the deployment and service configuration.

```
kubectl apply -f display/deployment.yaml
kubectl apply -f display/service.yaml
```

To check for success we can use `kubectl get services` which should output something like
```
NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)        AGE
display-service001   LoadBalancer   10.83.247.199   34.69.30.202   80:31108/TCP   28m
kubernetes           ClusterIP      10.83.240.1     <none>         443/TCP        21h
serv-service000      ClusterIP      10.83.241.27    <none>         80/TCP         30m
```
We now have an external ip address to access out app on port 80.
Creating this IP takes a moment so just wait if it's pending.

To make a request, switch this address with your own external ip.
```
curl http://34.69.30.202/
```
This should output
```
Value from service: success
```
upon successful completion.
