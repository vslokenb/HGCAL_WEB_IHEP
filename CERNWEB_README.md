# **CERN Web Deployment Guide for HGCAL IHEP MAC**

This guide provides instructions on deploying and managing the **HGCAL IHEP MAC** system on **CERN's PAAS (Platform-as-a-Service) infrastructure**, utilizing **OKD (OpenShift Kubernetes Distribution)** for containerized deployment.

---

## **1. Building & Pushing the Docker Image**

Before deploying the application, build and push the Docker image to **Docker Hub**.

### **1.1 Log in to Docker Hub**
Authenticate with **Podman** to push images to **Docker Hub**:
\```
podman login docker.io
\```
Enter your **Docker Hub** credentials when prompted.

### **1.2 Build the Image**
Navigate to the directory containing the **Dockerfile** and build the new image:
\```
docker build -t ziruiality/hgcal_web_ihep:latest .
\```

### **1.3 Push the Image to Docker Hub**
After building the image, push it to **Docker Hub**:
\```
docker push ziruiality/hgcal_web_ihep:latest
\```
Once the image is pushed, it is accessible at:  
[Docker Hub Repository](https://hub.docker.com/repository/docker/ziruiality/hgcal_web_ihep/general)**  

---

## **2. Deploying on CERN PAAS (OKD/OpenShift)**

CERN provides an easy-to-use web interface for deploying Docker images via **OKD (OpenShift Kubernetes Distribution)**.

### **2.1 Deploy Image via OKD Web Interface**
Go to **CERN PAAS OpenShift Web Console**:  
[OKD Deployment Portal](https://paas.cern.ch/deploy-image/ns/hgcal-ihep-website)**  

1. Select **"Deploy Image"**.
2. Choose **Docker Image** and enter:
   \```
   docker.io/ziruiality/hgcal_web_ihep:latest
   \```
3. Click **Deploy** to start the process.

---

## **3. Configuring Storage (PVC) & Environment Variables**

Persistent storage (PVC) is required for saving files or logs, to keep the updated information in user information and output files.

### **3.1 Create a Persistent Volume Claim (PVC)**
In **OKD**, create a PVC for data storage:
1. Navigate to **Storage** → **Persistent Volume Claims**.
2. Click **Create PVC**, set the required storage size, and select the appropriate access mode.

### **3.2 Configure Deployment Environment**
After deploying the image:
1. Navigate to **Workloads** → **Deployments** → **Environment**.
2. Add **environment variables** and adjust **volume mounts** if needed.

---

## **4. Updating the Deployed Image**

If a new version of the application is built and pushed to Docker Hub, update the deployment with the latest image.

### **4.1 Update Image via Web Interface**
1. Go to **Workloads** → **Deployments**.
2. Select **hgcal-ihep-website**.
3. Click **Edit Deployment** and update the image to the latest tag:
   \```
   docker.io/ziruiality/hgcal_web_ihep:latest
   \```
4. Click **Save** and restart the deployment.

### **4.2 Update Image via CLI**
Alternatively, update the image using **oc CLI**:
\```
oc set image deployment/hgcal hgcal-web=ziruiality/hgcal_web_ihep:v2
\```
Then restart the pod:
\```
oc rollout restart deployment/hgcal
\```

---

## **5. OKD Command-Line Operations**

To manage the deployment via the command line, use the **oc CLI**.

### **5.1 Log in to OKD**
\```
oc sso-login --server https://api.paas.okd.cern.ch
\```
Follow the authentication steps to access **CERN OpenShift**.

### **5.2 Check Running Pods**
\```
oc get pods
\```

### **5.3 Enter a Running Pod**
To access a container inside a pod:
\```
oc exec -it hgcal-644cd9894b-cvdzm -- /bin/bash
\```

### **5.4 Copy Files to a Pod**
To transfer files (e.g., `user_info.csv`) to a pod:
\```
oc cp user_info.csv hgcal-644cd9894b-cvdzm:/tmp/
\```

---

## **6. Verifying Deployment & Debugging**

### **6.1 Check Logs of a Pod**
To troubleshoot, view logs using:
\```
oc logs -f hgcal-644cd9894b-cvdzm
\```

### **6.2 Restart a Pod**
To manually restart a pod if needed:
\```
oc delete pod hgcal-644cd9894b-cvdzm
\```
A new pod should automatically start based on the deployment settings.

---

## **7. Accessing the CERN-Hosted Web Application**

Once successfully deployed, access the application at:  
**[HGCAL IHEP MAC CERN Webpage](https://hgcal-hgcal-ihep-website.app.cern.ch/)**  

