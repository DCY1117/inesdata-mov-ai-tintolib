# Configuration for INESData connectors and Keycloak
import os

# Keycloak configuration
KEYCLOAK_URL = "http://keycloak.dev.ed.inesdata.upm"
KEYCLOAK_REALM = "demo"
KEYCLOAK_CLIENT_ID = "dataspace-users"

# Consumer connector configuration
CONSUMER_CONNECTOR_URL = "http://conn-oeg-consumer.dev.ds.inesdata.upm"
CONSUMER_MANAGEMENT_API = f"{CONSUMER_CONNECTOR_URL}/management"

# Provider connector configuration
PROVIDER_CONNECTOR_URL = "http://conn-oeg-provider.dev.ds.inesdata.upm"
PROVIDER_DSP_ENDPOINT = f"{PROVIDER_CONNECTOR_URL}/protocol"

# API endpoints (INESData custom paths)
CATALOG_ENDPOINT = "/federatedcatalog/request"
NEGOTIATION_ENDPOINT = "/v3/contractnegotiations"
TRANSFER_ENDPOINT = "/v3/transferprocesses"
ASSET_ENDPOINT = "/v3/assets"
