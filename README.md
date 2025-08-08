
# Chatbot Graph RAG

This project implements a Chatbot using a combination of GraphRAG, Hybrid Search, and standard RAG with Vector Search. The application is built with FastAPI and utilizes Neo4j for graph-based data storage and FAISS for vector search.

## Features

- **Hybrid Search:** Combines semantic search with graph-based search to provide more accurate and contextually relevant answers.
- **GraphRAG:** Leverages a knowledge graph to answer questions by traversing relationships between entities.
- **RAG with Vector Search:** A standard Retrieval-Augmented Generation implementation using a vector store for semantic search.
- **File Upload:** Allows uploading markdown files to populate the knowledge graph and vector store.
- **API Endpoints:** Provides a set of API endpoints to interact with the chatbot and manage data.

## Project Structure
- **`app/main.py`**: The main FastAPI application file, defining the API endpoints.
- **`app/crud/`**: Contains the core logic for the different search and retrieval methods.
  - **`HybridSearch.py`**: Implements the hybrid search functionality.
  - **`GraphRAG.py`**: Implements the GraphRAG functionality.
  - **`RAG_VectorSearch.py`**: Implements the RAG with vector search functionality.
- **`app/pkgs/`**: Contains helper modules and utilities.
  - **`model.py`**: A wrapper for the Gemma3n model API.
  - **`Neo4jManager.py`**: Manages the connection to the Neo4j database.
- **`app/faiss_index/`**: Stores the FAISS index for vector search.
- **`app/upload_data.py`**: Contains the logic for processing uploaded files.

## Getting Started

### Prerequisites

- Python 3.10+
- Docker
- Neo4j Database

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://your-repository-url.com/Chatbot_Graph_RAG.git
   cd Chatbot_Graph_RAG
   ```

2. **Install the required packages:**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Set up the environment variables:**
   - Create a `.env` file in the `app` directory.
   - Add the following variables to the `.env` file:
     ```
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USERNAME=neo4j
     NEO4J_PASSWORD=your-neo4j-password
     GEMMA3N_API_KEY=your-gemma3n-api-key
     ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- **`GET /`**: Returns a welcome message.
- **`POST /hybrid/ask`**: Ask a question using the hybrid search method.
- **`POST /graph_rag/ask`**: Ask a question using the GraphRAG method.
- **`POST /rag/ask`**: Ask a question using the RAG with vector search method.
- **`POST /graphrag_vector/upload`**: Upload a markdown file to populate the knowledge graph and vector store.
- **`POST /vector/upload`**: Upload a file to populate the vector store only.
- **`GET /upload_history`**: Get the history of uploaded files.
- **`POST /extract-triples`**: Extract triples from a given text.

## Usage

1. **Start the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Upload a markdown file:**
   - Use a tool like `curl` or Postman to send a `POST` request to the `/graphrag_vector/upload` endpoint with a markdown file.

3. **Ask a question:**
   - Send a `POST` request to one of the `ask` endpoints (`/hybrid/ask`, `/graph_rag/ask`, or `/rag/ask`) with a query.
