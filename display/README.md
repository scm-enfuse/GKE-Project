# Price Visualization

Calls get request on endpoint which supplies the current value of a particular stock/currency

container port: 8000
get request to "/" Diplays visulization of updating price data.

Download the requirements.
```
pip install -r requirements.txt
```

The dash app can be ran using
```
python app.py
```
One can containerize the application using docker. Here we name the image scat.
```
docker build -t scat .
```
Run and bind the container port 8000 to local port 8080.
```
docker run --name scat_container -p 8080:8000 scat
```
View the application by typing this into your web browser.
```
http://127.0.0.1:8080/
```
Should output most price visual

```
gcloud builds submit --tag gcr.io/YOUR_PROJECT/scat .
```
In Cloud Run on the GCP Console, you will now be able to enter the image url gcr.io/YOUR_PROJECT/tsla which will refer to the latest version of candle on GCP Container Registry. BE SURE TO SET THE CONTAINER PORT TO 6000. After you've successfully launched your container on Cloud Run, you can map the a custom domain (one you create with Google Domains) to deploy your application. [Here is where to do so!](https://console.cloud.google.com/run/domains?_ga=2.213771028.1062364257.1622766654-335875042.1622766654)

Create a cluster in Google Kubernetes Engine (GKE).
A more detailed description of deploying a python (and others) app to GKE can be found in the [GCP official documentation](https://cloud.google.com/kubernetes-engine/docs/quickstarts/deploying-a-language-specific-app) 
```
gcloud container clusters create stock-cluster \
    --num-nodes 1 \
    --zone us-central1
```

See that the cluster candles-gke has a RUNNING status.
```
kubeconfig entry generated for candles-gke.
NAME         LOCATION     MASTER_VERSION   MASTER_IP       MACHINE_TYPE  NODE_VERSION     NUM_NODES  STATUS
candles-gke  us-central1  1.19.9-gke.1400  35.226.100.180  e2-medium     1.19.9-gke.1400  3          RUNNING
```
The status and availability of nodes int he cluster can be checked using the following command:
```
kubectl get nodes
```
Deploy resources to the cluster and track the status of the deployment.
```
kubectl apply -f deployment.yaml
kubectl get deployments
```
Check the status of the pods created after deployment.
```
kubectl get pods
```

To connect this application to a service, we are able to sent requests using the CLUSTER-IP and PORT of our tsla survice. To see this information use the command `kubectl get services`.

```
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.91.240.1     <none>        443/TCP   9m56s
tsla         ClusterIP   10.91.242.203   <none>        80/TCP    6m36s
```


