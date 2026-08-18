from src.graph.retriever import GraphRetriever, format_evidence_package


if __name__ == "__main__":
    retriever = GraphRetriever()
    evidence_package = retriever.get_evidence_package("Horizon Growth Fund")
    print(format_evidence_package(evidence_package))