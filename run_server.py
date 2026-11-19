"""Run CropDiseaseAI FastAPI server locally or in cloud container."""

import os
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    is_prod = os.getenv("RENDER", "") or os.getenv("ENVIRONMENT", "").lower() == "production"

    print("=" * 70)
    print(f"Starting CropDiseaseAI API on http://{host}:{port}")
    print(f"  - Interactive Web App: http://{host}:{port}/ui")
    print(f"  - Interactive API Docs: http://{host}:{port}/docs")
    print(f"  - Pinecone + Groq RAG: http://{host}:{port}/rag/query")
    print("=" * 70)

    uvicorn.run("api.main:app", host=host, port=port, reload=not is_prod)
