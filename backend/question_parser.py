import re
from pdf_loader import extract_pdf_text
from collections import defaultdict
import random

def extract_questions_with_sections():
    raw_text = extract_pdf_text()
    lines = raw_text.strip().split('\n')

    data = defaultdict(lambda: defaultdict(list))  # {section: {subsection: [questions]}}
    current_section = ""
    current_subsection = ""
    current_question = ""
    current_options = {}
    current_answer_key = ""

    for line in lines:
        line = line.strip()

        # Detect section
        if line.startswith("# Section:"):
            current_section = line.replace("# Section:", "").strip()
            continue

        # Detect sub-section
        if line.startswith("##Sub-section"):
            current_subsection = re.sub(r'^##Sub-section\s*[:\-]?\s*', '', line).strip()
            continue

        # Detect question line like "1. What is ..."
        match_q = re.match(r'^\d+\.\s+(.*)', line)
        if match_q:
            if current_question and current_options and current_section and current_subsection:
                question_obj = {
                    'question': f"Q{len(data[current_section][current_subsection]) + 1}: {current_question}",
                    'options': current_options,
                    'answer': f"{current_answer_key}) {current_options.get(current_answer_key, '')}"
                }
                data[current_section][current_subsection].append(question_obj)

            current_question = match_q.group(1).strip()
            current_options = {}
            current_answer_key = ""
            continue

        # Detect options like "✅ b) Some answer" or "a) Some answer"
        match_opt = re.match(r'^(✅\s*)?([a-d])\)\s+(.*)', line)
        if match_opt:
            key = match_opt.group(2)
            text = match_opt.group(3).strip()
            current_options[key] = text
            if match_opt.group(1):  # if ✅ is present
                current_answer_key = key
            continue

        # Detect explicit answer line like "Answer: b"
        match_ans = re.match(r'^Answer:\s*([a-d])$', line)
        if match_ans:
            current_answer_key = match_ans.group(1)
            continue

    # Save the final question
    if current_question and current_options and current_section and current_subsection:
        question_obj = {
            'question': f"Q{len(data[current_section][current_subsection]) + 1}: {current_question}",
            'options': current_options,
            'answer': f"{current_answer_key}) {current_options.get(current_answer_key, '')}"
        }
        data[current_section][current_subsection].append(question_obj)

    return data

def extract_sampled_questions():
    full_data = extract_questions_with_sections()
    sampled_data = {}

    for section, subsects in full_data.items():
        sampled_data[section] = {}
        for sub, questions in subsects.items():
            sampled_data[section][sub] = random.sample(questions, min(24, len(questions)))
    
    return sampled_data

# Test the parser
if __name__ == "__main__":
    sections = extract_questions_with_sections()
    for section, subsects in sections.items():
        print(f"\n=== Section: {section} ===")
        for sub, qs in subsects.items():
            print(f"\n--- Sub-section: {sub} ---")
            for q in qs:
                print(q['question'])
                for k, v in q['options'].items():
                    print(f"  {k}) {v}")
                print("✅ Answer:", q['answer'])
                print("-" * 50)
