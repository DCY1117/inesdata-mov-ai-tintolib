"""EDC Management API client for catalog, negotiation, and transfer operations"""
import requests
from typing import Optional, Dict, List
import streamlit as st
from config import (
    CONSUMER_MANAGEMENT_API,
    PROVIDER_DSP_ENDPOINT,
    CATALOG_ENDPOINT,
    NEGOTIATION_ENDPOINT,
    TRANSFER_ENDPOINT
)


class EDCClient:
    """Client for EDC Management API operations"""
    
    def __init__(self, auth_headers: Dict[str, str]):
        """
        Initialize EDC client with authentication headers
        
        Args:
            auth_headers: Dict with Authorization header
        """
        self.auth_headers = auth_headers
        self.base_url = CONSUMER_MANAGEMENT_API
    
    def get_catalog(self) -> Optional[Dict]:
        """
        Request catalog from provider connector (INESData federated catalog)
        
        Returns:
            Catalog data or None if failed
        """
        url = f"{self.base_url}{CATALOG_ENDPOINT}"
        
        # INESData federated catalog - send null body for default QuerySpec
        try:
            response = requests.post(
                url,
                json=None,
                headers=self.auth_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                catalog_data = response.json()
                return catalog_data
            else:
                st.error(f"Catalog request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def parse_catalog_datasets(self, catalog) -> List[Dict]:
        """
        Parse catalog response and extract dataset information
        
        Args:
            catalog: Catalog response from INESData (can be list or dict)
            
        Returns:
            List of datasets with simplified structure
        """
        datasets = []
        
        if not catalog:
            return datasets
        
        # INESData returns a list of catalog items directly
        if isinstance(catalog, list):
            catalog_items = catalog
        elif isinstance(catalog, dict):
            # Fallback for standard EDC format
            catalog_items = [catalog]
        else:
            return datasets
        
        # Process each catalog item
        for catalog_item in catalog_items:
            # Extract dataset from catalog
            dataset_data = catalog_item.get('http://www.w3.org/ns/dcat#dataset', {})
            
            # Handle case where dataset is a list (process all items)
            if isinstance(dataset_data, list):
                dataset_list = dataset_data
            else:
                dataset_list = [dataset_data] if dataset_data else []
            
            # Process each dataset
            for dataset_data in dataset_list:
                if not dataset_data:
                    continue
                
                # Extract service endpoint info
                service = catalog_item.get('http://www.w3.org/ns/dcat#service', {})
                endpoint = service.get('http://www.w3.org/ns/dcat#endpointUrl', 
                                     service.get('http://www.w3.org/ns/dcat#endpointURL', 'Unknown'))
                
                # Extract policy and offer information
                has_policy = dataset_data.get('odrl:hasPolicy', {})
                offer = has_policy.get('offer', {})
                offer_id = offer.get('@id', None)
                
                # Extract distribution formats
                distributions = dataset_data.get('http://www.w3.org/ns/dcat#distribution', [])
                formats = []
                for dist in distributions:
                    if isinstance(dist, dict):
                        fmt = dist.get('http://purl.org/dc/terms/format', {})
                        if isinstance(fmt, dict):
                            format_id = fmt.get('@id', '')
                            if format_id:
                                formats.append(format_id)
                
                # Parse description (may contain HTML)
                description = dataset_data.get('http://purl.org/dc/terms/description', 
                                             dataset_data.get('shortDescription', 'No description'))
                # Remove HTML tags for preview if needed
                import re
                description_text = re.sub('<[^<]+?>', '', description) if description else 'No description'
                
                # Get byte size - may be empty string
                byte_size = dataset_data.get('http://www.w3.org/ns/dcat#byteSize', '')
                byte_size_display = byte_size if byte_size else 'Not available'
                
                # Get content type - may be empty string
                content_type = dataset_data.get('contenttype', '')
                content_type_display = content_type if content_type else 'Not available'
                
                # Extract filename from various possible fields
                filename = (dataset_data.get('filename') or 
                           dataset_data.get('http://www.w3.org/ns/dcat#fileName') or
                           dataset_data.get('edc:filename') or
                           dataset_data.get('name', '') + '.csv')
                
                parsed = {
                    'id': dataset_data.get('@id', dataset_data.get('id', 'Unknown')),
                    'name': dataset_data.get('name', dataset_data.get('@id', 'Untitled')),
                    'filename': filename,
                    'title': dataset_data.get('name', dataset_data.get('@id', 'Untitled')),
                    'shortDescription': dataset_data.get('shortDescription', description_text),
                    'description': description_text,
                    'description_html': description,
                    'version': dataset_data.get('version', 'N/A'),
                    'format': dataset_data.get('http://purl.org/dc/terms/format', 'Unknown'),
                    'contentType': content_type_display,
                    'assetType': dataset_data.get('assetType', 'Unknown'),
                    'keywords': dataset_data.get('http://www.w3.org/ns/dcat#keyword', 'N/A'),
                    'byteSize': byte_size_display,
                    'participantId': dataset_data.get('participantId', 
                                                     catalog_item.get('https://w3id.org/dspace/v0.8/participantId', 'Unknown')),
                    'endpoint': endpoint,
                    'distributionFormats': formats,
                    'offerId': offer_id,
                    'offer': offer,
                    'hasPolicy': has_policy,
                    'properties': dataset_data
                }
                datasets.append(parsed)
        
        return datasets
    
    def initiate_negotiation(self, offer_id: str, asset_id: str, provider_endpoint: str, offer: Dict) -> Optional[str]:
        """
        Initiate contract negotiation with provider
        
        Args:
            offer_id: The contract offer ID from catalog
            asset_id: The asset ID to negotiate for
            provider_endpoint: The provider's protocol endpoint
            offer: The complete offer object from catalog
            
        Returns:
            Negotiation ID or None if failed
        """
        url = f"{self.base_url}{NEGOTIATION_ENDPOINT}"
        
        # Use the exact format from INESData connector interface
        # Add full JSON-LD context including odrl namespace
        # Add required assigner and target to policy with proper JSON-LD structure
        policy_with_required_fields = {
            **offer,
            "odrl:assigner": {
                "@id": "conn-oeg-provider"
            },
            "odrl:target": {
                "@id": asset_id
            }
        }
        
        payload = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
                "edc": "https://w3id.org/edc/v0.0.1/ns/",
                "odrl": "http://www.w3.org/ns/odrl/2/"
            },
            "@type": "ContractRequest",
            "counterPartyAddress": provider_endpoint,
            "protocol": "dataspace-protocol-http",
            "policy": policy_with_required_fields
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.auth_headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                negotiation_id = result.get('@id', result.get('id'))
                st.success(f"✅ Negotiation initiated: {negotiation_id}")
                return negotiation_id
            else:
                st.error(f"❌ Negotiation failed: {response.status_code}")
                with st.expander("Error details"):
                    st.code(response.text)
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            return None
    
    def check_negotiation_status(self, negotiation_id: str) -> Optional[Dict]:
        """
        Check the status of a contract negotiation
        
        Args:
            negotiation_id: The negotiation ID
            
        Returns:
            Negotiation details or None if failed
        """
        url = f"{self.base_url}{NEGOTIATION_ENDPOINT}/{negotiation_id}"
        
        try:
            response = requests.get(
                url,
                headers=self.auth_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def initiate_transfer(self, contract_agreement_id: str, asset_id: str, provider_endpoint: str) -> Optional[str]:
        """
        Initiate data transfer process
        
        Args:
            contract_agreement_id: The agreed contract ID
            asset_id: The asset ID to transfer
            provider_endpoint: The provider's protocol endpoint
            
        Returns:
            Transfer process ID or None if failed
        """
        url = f"{self.base_url}{TRANSFER_ENDPOINT}"
        
        payload = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
                "edc": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "TransferRequest",
            "counterPartyAddress": provider_endpoint,
            "contractId": contract_agreement_id,
            "assetId": asset_id,
            "protocol": "dataspace-protocol-http",
            "transferType": "HttpData-PULL",
            "dataDestination": {
                "@type": "DataAddress",
                "type": "HttpData"
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.auth_headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return result.get('@id', result.get('id'))
            else:
                st.error(f"Transfer failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def check_transfer_status(self, transfer_id: str) -> Optional[Dict]:
        """
        Check the status of a transfer process
        
        Args:
            transfer_id: The transfer process ID
            
        Returns:
            Transfer details or None if failed
        """
        url = f"{self.base_url}{TRANSFER_ENDPOINT}/{transfer_id}"
        
        try:
            response = requests.get(
                url,
                headers=self.auth_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def get_edr(self, transfer_id: str) -> Optional[Dict]:
        """
        Get EDR (Endpoint Data Reference) for a transfer
        
        Args:
            transfer_id: The transfer process ID
            
        Returns:
            EDR data or None if failed
        """
        # Try INESData-specific endpoint first
        url = f"{self.base_url}/v3/edrs/{transfer_id}/dataaddress"
        
        try:
            response = requests.get(
                url,
                headers=self.auth_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.warning(f"EDR not available yet (status {response.status_code}). Transfer may still be in progress.")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error getting EDR: {str(e)}")
            return None
    
    def download_data(self, edr_endpoint: str, edr_auth_key: str, edr_auth_code: str, asset_id: str = None, edr_data: Dict = None) -> Optional[bytes]:
        """
        Download data using EDR (Endpoint Data Reference)
        
        Args:
            edr_endpoint: The EDR endpoint URL
            edr_auth_key: The authorization header key
            edr_auth_code: The authorization token/code
            asset_id: Optional asset ID
            edr_data: Full EDR data for debugging
            
        Returns:
            Downloaded data as bytes or None if failed
        """
        try:
            # Build headers - EDC expects raw token, not Bearer prefix
            headers = {
                edr_auth_key: edr_auth_code
            }
            
            # Use the endpoint as-is - provider should resolve asset internally
            download_url = edr_endpoint
            
            st.info(f"🔗 Downloading from: {download_url}")
            st.info(f"🔑 Auth header: {edr_auth_key}")
            
            if edr_data:
                with st.expander("🔍 Full EDR Debug"):
                    st.json(edr_data)
            
            response = requests.get(
                download_url,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                st.success(f"✅ Data downloaded successfully! ({len(response.content)} bytes)")
                return response.content
            else:
                st.error(f"❌ Download failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            return None
    
    def terminate_transfer(self, transfer_id: str, reason: str = "User requested termination") -> bool:
        """
        Terminate an active transfer process
        
        Args:
            transfer_id: The transfer process ID to terminate
            reason: Reason for termination
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}{TRANSFER_ENDPOINT}/{transfer_id}/terminate"
        
        payload = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "reason": reason
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.auth_headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                st.success(f"✅ Transfer terminated successfully")
                return True
            else:
                st.error(f"❌ Failed to terminate: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            return False
