"""Basic usage example for GRASS RAG Pipeline."""

from grass_rag import GrassRAG

def main():
    # Initialize pipeline
    rag = GrassRAG()
    
    # Ask questions
    questions = [
        "How do I import shapefile?",
        "How do I buffer vectors?",
        "How do I calculate slope?"
    ]
    
    for question in questions:
        answer, results, metrics = rag.query(question)
        print(f"Q: {question}")
        print(f"A: {answer}")
        print(f"Time: {metrics['total_latency']:.3f}s\n")

if __name__ == "__main__":
    main()