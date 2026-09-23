from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2") 

import chromadb
client = chromadb.Client()
collection = client.get_or_create_collection(name="Nexora_documents")

# open file path 
def open_files(file_path):
    with open(file_path) as f:
        contents = f.read()
    return contents

# chunking 
def chunks_list(contents):
    chunks = contents.split("\n\n")
    return chunks

# embedding 
def embed_list(chunks):
    vectors = model.encode(chunks)
    return vectors

# adding embedding to collection 
def adding_list(chunks, vectors, role_tier, department, ids):
    collection.add(
        documents = chunks,
        embeddings = vectors.tolist(),
        metadatas = [{"role_tier":role_tier, "department":department}] * len(chunks),
        ids=ids        
    )

# calling all functions in one 
def all_functions(file_path, role_tier, department, ids):
    contents = open_files(file_path)
    chunks = chunks_list(contents)
    vectors = embed_list(chunks)
    adding_list(chunks, vectors, role_tier, department, ids)
