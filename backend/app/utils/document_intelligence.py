from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.core.config import settings

class DocumentIntelligenceService:
    """Service for Azure Document Intelligence operations"""
    
    def __init__(self):
        """Initialize the Document Intelligence service"""
        self.endpoint = settings.azure_document_intelligence_endpoint
        self.key = settings.azure_document_intelligence_key
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint, 
            credential=AzureKeyCredential(self.key)
        )
    
    def analyze_document(self, document_content):
        """Analyze a document using Azure Document Intelligence
        
        Args:
            document_content: The content of the document to analyze
            
        Returns:
            The extracted text from the document
        """
        # Analyze the document using the Layout model
        poller = self.client.begin_analyze_document(
            "prebuilt-layout", document_content
        )
        result = poller.result()
        
        # Extract text from the document
        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
        
        return extracted_text

# Create a singleton instance
document_intelligence_service = DocumentIntelligenceService() 