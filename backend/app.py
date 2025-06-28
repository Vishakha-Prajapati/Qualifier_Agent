from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
from pdf_loader import extract_pdf_text
from question_parser import extract_questions_with_sections, extract_sampled_questions
from datetime import datetime
import os

# Load environment
load_dotenv()

# Initialize Flask
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates'))
app = Flask(__name__, template_folder=TEMPLATE_DIR)

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client['mentorship']
user_collection = db['user']
assessment_collection = db['assessments']

# Routes
@app.route('/')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def handle_register_form():
    email = request.form.get('email')

    if user_collection.find_one({'email': email}):
        return render_template('register.html', error="Email already registered. Please log in or use a different email.")

    data = {
        'full_name': request.form.get('full_name'),
        'email': email,
        'university': request.form.get('university'),
        'country': request.form.get('country'),
        'degree': request.form.get('degree'),
        'graduation_year': request.form.get('graduation_year'),
        'technical_skills': request.form.get('technical_skills'),
        'experience_summary': request.form.get('experience_summary')
    }

    user_collection.insert_one(data)
    return render_template('welcome.html', name=data['full_name'])

@app.route('/welcome')
def welcome_page():
    return render_template('welcome.html')

@app.route('/rules')
def rules_page():
    return render_template('rules.html')

@app.route('/assessment')
def assessment_page():
    return render_template('assessment.html')

@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/load-questions')
def load_questions():
    content = extract_pdf_text()
    return f"<pre>{content}</pre>"

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions_by_section = extract_sampled_questions()
    return jsonify(questions_by_section)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    user_collection.insert_one(data)
    return jsonify({'message': 'Registered successfully'}), 200

@app.route('/api/submit-answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    user_answers = data.get('answers', [])
    user_email = data.get('email')

    total_questions = len(user_answers)
    correct_count = 0
    submitted = []

    for item in user_answers:
        q_text = item.get('question')
        selected = item.get('selected_option')
        correct = item.get('correct_option')
        is_correct = selected == correct[:1]

        submitted.append({
            'question': q_text,
            'selected_option': selected,
            'correct_option': correct,
            'is_correct': is_correct
        })

        if is_correct:
            correct_count += 1

    result = {
        'email': user_email,
        'answers': submitted,
        'total_questions': total_questions,
        'correct_answers': correct_count,
        'result': 'Pass' if correct_count >= 17 else 'Fail',
        'timestamp': datetime.utcnow()
    }

    assessment_collection.insert_one(result)

    return jsonify({
        'message': f"You {'passed' if correct_count >= 17 else 'failed'} the test.",
        'score': correct_count,
        'result': result['result']
    })

# Run App
if __name__ == '__main__':
    app.run(debug=True)
