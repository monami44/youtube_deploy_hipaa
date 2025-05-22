import os
from pydantic import BaseModel, Field, computed_field
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    
    # Database
    database_url: str = Field(
        default=os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/docprocessor")
    )
    
    # Azure Storage
    azure_storage_account_name: str = Field(
        default=os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    )
    azure_storage_account_key: str = Field(
        default=os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")
    )
    azure_storage_container_name: str = Field(
        default=os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    )
    
    @computed_field
    def azure_storage_connection_string(self) -> str:
        """Create connection string from account name and key"""
        # First check if a full connection string is provided
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        if conn_str:
            return conn_str
            
        # Otherwise build it from components
        if self.azure_storage_account_name and self.azure_storage_account_key:
            return f"DefaultEndpointsProtocol=https;AccountName={self.azure_storage_account_name};AccountKey={self.azure_storage_account_key};EndpointSuffix=core.windows.net"
        return ""
    
    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str = Field(
        default=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    )
    azure_document_intelligence_key: str = Field(
        default=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
    )
    
    # OpenAI
    azure_openai_api_key: str = Field(
        default=os.getenv("AZURE_OPENAI_API_KEY", "")
    )
    azure_openai_endpoint_full: str = Field(
        default=os.getenv("AZURE_OPENAI_ENDPOINT", "")
    )
    
    @computed_field
    def azure_openai_endpoint(self) -> str:
        """Extract base endpoint from full endpoint"""
        endpoint = self.azure_openai_endpoint_full
        # Extract the base URL (up to .com/)
        match = re.search(r'(https://.*?\.com/)', endpoint)
        if match:
            return match.group(1)
        return endpoint
    
    @computed_field
    def azure_openai_deployment(self) -> str:
        """Extract deployment name from endpoint"""
        endpoint = self.azure_openai_endpoint_full
        match = re.search(r'deployments/([^/]+)', endpoint)
        if match:
            return match.group(1)
        return "gpt-4.1"  # Default deployment name
    
    @computed_field
    def azure_openai_api_version(self) -> str:
        """Extract API version from endpoint"""
        endpoint = self.azure_openai_endpoint_full
        match = re.search(r'api-version=([^&]+)', endpoint)
        if match:
            return match.group(1)
        return "2023-05-15"  # Default API version
    
    # App settings
    poll_interval_seconds: int = Field(
        default=int(os.getenv("POLL_INTERVAL_SECONDS", "15"))
    )

# Create global settings object
settings = Settings() 