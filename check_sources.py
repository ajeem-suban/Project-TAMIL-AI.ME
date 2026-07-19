import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("tamil_corpus")

data = collection.get()

sources = sorted(set(
    m.get("source", "")
    for m in data["metadatas"]
))

print("Total Sources:", len(sources))
print()

for s in sources:
    print(s)