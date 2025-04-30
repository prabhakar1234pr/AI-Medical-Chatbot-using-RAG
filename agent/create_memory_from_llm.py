from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Step 1: Load PDFs
data_path = "data/"
def load_pdf(file_path):
    loader = DirectoryLoader(file_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

documents = load_pdf(data_path)
print('length of documents:', len(documents))

# Step 2: Split into chunks
def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_documents(documents)

chunks = split_documents(documents)
print('length of chunks:', len(chunks))

# Step 3: Load embedding model
def generate_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embedding_model = generate_embeddings()

# Step 4: Store chunks in FAISS
DB_FAISS_PATH = 'db/faiss_index'
db = FAISS.from_documents(chunks, embedding_model)
db.save_local(DB_FAISS_PATH)

