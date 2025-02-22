import os
import random
from openai import OpenAI, AsyncOpenAI
from typing import List, Tuple, Dict, Deque
from collections import deque
from dotenv import load_dotenv
from src.models.question import Question
from src.utils.token_counter import TokenCounter
import uuid
import logging
import json
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please check your .env file.")

client = OpenAI(api_key=api_key)
async_client = AsyncOpenAI(api_key=api_key)

class QuestionGenerator:
    def __init__(self):
        self.categories = [
            "Science", "History", "Geography", "Entertainment",
            "Sports", "Technology", "Arts", "Literature"
        ]
        self.categories_hebrew = {
            "Science": "מדע",
            "History": "היסטוריה",
            "Geography": "גאוגרפיה",
            "Entertainment": "בידור",
            "Sports": "ספורט",
            "Technology": "טכנולוגיה",
            "Arts": "אמנות",
            "Literature": "ספרות"
        }
        self.asked_questions_file = "asked_questions.json"
        self.load_asked_questions()
        self.question_queue = deque(maxlen=10)  # Increased queue size to 10
        self.explanation_queue = deque(maxlen=10)  # Matching explanation queue
        self.token_counter = TokenCounter.get_instance()
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.language = os.getenv("GAME_LANGUAGE", "English")
        self.support_hebrew = os.getenv("SUPPORT_HEBREW", "true").lower() == "true"
        self.validate_api_key()
        self.prefetch_lock = asyncio.Lock()  # Lock to prevent concurrent pre-fetching
        self.background_task = None  # Track the background pre-fetching task
        self.min_queue_size = 5  # Minimum questions before triggering more pre-fetching
        self._is_shutting_down = False  # Flag to indicate shutdown
        
    async def cleanup(self):
        """Cleanup resources before shutdown"""
        self._is_shutting_down = True
        if self.background_task and not self.background_task.done():
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
        self.question_queue.clear()
        self.explanation_queue.clear()
    
    def load_asked_questions(self):
        """Load previously asked questions from file"""
        try:
            if os.path.exists(self.asked_questions_file):
                with open(self.asked_questions_file, 'r') as f:
                    self.asked_questions = json.load(f)
            else:
                self.asked_questions = []
        except Exception as e:
            logger.error(f"Error loading asked questions: {e}")
            self.asked_questions = []
    
    def save_asked_questions(self, question: Dict):
        """Save a new question to the asked questions file"""
        try:
            question_data = {
                "text": question["text"],
                "correct_answer": question["correct_answer"],
                "category": question["category"],
                "asked_at": datetime.now().isoformat()
            }
            self.asked_questions.append(question_data)
            with open(self.asked_questions_file, 'w') as f:
                json.dump(self.asked_questions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving asked question: {e}")
    
    def validate_api_key(self):
        """Validate the OpenAI API key by making a test request"""
        try:
            logger.info("Validating OpenAI API key...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            logger.info("API key validation successful!")
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            raise ValueError(f"Invalid OpenAI API key: {str(e)}")
    
    def update_model(self, model_name: str):
        """Update the OpenAI model being used"""
        self.model = model_name
        logger.info(f"Updated OpenAI model to: {model_name}")
        # Cancel existing background task
        if self.background_task and not self.background_task.done():
            self.background_task.cancel()
        self.background_task = None
        # Clear pre-fetched questions
        self.question_queue.clear()
        self.explanation_queue.clear()
    
    def start_background_prefetch(self, difficulty: int):
        """Start the background pre-fetching task"""
        if self.background_task is None or self.background_task.done():
            self.background_task = asyncio.create_task(self.continuous_prefetch(difficulty))
            logger.info("Started background pre-fetching task")
    
    async def continuous_prefetch(self, difficulty: int):
        """Continuously pre-fetch questions in the background"""
        try:
            while True:
                current_size = len(self.question_queue)
                if current_size < self.question_queue.maxlen:
                    try:
                        question, explanation = await self.generate_question(difficulty)
                        async with self.prefetch_lock:
                            self.question_queue.append(question)
                            self.explanation_queue.append(explanation)
                            logger.info(f"Successfully pre-fetched question. Queue size: {len(self.question_queue)}/{self.question_queue.maxlen}")
                    except Exception as e:
                        logger.error(f"Error generating question in background: {e}")
                        await asyncio.sleep(2)  # Wait before retrying
                    # Adaptive delay based on queue size
                    delay = 5 if current_size > self.min_queue_size else 1
                    await asyncio.sleep(delay)
                else:
                    # Queue is full, longer wait
                    await asyncio.sleep(10)
        except asyncio.CancelledError:
            logger.info("Background pre-fetching task cancelled")
        except Exception as e:
            logger.error(f"Background pre-fetching error: {e}")
            # Don't auto-restart, let get_next_question handle it
    
    async def get_next_question(self, difficulty: int) -> Tuple[Question, str]:
        """Get the next question, using pre-fetched if available"""
        try:
            # Start or restart background task if needed
            if self.background_task is None or self.background_task.done():
                self.start_background_prefetch(difficulty)
            
            if self.question_queue and self.explanation_queue:
                async with self.prefetch_lock:
                    question = self.question_queue.popleft()
                    explanation = self.explanation_queue.popleft()
                logger.info(f"Using pre-fetched question. Remaining in queue: {len(self.question_queue)}/{self.question_queue.maxlen}")
                return question, explanation
            else:
                # If queue is empty, generate one now
                logger.info("Queue empty, generating question now")
                question, explanation = await self.generate_question(difficulty)
                # Ensure background task is running for future questions
                self.start_background_prefetch(difficulty)
                return question, explanation
        except Exception as e:
            logger.error(f"Error getting next question: {e}")
            raise RuntimeError(f"Error getting next question: {e}")
    
    def update_language(self, language: str, support_hebrew: bool):
        """Update language settings"""
        self.language = language
        self.support_hebrew = support_hebrew
        # Clear pre-fetched questions to ensure they're in the correct language
        self.question_queue.clear()
        self.explanation_queue.clear()
        logger.info(f"Updated language settings - Language: {language}, Hebrew Support: {support_hebrew}")
    
    def get_category_name(self, category: str) -> str:
        """Get category name in current language"""
        if self.language == "Hebrew" and self.support_hebrew:
            return self.categories_hebrew.get(category, category)
        return category
    
    async def generate_question(self, difficulty: int, category: str = None) -> Tuple[Question, str]:
        try:
            difficulty_desc = "basic" if difficulty <= 3 else \
                            "intermediate" if difficulty <= 7 else "advanced"
            
            category = category or random.choice(self.categories)
            logger.info(f"Generating {difficulty_desc} question about {category} using {self.model}")
            
            # Format previously asked questions for the prompt
            asked_questions_text = "\n".join([
                f"- {q['text']} (Answer: {q['correct_answer']})"
                for q in self.asked_questions[-10:]  # Last 10 questions
            ])
            
            # Determine language for the prompt
            language_instruction = ""
            if self.language == "Hebrew" and self.support_hebrew:
                language_instruction = "Generate the question, answers, and explanation in Hebrew. Use correct Hebrew grammar and punctuation."
            else:
                language_instruction = "Generate the question in English."
            
            max_attempts = 3
            for attempt in range(max_attempts):
                prompt = f"""{language_instruction}
                Generate a trivia question following these rules:
                1. Topic: {category}
                2. Difficulty: {difficulty_desc}
                3. Format your response EXACTLY like this example:
                   What is the capital of France?|Paris|London|Berlin|Madrid|Paris is the capital of France since 1792. It's the largest city in France and one of the most visited cities in the world.
                4. Make sure to include:
                   - A clear question
                   - The correct answer
                   - 3 plausible but incorrect answers
                   - A brief, interesting explanation
                5. Separate each part with the | character
                6. Do not use any of these recently asked questions:
                {asked_questions_text}
                7. Do not include any other text or formatting"""
                
                response = await async_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise trivia question generator. Follow the format exactly."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                # Track tokens
                self.token_counter.add_tokens(
                    len(prompt.split()),  # Approximate token count for sent
                    response.usage.completion_tokens  # Exact token count for received
                )
                
                content = response.choices[0].message.content.strip()
                parts = [part.strip() for part in content.split("|")]
                
                if len(parts) != 6:
                    logger.warning(f"Invalid format in attempt {attempt + 1}")
                    continue
                
                question_text, correct_answer, *wrong_answers_and_explanation = parts
                wrong_answers = wrong_answers_and_explanation[:3]
                explanation = wrong_answers_and_explanation[3]
                
                if not all([question_text, correct_answer] + wrong_answers + [explanation]):
                    logger.warning(f"Empty field in attempt {attempt + 1}")
                    continue
                
                # Check if this question was asked before
                if any(q["text"] == question_text for q in self.asked_questions):
                    if attempt == max_attempts - 1:
                        raise ValueError("Unable to generate unique question after max attempts")
                    continue
                
                # Save the question to asked questions
                self.save_asked_questions({
                    "text": question_text,
                    "correct_answer": correct_answer,
                    "category": category
                })
                
                options = wrong_answers + [correct_answer]
                random.shuffle(options)
                
                logger.info("Question generated successfully")
                return Question(
                    id=str(uuid.uuid4()),
                    text=question_text.strip(),
                    correct_answer=correct_answer.strip(),
                    options=[opt.strip() for opt in options],
                    category=self.get_category_name(category),
                    difficulty=difficulty,
                    points=difficulty * 10
                ), explanation.strip()
            
            raise ValueError("Failed to generate unique question after max attempts")
            
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            raise RuntimeError(f"Error generating question: {str(e)}")
    
    async def get_additional_info(self, question: str, answer: str) -> str:
        """Get additional interesting information about the answer"""
        try:
            # Determine language for the prompt
            language_instruction = ""
            if self.language == "Hebrew" and self.support_hebrew:
                language_instruction = "Provide the response in Hebrew, using correct grammar and punctuation."
            else:
                language_instruction = "Provide the response in English."
            
            prompt = f"""{language_instruction}
            Given this trivia question: "{question}" with answer "{answer}",
            provide 2-3 fascinating facts that make this knowledge more interesting.
            Focus on surprising connections and lesser-known details.
            Keep it brief but engaging."""
            
            response = await async_client.chat.completions.create(
                model=self.model,  # Use the same model for consistency
                messages=[
                    {"role": "system", "content": "You are a knowledgeable educator who makes learning fascinating."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # Track tokens
            self.token_counter.add_tokens(
                len(prompt.split()),  # Approximate token count for sent
                response.usage.completion_tokens  # Exact token count for received
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error getting additional info: {str(e)}")
            return "Unable to fetch additional information at this time." 