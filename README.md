# 🌱 CropDiseaseAI

> **Autonomous Multilingual Crop Disease Diagnostics & Curated Agronomic Advisory Engine**  
> Built as an enterprise microservice for the [AgriConnect](https://github.com/guru2005-z) ecosystem.

---

## 🚀 Key Capabilities

- **Deep Learning Vision Classification (6 Crops)**:
  - 🌾 **Paddy / Rice**: Leaf Blast, Brown Spot, Tungro, Healthy
  - 🌽 **Maize / Corn**: Northern Leaf Blight, Common Rust, Gray Leaf Spot, Healthy
  - 🥜 **Groundnut / Peanut**: Early Leaf Spot (Tikka), Late Leaf Spot, Rust, Healthy
  - 🌶️ **Chilli / Pepper**: Anthracnose / Fruit Rot, Leaf Curl Virus, Yellow Mosaic, Healthy
  - 🍌 **Banana / Plantain**: Black Sigatoka, Cordana Leaf Spot, Panama Wilt, Healthy
  - 🌾 **Wheat / Cereal**: Brown Leaf Rust, Yellow Stripe Rust, Septoria Leaf Blight, Healthy

- **Certified ICAR & ANGRAU Grounded RAG (`AgriBot`)**:
  - Pinecone Serverless Vector Database (`cropdisease-rag`, 384 dimensions)
  - Ultra-low latency Groq LPU synthesis (`openai/gpt-oss-120b`)
  - Grounded in certified university Package of Practices (ANGRAU, ICAR-IIRR, CIMMYT, IRRI, PPQS)

- **Native Multilingual Translation**:
  - 100% dynamic UI and LLM response translation across 5 languages:
    - 🇬🇧 English
    - 🇮🇳 తెలుగు (Telugu)
    - 🇮🇳 हिन्दी (Hindi)
    - 🇮🇳 தமிழ் (Tamil)
    - 🇮🇳 ಕನ್ನಡ (Kannada)

---

## 🛠️ Tech Stack & Microservice Architecture

- **Web Framework**: FastAPI (Asynchronous Python 3.11+)
- **ML / Neural Networks**: TensorFlow 2.15+ (MobileNetV2, CNN Transfer Learning)
- **Vector Database**: Pinecone Serverless (`llama-text-embed-v2`, cosine metric)
- **Reasoning LLM**: Groq LPU Inference Engine (`openai/gpt-oss-120b`)
- **Deployment**: Docker container on Render / AWS EC2

---

## 📦 Local Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/guru2005-z/CropDiseaseAI.git
cd CropDiseaseAI

# 2. Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (.env)
cp .env.example .env
# Edit .env with your GROQ_API_KEY and PINECONE_API_KEY

# 5. Run server
python run_server.py
```

- **Interactive Web App**: [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌐 Docker & Cloud Deployment (Render)

```bash
# Build Docker image
docker build -t cropdisease-ai .

# Run container locally
docker run -p 8000:8000 --env-file .env cropdisease-ai
```

### Deploying to Render
1. Connect your GitHub repository to [Render](https://dashboard.render.com).
2. Select **Runtime: Docker**.
3. Set environment variables:
   - `GROQ_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME=cropdisease-rag`
   - `PINECONE_NAMESPACE=agricultural-rag`
4. Render deploys your service with free automatic SSL: `https://cropdisease-ai.onrender.com`.

---

## 🔗 AgriConnect Integration

In your **AgriConnect** frontend or backend `.env`, set:
```env
CROP_DISEASE_AI_URL=https://cropdisease-ai.onrender.com
```

When a farmer scans an affected crop leaf in AgriConnect, the platform calls `POST /predict/{crop_name}` and immediately gives the option to **hire nearby spray workers** to apply the recommended treatment.
