# INESData Dataspace Browser

A Streamlit application to browse catalogs, negotiate contracts, and download data from INESData dataspaces automatically.

## Features

- 🔐 **Keycloak Authentication**: Login with consumer connector credentials
- 📚 **Catalog Browser**: View available datasets from provider
- 🤝 **Auto Negotiation**: Automatically negotiate contracts (coming soon)
- 📥 **Data Download**: Pull data from provider (coming soon)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure** (edit `config.py` if needed):
   - Keycloak URL: `http://keycloak.dev.ed.inesdata.upm`
   - Consumer connector: `http://conn-oeg-consumer.dev.ds.inesdata.upm`
   - Provider connector: `http://conn-oeg-provider.dev.ds.inesdata.upm`

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Default Credentials

**Consumer (from credentials JSON):**
- Username: `user-conn-oeg-consumer`
- Password: `vCV!otahBte*!c@9`

**Provider (from credentials JSON):**
- Username: `user-conn-oeg-provider`
- Password: `nZEUI2_PXddY3i3@`

## Usage Flow

1. **Login** with consumer credentials
2. **Browse** the provider's catalog
3. **Select** a dataset
4. **Click** "Request Data" to start automatic negotiation
5. **Download** the data once transfer completes

## Architecture

```
app.py              # Main Streamlit UI
├── auth.py         # Keycloak authentication
├── edc_client.py   # EDC Management API client
└── config.py       # Configuration (URLs, endpoints)
```

## Next Steps

- [ ] Implement contract negotiation flow
- [ ] Add transfer process monitoring
- [ ] Implement data download with EDR tokens
- [ ] Add progress indicators for async operations
- [ ] Support multiple providers

## Requirements

- Python 3.10+
- Access to INESData connectors (Minikube with minikube tunnel running)
- Keycloak realm configured
