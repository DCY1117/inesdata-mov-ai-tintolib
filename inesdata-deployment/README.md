This repository contains the code for the automated deployment of elements of the INESData platform.

It is based in Kubernetes and Helm charts.

THe deployment of a working platform is divided in 3 different steps:

- Deploying the common services (POstgres Database, Minio Object Storage, Keycloak Identity Provider), which will be common
to all the platform, and will be shared by all the different deployments.
- Deploying a dataspace, which in its core is nothing more than a set of configurations for the platform and common services, 
and a public website. This deployment will be launched for every dataspace desired in the platform. 
- Deploying a connector, which is the main element that an organization will use to connect their data to the dataspace.
A complete connector is composed by the main backend service and a frontend SPA web interface.

## Requirements

- A Kubernetes cluster.
- kubectl and helm installed locally. 

## Deploying a dataspace

The dataspace wil deployed using the Helm chart in the `dataspace` folder.
Steps:
- Creating a new namespace for the dataspace.
- Create a Keycloak Realm for the dataspace.
- Deploy the public web portal.

Follow the steps provided in the file deployment-guide.txt

## Deploying a connector

The connector will be deployed using the Helm chart in the `connector` folder.

Follow the steps provided in the file deployment-guide.txt


## Disclaimer

Este trabajo ha recibido financiación del proyecto INESData (Infraestructura para la INvestigación de ESpacios de DAtos distribuidos en UPM), un proyecto financiado en el contexto de la convocatoria UNICO I+D CLOUD del Ministerio para la Transformación Digital y de la Función Pública en el marco del PRTR financiado por Unión Europea (NextGenerationEU)