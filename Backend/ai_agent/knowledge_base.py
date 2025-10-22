import os
import pandas as pd
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index.embeddings import HuggingFaceEmbedding
from langchain_community.llms import GooglePalm
from langchain_google_genai import ChatGoogleGenerativeAI
from django.conf import settings
import chromadb

class KnowledgeBase:
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self.policies_csv = settings.COMPANY_POLICIES_CSV
        self.flights_csv = settings.FLIGHT_DATA_CSV
        self.index = None
        self.vector_store = None
        self._setup_knowledge_base()
    
    def _setup_knowledge_base(self):
        """Setup LlamaIndex with company policies and flight data"""
        try:
            # Initialize embedding model
            embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
            
            # Initialize LLM (Gemini via Google Palm)
            llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1
            )
            
            service_context = ServiceContext.from_defaults(
                llm=llm,
                embed_model=embed_model
            )
            
            # Create documents from CSV files
            documents = self._load_csv_documents()
            
            if documents:
                # Create vector store index
                self.index = VectorStoreIndex.from_documents(
                    documents, 
                    service_context=service_context
                )
                
        except Exception as e:
            print(f"Error setting up knowledge base: {e}")
    
    def _load_csv_documents(self):
        """Load documents from CSV files"""
        documents = []
        
        try:
            # Load company policies
            if os.path.exists(self.policies_csv):
                policies_df = pd.read_csv(self.policies_csv)
                for _, row in policies_df.iterrows():
                    doc_text = f"""
                    Policy Category: {row.get('category', 'General')}
                    Policy Title: {row.get('title', 'No Title')}
                    Policy Details: {row.get('details', 'No details available')}
                    Effective Date: {row.get('effective_date', 'Not specified')}
                    Applicable To: {row.get('applicable_to', 'All customers')}
                    """
                    documents.append(doc_text)
            
            # Load flight data
            if os.path.exists(self.flights_csv):
                flights_df = pd.read_csv(self.flights_csv)
                for _, row in flights_df.iterrows():
                    doc_text = f"""
                    Flight Information:
                    Airline: {row.get('airline', 'Unknown')}
                    Route: {row.get('departure_city', 'Unknown')} to {row.get('arrival_city', 'Unknown')}
                    Aircraft: {row.get('aircraft_type', 'Not specified')}
                    Amenities: {row.get('amenities', 'Standard')}
                    Baggage Policy: {row.get('baggage_policy', 'Standard baggage allowance')}
                    Check-in Requirements: {row.get('check_in', 'Standard check-in')}
                    """
                    documents.append(doc_text)
                    
        except Exception as e:
            print(f"Error loading CSV documents: {e}")
        
        return documents
    
    def query_knowledge_base(self, query):
        """Query the knowledge base for relevant information"""
        if not self.index:
            return "Knowledge base not available. Please contact support for policy information."
        
        try:
            query_engine = self.index.as_query_engine()
            response = query_engine.query(query)
            return str(response)
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"
    
    def get_company_policies(self, category=None):
        """Get company policies by category"""
        try:
            if os.path.exists(self.policies_csv):
                policies_df = pd.read_csv(self.policies_csv)
                if category:
                    policies_df = policies_df[policies_df['category'] == category]
                return policies_df.to_dict('records')
            return []
        except Exception as e:
            print(f"Error getting company policies: {e}")
            return []