# This chart deploys a new connector in the INESData platform.
#
connector:
  name: {{ keys.connector_name }}
  dataspace: {{ keys.dataspace_name }}
  environment: {{ 'pro' if keys.environment == 'PRO' else 'dev' }}
  image:
    name: ghcr.io/inesdata/inesdata-connector
    tag: 0.9.1
  replicas: 1
  jvmArgs: "{% if keys.environment == 'PRO'%}-Djavax.net.ssl.trustStore=/opt/connector/tls-cacerts/cacerts.jks -Djavax.net.ssl.trustStorePassword=inesdata{% endif %}"
  configuration:
    configFilePath: /opt/connector/config/connector-configuration.properties
  ingress:
    hostname: {{ keys.connector_name }}-{{ keys.dataspace_name }}.{% if keys.environment == 'PRO'%}ds.inesdata-project.eu{% else %}dev.ds.inesdata.upm{% endif %}
    protocol: {{ 'https' if keys.environment == 'PRO' else 'http' }}
  minio:
    accesskey: {{ keys.dataspace_name }}/{{ keys.connector_name }}/aws-access-key
    secretkey: {{ keys.dataspace_name }}/{{ keys.connector_name }}/aws-secret-key
  oauth2:
    allowedRole1: connector-admin
    allowedRole2: connector-management
    allowedRole3: connector-user
    client: {{ keys.connector_name }}
    privatekey: {{ keys.dataspace_name }}/{{ keys.connector_name }}/private-key
    publickey: {{ keys.dataspace_name }}/{{ keys.connector_name }}/public-key
    type: code
  transfer:
    privatekey: {{ keys.dataspace_name }}/{{ keys.connector_name }}/private-key
    publickey: {{ keys.dataspace_name }}/{{ keys.connector_name }}/public-key

connectorInterface:
  image:
    name: ghcr.io/inesdata/inesdata-connector-interface
    tag: 0.10.0
  oauth2:
    client:
      dataspace-users
    type:
      code
    scope:
      openid profile email

services:
  db:
    # comsrv prefix comes from the Helm release of the common services
    hostname: {{ keys.database_hostname }}
    # credentials for the new Connector DB. `user` will also be used to create the DB
    # and therefore must comply with SQL identifiers restrictions
    name: {{ keys.database.name }}
    user: {{ keys.database.user }}
    password: {{ keys.database.passwd }}
  keycloak:
    # comsrv prefix comes from the Helm release of the common services
    hostname: {{ keys.keycloak_internal_hostname }}
    external: {{ keys.keycloak_hostname }}
    protocol: {{ 'https' if keys.environment == 'PRO' else 'http' }}
  minio:
    # comsrv prefix comes from the Helm release of the common services
    hostname: {{ keys.minio_hostname }}
    bucket: {{ keys.dataspace_name }}-{{ keys.connector_name }}
    protocol: {{ 'https' if keys.environment == 'PRO' else 'http' }}
  registrationService:
    hostname: {% if keys.environment == 'PRO' %}registration-service-{{ keys.dataspace_name }}.ds.inesdata-project.eu{% 
                                         else %}{{ keys.dataspace_name }}-registration-service:8080{% endif %}
    protocol: {{ 'https' if keys.environment == 'PRO' else 'http' }}
  vault:
    url: {{ keys.vault_url }}
    token: {{ keys.vault.token }}
    path: {{ keys.dataspace_name }}/{{ keys.connector_name }}/
