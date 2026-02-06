#Ingest profile documents into ChromaDB.

"""
How to use:
  1. Create a .env file with `OPENAI_API_KEY=your_key_here`
  2. Install dependencies: `pip install -r backend/requirements.txt`.
  3. Run: python scripts/ingest_data.py --slides`  # Profile docs + Google Slides

This script will:
  - Read all `*.md` files in `backend/data/profile/` + slides from Viven AI Google Drive folder
  - Create ChromaDB 
  - Use OpenAI embeddings to embed each document and store them
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

#Add backend to path to import integrations
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set. Check .env file")
    raise SystemExit(1)

#Set up ChromaDB
import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_DIR = BASE_DIR / "backend" / "data" / "profile"
CHROMA_DIR = BASE_DIR / "chroma_db"

#Read from backend/data/profile/*.md 
def read_profile_files(directory: Path):
    files = sorted(directory.glob("*.md"))
    documents = []
    metadatas = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        documents.append(text)
        metadatas.append({"source": f.name}) #Store filename as metadata for retrieval (e.g., "resume.md") (turned off for now)
    return documents, metadatas


def main():
    print(f"Profile dir: {PROFILE_DIR}")
    documents, metadatas = read_profile_files(PROFILE_DIR)
    if not documents:
        print("No markdown files found. Add resume.md etc. and retry.") #Error handling
        return

    #OpenAI embedding function
    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    #Create/Get collection and attach embedding function
    collection = client.get_or_create_collection(name="profile", embedding_function=embedding_fn)

    #Generate ids
    ids = [f"doc_{i}" for i in range(len(documents))]

    #Add documents (embeddings applied)
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Indexed {len(documents)} documents into Chroma at {CHROMA_DIR}")


def ingest_slides(collection):
    """
    Gets all presentations from Viven AI Google Drive folder and adds them to ChromaDB
    """

    from integrations.google_slides import get_all_slides_content, is_authenticated

    #Auth Check
    if not is_authenticated():
        print("\nERROR: Not authenticated with Google!")
        print("Please run the backend and go to http://localhost:8000/auth/login first.")
        return 0

    #Fetch presentations
    print("\nFetching presentations from Viven AI folder...")
    all_presentations = get_all_slides_content()

    if not all_presentations:
        print("No presentations found.")
        return 0

    #Convert slides to documents
    documents = []
    metadatas = []
    ids = []

    for presentation in all_presentations:
        pres_title = presentation.get("title")
        source_name = presentation.get("source_name", pres_title)

        print(f"\nProcessing: {source_name}")

        for slide in presentation.get("slides", []):
            slide_num = slide.get("slide_number", 0)
            slide_title = slide.get("title", "")
            slide_body = slide.get("body", "")

            #Combine content
            content_parts = []
            if slide_title:
                content_parts.append(f"Slide Title: {slide_title}")
            if slide_body:
                content_parts.append(f"Content: {slide_body}")

            #Handle empty slides
            if not content_parts:
                print(f"  - Slide {slide_num}: (empty, skipping)")
                continue

            #Build document text and give context
            document_text = f"From '{source_name}', Slide {slide_num}:\n" + "\n".join(content_parts)

            #Create unique ID from ChromaDB
            safe_name = source_name.lower().replace(" ", "-").replace("'", "")
            doc_id = f"slides_{safe_name}_slide_{slide_num}"

            documents.append(document_text)
            metadatas.append({
                "source": f"{source_name} (Slide {slide_num})",
                "type": "slides",
                "presentation": source_name,
                "slide_number": slide_num,
            })
            ids.append(doc_id)

    #if empty
    if not documents:
        print("No content found")
        return 0

    #Remove old slides (prevent duplicates on rerun)
    print("\nRemoving old slides data (if any)...")
    try:
        existing = collection.get(where={"type": "slides"})
        old_ids = existing.get("ids", [])
        if old_ids:
            print(f"  Removing {len(old_ids)} old slide documents...")
            collection.delete(ids=old_ids)
    except Exception:
        pass  #No old slides

    #Add to ChromaDB
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return len(documents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ingest profile docs and optionally Google Slides")
    parser.add_argument(
        "--slides",
        action="store_true",
        help="Also ingest Google Slides from your Viven AI folder"
    )
    args = parser.parse_args()

    #Main ingestion
    main()

    #Slides
    if args.slides:
        # Re-create the collection connection for slides
        embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_or_create_collection(name="profile", embedding_function=embedding_fn)

        slides_count = ingest_slides(collection)
        print(f"\nIngested {slides_count} slide documents from Google Drive.")