"""Authentication module for Keycloak token management"""
import requests
from typing import Optional, Dict
import streamlit as st
from config import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID


class KeycloakAuth:
    """Handle Keycloak authentication and token management"""
    
    def __init__(self):
        self.token_endpoint = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    def get_token(self, username: str, password: str) -> Optional[Dict]:
        """
        Get access token from Keycloak using username/password
        
        Args:
            username: Keycloak username
            password: Keycloak password
            
        Returns:
            Dict with access_token, refresh_token, expires_in, etc. or None if failed
        """
        try:
            payload = {
                'grant_type': 'password',
                'client_id': KEYCLOAK_CLIENT_ID,
                'username': username,
                'password': password,
                'scope': 'openid profile email'
            }
            
            response = requests.post(
                self.token_endpoint,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Authentication failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict with new access_token or None if failed
        """
        try:
            payload = {
                'grant_type': 'refresh_token',
                'client_id': KEYCLOAK_CLIENT_ID,
                'refresh_token': refresh_token
            }
            
            response = requests.post(
                self.token_endpoint,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def get_auth_headers(self, access_token: str) -> Dict[str, str]:
        """
        Get authorization headers for API requests
        
        Args:
            access_token: The access token
            
        Returns:
            Dict with Authorization header
        """
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
