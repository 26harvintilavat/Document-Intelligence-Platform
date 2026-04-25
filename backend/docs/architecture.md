# Architecture Notes

## Project Purpose

The Document Intelligence Platform allows users to upload PDFs and ask questions from those documents.

## Core RAG Flow

1. Upload PDF
2. Extract text
3. Split text into chunks
4. Create embeddings
5. Store embeddings in vector database
6. User asks question
7. Retrieve relevant chunks
8. Generate answer using LLM
9. Return answer with source references

## Backend Structure

```text
backend/app/main.py
```
