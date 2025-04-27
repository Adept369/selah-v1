import os
from pinecone import Pinecone, ServerlessSpec

class CaseLawScholarAgent:
    def __init__(self):
        # Load credentials from environment
        api_key = os.getenv("PINECONE_API_KEY")
        env     = os.getenv("PINECONE_ENVIRONMENT")  # e.g. "us-west1-gcp"

        # Instantiate the Pinecone client
        self.pc = Pinecone(api_key=api_key, environment=env)

        # Ensure our index exists (create as serverless if needed)
        self.index_name = "case-law"
        self.dimension  = 1536
        self.metric     = "cosine"

        resp = self.pc.list_indexes()
        # v2 SDK: resp.names is a callable method
        if hasattr(resp, "names") and callable(resp.names):
            names_list = resp.names()       # ← invoke the method
        elif hasattr(resp, "names"):
            names_list = resp.names        # unlikely, but safe
        else:
            names_list = resp              # if it’s already a list[str]

        existing = set(names_list)

        if self.index_name not in existing:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec()
            )

        # Bind to the index for queries/upserts
        self.index = self.pc.Index(self.index_name)

    def run(self, query: str) -> str:
        # MVP: hardcoded response
        if "sovereignty" in query.lower():
            return (
                "Sovereignty is the supreme authority within a territory. "
                "Refer to Worcester v. Georgia, 31 U.S. (6 Pet.) 515 (1832)."
            )
        return f"CaseLawScholar received your query: '{query}'"