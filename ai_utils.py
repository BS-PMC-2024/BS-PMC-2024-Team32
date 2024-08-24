from openai import OpenAI
from config import Config
from app.models import AIProblems,db,StudentAttempts
import app
import traceback
import logging
import re
import json
from flask import session

logger = logging.getLogger(__name__)


client = OpenAI(api_key=Config.OPENAI_API_KEY)


def generate_math_problem(course_name, difficulty):
    prompt = f"""
    Create a {difficulty} {course_name} problem with 4 multiple-choice options.
    Format your response exactly as follows:

    PROBLEM: [Problem statement]
    A: [Option A]
    B: [Option B]
    C: [Option C]
    D: [Option D]
    CORRECT: [Letter of the correct option (A, B, C, or D)]

    Ensure that:
    1. The options are distinct and complete answers.
    2. Only one option is correct.
    3. The problem is appropriate for {course_name} at {difficulty} level.
    4. You clearly indicate which answer is correct using the CORRECT: field.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a math teacher creating {course_name} problems."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        logger.debug(f"Generated problem: {content}")
        
        # Parse the response
        lines = content.split('\n')
        problem_text = lines[0].replace('PROBLEM:', '').strip()
        options = [line.strip()[3:] for line in lines[1:5]]  # Remove A:, B:, etc.
        correct_answer = lines[5].replace('CORRECT:', '').strip()

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
        logger.error(f"Error in generate_math_problem: {str(e)}")
        logger.exception("Exception details:")
        return None

def evaluate_student_answer(problem_id, student_answer):
    problem = AIProblems.query.get(problem_id)
    if not problem:
        logger.error(f"Problem with id {problem_id} not found")
        return None, "Error: Problem not found"

    is_correct = student_answer.upper() == problem.correct_answer.upper()

    explanation_prompt = f"""
    Problem: {problem.problem_text}
    Options:
    A: {problem.options[0]}
    B: {problem.options[1]}
    C: {problem.options[2]}
    D: {problem.options[3]}
    Correct Answer: {problem.correct_answer}
    Student's Answer: {student_answer}

    Please provide a detailed explanation of why the answer is {"correct" if is_correct else "incorrect"}.
    Include the correct solution process.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a math teacher providing explanations for problem solutions."},
                {"role": "user", "content": explanation_prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        explanation = response.choices[0].message.content.strip()
        
        # Save the student's attempt
        user_id = session.get('user_id')
        if user_id:
            student_attempt = StudentAttempts(
                student_id=user_id,
                problem_id=problem_id,
                student_answer=student_answer,
                is_correct=is_correct
            )
            db.session.add(student_attempt)
            db.session.commit()

        return is_correct, explanation

    except Exception as e:
        logger.error(f"Error in evaluate_student_answer: {str(e)}")
        logger.exception("Exception details:")
        return None, f"Error evaluating answer: {str(e)}"
    

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