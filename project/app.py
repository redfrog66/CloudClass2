import openai
from flask import Flask, request, render_template, jsonify
import os
import docx  # For reading .docx files

# Load API key from a text file
with open('apikey.txt', 'r') as file:
    openai.api_key = file.read().strip()

# Initialize Flask app
app = Flask(__name__)

# Function to extract text from .docx file
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to upload the document
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Handle .docx files and extract text
    if file.filename.endswith('.docx'):
        content = extract_text_from_docx(file_path)
        print("Extracted .docx content:", content)  # Debugging step
    else:
        # For other file formats, e.g., .txt
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

    # Debugging output
    print(f"Uploaded content length: {len(content)}")  # Check content length
    return jsonify({"message": "File uploaded successfully", "content": content})

# Route to ask questions based on document content
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    content = data.get('content')
    question = data.get('question')

    try:
        # Generate a response using the ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond in the same language as the question."},
                {"role": "user", "content": f"Based on the following document:\n\n{content}\n\nAnswer the question: {question}"}
            ],
            max_tokens=150
        )

        # Extract the answer from the response
        if response and response.choices and len(response.choices) > 0:
            answer = response.choices[0].message['content'].strip()
            return jsonify({"answer": answer})
        else:
            return jsonify({"error": "No answer found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.mkdir('uploads')
    app.run(debug=True)
