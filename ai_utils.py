from openai import OpenAI
from config import Config
from app.models import AIProblems, db
import app
import traceback
import logging
import re
import json


logger = logging.getLogger(__name__)


client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_problem(course_name, difficulty):
    try:
        prompt = f"""
        Create a {difficulty} {course_name} problem. 
        Provide the following in JSON format:
        1. A problem statement
        2. Four multiple-choice options (A, B, C, D)
        Do not include the correct answer or explanation.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a math teacher creating problems for students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response content: {content}")
        
        # Remove Markdown code blocks if present
        content = re.sub(r'```json\s*|\s*```', '', content)
        
        data = json.loads(content)
        problem_text = data.get('problem_statement', '')
        
        # Handle different option formats
        options = []
        if isinstance(data.get('options'), list):
            options = data['options']
        elif isinstance(data.get('options'), dict):
            options = [f"{k}) {v}" for k, v in data['options'].items()]
        else:
            for key in ['A', 'B', 'C', 'D']:
                if key in data or f'option_{key}' in data:
                    value = data.get(key) or data.get(f'option_{key}')
                    options.append(f"{key}) {value}")
        
        if not options:
            raise ValueError("No options provided in the AI response")
        
        new_problem = AIProblems(
            problem_text=problem_text,
            options=options,
            topic=course_name,
            difficulty=difficulty,
            course_name=course_name,
            correct_answer="Not checked yet"  # Placeholder value
        )
        db.session.add(new_problem)
        db.session.commit()
        
        logger.debug(f"Successfully generated problem: id={new_problem.id}, text={new_problem.problem_text}, options={options}")
        return new_problem
        
    except Exception as e:
        logger.error(f"Error in generate_problem: {str(e)}")
        logger.exception("Exception details:")
        return None

def check_answer(problem_id, student_answer):
    problem = AIProblems.query.get(problem_id)
    if not problem:
        logger.error(f"Problem with id {problem_id} not found")
        return None, None, None

    try:
        # Get the full text of the student's answer
        student_answer_full = next((opt for opt in problem.options if opt.startswith(student_answer)), student_answer)

        prompt = f"""
        Problem: {problem.problem_text}
        Options: {', '.join(problem.options)}
        Student's answer: {student_answer_full}

        Provide your response in JSON format with the following keys:
        1. is_correct: 'Correct' or 'Incorrect'
        2. correct_answer: The full correct answer (e.g., 'A) x = 4')
        3. explanation: Explanation of the solution process
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a math teacher evaluating a student's answer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response content: {content}")
        
        # Remove Markdown code blocks if present
        content = re.sub(r'```json\s*|\s*```', '', content)
        
        data = json.loads(content)
        is_correct = data.get('is_correct', '').lower() == 'correct'
        correct_answer = data.get('correct_answer', '')
        explanation = data.get('explanation', '')

        # Update the problem with the correct answer
        correct_letter = correct_answer.split(')')[0].strip()
        problem.correct_answer = correct_letter
        db.session.commit()

        return is_correct, correct_answer, explanation

    except Exception as e:
        logger.error(f"Error in check_answer: {str(e)}")
        logger.exception("Exception details:")
        return None, None, None


def provide_feedback(problem, student_answer):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful math teacher providing feedback."},
                {"role": "user", "content": f"Problem: {problem}\nStudent answer: {student_answer}\nProvide detailed feedback."}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        app.logger.error(f"Error providing feedback: {str(e)}")
        if "insufficient_quota" in str(e):
            return "API quota exceeded. Please try again later or contact support."
        return "An error occurred while providing feedback. Please try again."

def ai_tutor_response(course, question):
    try:
        logger.info(f"Sending request to OpenAI API for course: {course}, question: {question}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an AI tutor specializing in {course}. Provide helpful, concise answers to student questions."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.7
        )
        logger.info(f"Received response from OpenAI API: {response}")
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content.strip()
        else:
            logger.warning("No valid response received from OpenAI API")
            return "Failed to generate a response. Please try again."
    except Exception as e:
        logger.error(f"Error in ai_tutor_response: {str(e)}")
        logger.error(traceback.format_exc())
        if "insufficient_quota" in str(e):
            return "API quota exceeded. Please try again later or contact support."
        return f"An error occurred: {str(e)}"