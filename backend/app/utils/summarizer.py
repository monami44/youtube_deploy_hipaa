import openai
from app.core.config import settings
import os
from openai import AzureOpenAI

class DocumentSummarizer:
    """Service for summarizing document content using OpenAI"""
    
    def __init__(self):
        """Initialize the OpenAI client"""
        # Check if we have Azure OpenAI credentials
        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_version=settings.azure_openai_api_version
                )
                self.deployment = settings.azure_openai_deployment
                print(f"Successfully initialized Azure OpenAI client with deployment: {self.deployment}")
            except Exception as e:
                print(f"Error initializing Azure OpenAI client: {e}")
                self.client = None
                self.deployment = None
        else:
            # Fallback if no Azure config
            self.client = None
            self.deployment = None
            print("No Azure OpenAI credentials found - summaries will be mocked")
    
    def generate_summary(self, document_text, custom_prompt=None):
        """Generate a summary for the document
        
        Args:
            document_text: The text content of the document
            custom_prompt: Optional custom prompt to guide the summary
            
        Returns:
            The generated summary
        """
        # Create a system prompt that follows HIPAA guidelines
        system_prompt = """
        You are a HIPAA-compliant document summarization assistant. 
        Provide a concise summary of the document focusing on:
        1. Key information and important points
        2. Main topics and sections
        3. Any action items or recommendations
        
        Maintain medical privacy and confidentiality standards in your summary.
        """
        
        # Use custom prompt if provided
        if custom_prompt:
            user_prompt = f"{custom_prompt}\n\nDocument text:\n{document_text[:8000]}"
        else:
            user_prompt = f"Summarize this document:\n\n{document_text[:8000]}"
        
        # If no client is available, return a mock summary for local development
        if not self.client or not self.deployment:
            return "This is a mock summary for local development. Azure OpenAI API credentials are required for actual summaries."
            
        # Generate the summary
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

# Create a singleton instance
document_summarizer = DocumentSummarizer() 