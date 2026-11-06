import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
col = client.get_collection("tamil_corpus")
for src in ["agananooru", "madhuraikanji", "pathirruppattu", "pathupattu-pattinapalai", "pathupattu-mullaipattu"]:
    res = col.get(where={"source": src})
    print(src, "->", len(res["ids"]))