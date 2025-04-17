from flask import Flask, render_template, request, jsonify
import pickle
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from groq import Groq
import random
import boto3
import io
import os

app = Flask(__name__)

# Optional: load from environment variables for security
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = "chatbothtk"
OBJECT_KEY = "Vectorstore/Hoonartek_Index.pkl"

# Groq API Key (you can also move this to an env variable)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Greeting responses
greeting_responses = [
    "How may I assist you today?",
    "What would you like to know about Hoonartek?",
    "Feel free to ask anything about our services or projects.",
]

# Load FAISS index from S3
def load_faiss_from_s3():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        file_stream = io.BytesIO()
        s3.download_fileobj(BUCKET_NAME, OBJECT_KEY, file_stream)
        file_stream.seek(0)
        vectordb = pickle.load(file_stream)
        return vectordb
    except Exception as e:
        print(f"❌ Error loading FAISS index from S3: {e}")
        return None

vectordb = load_faiss_from_s3()

def get_answer_from_website(question):
    try:
        # Basic greeting detection
        if any(word in question.lower() for word in ["hello", "hi", "hey", "morning", "evening", "howdy"]):
            return random.choice(greeting_responses)

        # Search for context in vector store
        docs = vectordb.similarity_search(question, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"""
Answer the following question based ONLY on the context below.
If the answer is not found in the context, say "Sorry, I couldn't find that on the website."

Context:
{context}

Question: {question}
Answer:
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")
    answer = get_answer_from_website(user_message)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)

 