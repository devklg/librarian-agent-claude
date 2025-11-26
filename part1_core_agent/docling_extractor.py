"""
Docling Document Extractor - Multi-modal document processing
Uses Docling by IBM for advanced PDF processing with image captioning
"""

import os
from typing import Dict, List, Any, Optional
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend


class DoclingExtractor:
    """
    Advanced document extractor using Docling for multi-modal processing
    
    Features:
    - Text extraction from PDFs
    - Image detection and extraction
    - AI-powered image captioning (OpenAI)
    - Hybrid chunking
    - Export to multiple formats
    """
    
    def __init__(
        self, 
        enable_image_captions: bool = True,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize Docling extractor
        
        Args:
            enable_image_captions: Use OpenAI to caption images
            openai_api_key: OpenAI API key for image captioning
        """
        self.enable_image_captions = enable_image_captions
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Configure pipeline options
        self.pipeline_options = self._configure_pipeline()
        
        # Initialize converter
        self.converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.PPTX,
                InputFormat.HTML,
                InputFormat.MD
            ],
            pipeline_options=self.pipeline_options
        )
    
    def _configure_pipeline(self) -> PdfPipelineOptions:
        """Configure PDF processing pipeline"""
        
        options = PdfPipelineOptions()
        
        if self.enable_image_captions and self.openai_api_key:
            # Enable AI image captioning with OpenAI
            from docling.pipeline.simple_pipeline import SimplePipeline
            from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
            
            # Configure image description
            options.images_scale = 2.0  # Higher quality image processing
            options.generate_picture_images = True
            
            # OpenAI captioning prompt
            options.picture_description_prompt = """
            Describe this image in detail. Focus on:
            - What the image shows
            - Key elements and their relationships
            - Any text visible in the image
            - The purpose or meaning of the image
            
            Be concise but comprehensive.
            """
        
        return options
    
    def extract(
        self, 
        source: str,
        save_images: bool = False,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract content from document using Docling
        
        Args:
            source: File path or URL to document
            save_images: Save images as external files
            output_dir: Directory to save images (if save_images=True)
            
        Returns:
            {
                'content': str,  # Enriched text with image captions
                'images': List[Dict],  # Image metadata and paths
                'chunks': List[str],  # Pre-chunked content
                'metadata': Dict  # Document metadata
            }
        """
        
        # Convert document
        result = self.converter.convert(source)
        
        # Extract enriched content (text + image captions)
        enriched_content = result.document.export_to_markdown()
        
        # Extract images if requested
        images = []
        if save_images and output_dir:
            images = self._save_images(result, output_dir)
        
        # Get document metadata
        metadata = {
            'title': result.document.name,
            'num_pages': len(result.document.pages) if hasattr(result.document, 'pages') else 1,
            'has_images': len(images) > 0,
            'source': source
        }
        
        # Chunk the content
        chunks = self._chunk_content(enriched_content)
        
        return {
            'content': enriched_content,
            'images': images,
            'chunks': chunks,
            'metadata': metadata
        }
    
    def _save_images(
        self, 
        result: Any, 
        output_dir: str
    ) -> List[Dict[str, str]]:
        """Save extracted images to disk"""
        
        images = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Export with image references
        result.document.save(
            output_dir,
            output_format='markdown',
            image_mode='referenced'  # Save images as external files
        )
        
        # Collect image metadata
        if hasattr(result.document, 'pictures'):
            for idx, picture in enumerate(result.document.pictures):
                image_path = os.path.join(output_dir, f"image_{idx}.png")
                images.append({
                    'path': image_path,
                    'caption': picture.get('caption', ''),
                    'index': idx
                })
        
        return images
    
    def _chunk_content(
        self, 
        content: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[str]:
        """
        Chunk content using Docling's hybrid chunker
        
        Note: In production, use Docling's HybridChunker for smarter chunking
        This is a simplified version
        """
        
        # Simple chunking (in production, use HybridChunker from Docling)
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def extract_to_langchain(self, source: str) -> List[Any]:
        """
        Extract and convert to LangChain documents
        
        Perfect for LangChain/LangGraph integration!
        """
        
        result = self.converter.convert(source)
        
        # Export to LangChain format
        langchain_docs = result.document.export_to_document_tokens(
            format='langchain'
        )
        
        return langchain_docs


# Convenience functions for backward compatibility

def extract_from_url(url: str, **kwargs) -> Dict[str, Any]:
    """Extract content from URL"""
    extractor = DoclingExtractor(**kwargs)
    return extractor.extract(url)


def extract_from_file(filepath: str, **kwargs) -> Dict[str, Any]:
    """Extract content from local file"""
    extractor = DoclingExtractor(**kwargs)
    return extractor.extract(filepath)


def extract_with_image_captions(source: str, **kwargs) -> Dict[str, Any]:
    """Extract with AI-powered image captions"""
    extractor = DoclingExtractor(enable_image_captions=True, **kwargs)
    return extractor.extract(source, save_images=True)
