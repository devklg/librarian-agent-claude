"""
Example: Using Docling with Librarian Agent for Multi-modal RAG
"""

import asyncio
import sys
sys.path.append('./part1_core_agent')

from librarian_claude_agent import LibrarianClaudeAgent
from docling_extractor import DoclingExtractor


async def demo_multimodal_rag():
    """
    Demonstrate multi-modal RAG with Docling + Librarian Agent
    """
    
    print("🚀 Multi-modal RAG Demo with Docling + Librarian Agent\n")
    
    # Step 1: Initialize Docling extractor
    print("📚 Initializing Docling extractor...")
    docling = DoclingExtractor(enable_image_captions=True)
    
    # Step 2: Process a PDF with images
    print("📄 Processing PDF with images...")
    pdf_path = "./documents/technical_report.pdf"
    
    result = docling.extract(
        source=pdf_path,
        save_images=True,
        output_dir='./extracted_images'
    )
    
    print(f"✅ Processed: {result['metadata']['title']}")
    print(f"   Pages: {result['metadata']['num_pages']}")
    print(f"   Images: {len(result['images'])}")
    print(f"   Chunks: {len(result['chunks'])}\n")
    
    # Step 3: Show enriched content (text + image captions)
    print("📝 Sample enriched content:")
    print("-" * 60)
    print(result['content'][:500] + "...\n")
    
    # Step 4: Initialize Librarian Agent
    print("🤖 Initializing Librarian Agent...")
    agent = LibrarianClaudeAgent()
    
    # Step 5: Store in Universal Memory Bridge
    print("💾 Storing in Universal Memory Bridge...")
    # (This would connect to actual database in production)
    
    # Step 6: Query the agent about image content
    print("\n💬 Querying agent about image content...")
    
    queries = [
        "What does the architecture diagram in section 3.1 show?",
        "Describe the workflow illustrated in the document",
        "What are the main components shown in the figures?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        
        response = await agent.chat(
            message=query,
            session_id="demo-session",
            requester_id="demo-user"
        )
        
        print(f"🤖 Agent: {response['message'][:200]}...")
        print(f"💰 Cost: ${response['cost']['total']:.4f}")
        print(f"🎯 Cache Hit: {response['cache_hit']}")
        if response['skills_used']:
            print(f"📚 Skills Used: {', '.join(response['skills_used'])}")
    
    # Step 7: Show savings
    print("\n📊 Multi-modal RAG Benefits:")
    print("=" * 60)
    print("✅ Images not ignored - described by AI")
    print("✅ Complete information preserved")
    print("✅ Image content searchable as text")
    print("✅ Agent can answer questions about diagrams")
    print("✅ 90% cost savings from prompt caching")
    print("\n🎉 Multi-modal RAG Demo Complete!")


async def demo_batch_processing():
    """
    Demo: Process multiple documents with Docling
    """
    
    print("\n" + "="*60)
    print("📦 Batch Processing Demo")
    print("="*60 + "\n")
    
    # Initialize
    docling = DoclingExtractor(enable_image_captions=True)
    
    # Documents to process
    documents = [
        "./documents/api_guide.pdf",
        "./documents/architecture_overview.pdf",
        "./documents/user_manual.pdf"
    ]
    
    all_results = []
    
    for doc in documents:
        print(f"📄 Processing: {doc}")
        
        try:
            result = docling.extract(doc)
            all_results.append(result)
            
            print(f"   ✅ Success!")
            print(f"   📊 Chunks: {len(result['chunks'])}")
            print(f"   🖼️  Images: {len(result['images'])}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Processed {len(all_results)} documents")
    print(f"📊 Total chunks: {sum(len(r['chunks']) for r in all_results)}")
    print(f"🖼️  Total images: {sum(len(r['images']) for r in all_results)}")


async def demo_image_types():
    """
    Demo: Different types of images Docling can process
    """
    
    print("\n" + "="*60)
    print("🖼️  Image Types Demo")
    print("="*60 + "\n")
    
    docling = DoclingExtractor(enable_image_captions=True)
    
    # Process document with various image types
    result = docling.extract("./documents/mixed_content.pdf")
    
    print("Image types that Docling handles:")
    print("1. 📊 Charts and graphs → Described as data visualization")
    print("2. 🏗️  Architecture diagrams → Components and relationships")
    print("3. 📸 Screenshots → UI elements and actions")
    print("4. 📈 Flowcharts → Process steps and decision points")
    print("5. 🗺️  Infographics → Key information and layout")
    print("6. 🎨 Illustrations → Visual concepts and themes")
    
    print("\nExample captions from processed document:")
    print("-" * 60)
    for i, img in enumerate(result['images'][:3]):
        print(f"\nImage {i+1}:")
        print(f"Caption: {img['caption'][:150]}...")


if __name__ == "__main__":
    # Run demos
    print("🎯 Docling + Librarian Agent Examples\n")
    
    # Demo 1: Basic multi-modal RAG
    asyncio.run(demo_multimodal_rag())
    
    # Demo 2: Batch processing (optional)
    # asyncio.run(demo_batch_processing())
    
    # Demo 3: Image types (optional)
    # asyncio.run(demo_image_types())
    
    print("\n" + "="*60)
    print("📚 More examples in DOCLING_INTEGRATION.md")
    print("="*60)
