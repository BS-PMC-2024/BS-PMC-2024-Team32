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
        Create a {difficulty} {course_name} problem with 4 multiple-choice options (A, B, C, D).
        One option should be correct. Format your response as follows:

        Problem: [Your problem statement here]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct Answer: [Letter of the correct option (A, B, C, or D)]

        Ensure that the correct answer is included in the options.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a math teacher creating {course_name} problems."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        logger.debug(f"Generated problem: {content}")
        
        lines = content.split('\n')
        problem_text = lines[0].replace('Problem: ', '').strip()
        options = [line.strip() for line in lines[1:5]]
        correct_answer = lines[5].replace('Correct Answer: ', '').strip()

        # Ensure correct_answer is just the letter
        correct_answer = correct_answer[0] if correct_answer else ''

        new_problem = AIProblems(
            problem_text=problem_text,
            options=options,
            correct_answer=correct_answer,
            topic=course_name,
            difficulty=difficulty,
            course_name=course_name
        )
        db.session.add(new_problem)
        db.session.commit()
        
        logger.debug(f"Successfully generated problem: id={new_problem.id}, text={new_problem.problem_text}, correct_answer={correct_answer}")
        return new_problem
        
    except Exception as e:
        logger.error(f"Error in generate_problem: {str(e)}")
        logger.exception("Exception details:")
        return None
    

def check_answer(problem_id, student_answer):
    problem = AIProblems.query.get(problem_id)
    if not problem:
        logger.error(f"Problem with id {problem_id} not found")
        return None, None

    try:
        prompt = f"""
        Problem: {problem.problem_text}
        Options:
        {chr(10).join(problem.options)}
        Student's answer: {student_answer}

        Evaluate the student's answer. Your response must follow this exact format:
        CORRECT: [True/False]
        EXPLANATION: [Your detailed explanation here]

        Provide a step-by-step solution, explain why the answer is correct or incorrect, and state the correct answer if the student is wrong.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a math teacher evaluating a student's answer for an algebra, geometry, or calculus problem."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        logger.debug(f"AI response: {ai_response}")

        # Extract AI's assessment and explanation
        ai_assessment_match = re.search(r'CORRECT:\s*(True|False)', ai_response, re.IGNORECASE)
        ai_explanation_match = re.search(r'EXPLANATION:\s*(.+)', ai_response, re.DOTALL)

        if not ai_assessment_match or not ai_explanation_match:
            logger.error("AI response format is incorrect")
            return None, "Error in processing the answer. Please try again."

        is_correct = ai_assessment_match.group(1).lower() == 'true'
        explanation = ai_explanation_match.group(1).strip()

        return is_correct, explanation

    except Exception as e:
        logger.error(f"Error in check_answer: {str(e)}")
        logger.exception("Exception details:")
        return None, None
    


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