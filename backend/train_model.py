import pandas as pd
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# load dataset
data = pd.read_csv("data/mercury_tax_full_chatbot_dataset.csv")

questions = data["question"].tolist()
answers = data["answer"].tolist()

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(questions)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

pickle.dump((index, answers), open("model/chatbot_model.pkl", "wb"))

print("Model trained successfully")