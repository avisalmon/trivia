from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QProgressBar,
    QSpacerItem, QSizePolicy, QFrame, QDialog,
    QSpinBox, QFormLayout, QComboBox, QStatusBar, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from qasync import asyncSlot, asyncClose
from src.ui.achievements_dialog import AchievementsDialog
from src.ui.help_dialog import HelpDialog
from src.ui.analog_clock import AnalogClock
from src.utils.token_counter import TokenCounter
from src.utils.sound_generator import ensure_sound_files
import asyncio
import logging
import functools
import random
import os
from dotenv import load_dotenv, set_key

# Configure logging
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Settings")
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        # Timer duration setting
        self.timer_duration = QSpinBox()
        self.timer_duration.setRange(5, 60)
        self.timer_duration.setValue(int(os.getenv("DEFAULT_TIMER_DURATION", 20)))
        self.timer_duration.setSuffix(" seconds")
        layout.addRow("Time per question:", self.timer_duration)
        
        # Timer style setting
        self.timer_style = QComboBox()
        self.timer_style.addItems(["Digital", "Analog"])
        current_style = os.getenv("TIMER_STYLE", "Digital")
        self.timer_style.setCurrentText(current_style)
        layout.addRow("Timer style:", self.timer_style)
        
        # Language settings
        self.language_selector = QComboBox()
        self.language_selector.addItems(["English", "Hebrew"])
        current_language = os.getenv("GAME_LANGUAGE", "English")
        self.language_selector.setCurrentText(current_language)
        layout.addRow("Game Language:", self.language_selector)
        
        # Hebrew support toggle
        self.hebrew_support = QCheckBox()
        self.hebrew_support.setChecked(os.getenv("SUPPORT_HEBREW", "true").lower() == "true")
        layout.addRow("Enable Hebrew Support:", self.hebrew_support)
        
        # Model selection
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ])
        current_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.model_selector.setCurrentText(current_model)
        layout.addRow("AI Model:", self.model_selector)
        
        # Model info label
        self.model_info = QLabel("GPT-3.5 is faster but GPT-4 gives better questions")
        self.model_info.setStyleSheet("color: #666; font-style: italic;")
        self.model_info.setWordWrap(True)
        layout.addRow("", self.model_info)
        
        # Apply button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_settings)
        layout.addRow("", apply_button)
        
        # Save and close button
        save_button = QPushButton("Save and Close")
        save_button.clicked.connect(self.save_settings)
        layout.addRow("", save_button)
    
    def apply_settings(self):
        # Update .env file
        env_path = ".env"
        if os.path.exists(env_path):
            # Read all lines from .env
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update the values
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('DEFAULT_TIMER_DURATION='):
                        f.write(f'DEFAULT_TIMER_DURATION={self.timer_duration.value()}\n')
                    elif line.startswith('TIMER_STYLE='):
                        f.write(f'TIMER_STYLE={self.timer_style.currentText()}\n')
                    elif line.startswith('OPENAI_MODEL='):
                        f.write(f'OPENAI_MODEL={self.model_selector.currentText()}\n')
                    elif line.startswith('GAME_LANGUAGE='):
                        f.write(f'GAME_LANGUAGE={self.language_selector.currentText()}\n')
                    elif line.startswith('SUPPORT_HEBREW='):
                        f.write(f'SUPPORT_HEBREW={str(self.hebrew_support.isChecked()).lower()}\n')
                    else:
                        f.write(line)
            
            # Force reload of environment variables
            load_dotenv(override=True)
        
        # Apply settings immediately
        if self.parent:
            self.parent.timer_duration = self.timer_duration.value()
            self.parent.apply_settings()
            # Update the question generator model
            self.parent.game_manager.question_generator.update_model(self.model_selector.currentText())
            # Update language settings
            self.parent.game_manager.question_generator.update_language(
                self.language_selector.currentText(),
                self.hebrew_support.isChecked()
            )
    
    def save_settings(self):
        self.apply_settings()
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.is_paused = False
        self.token_counter = TokenCounter.get_instance()
        self.timer_duration = int(os.getenv("DEFAULT_TIMER_DURATION", 20))
        self.setup_ui()
        self.setup_sounds()
        self.setup_token_display()
        self.success_messages = [
            "Fantastic! 🌟",
            "You're on fire! 🔥",
            "Brilliant answer! 💫",
            "Amazing job! 🎯",
            "You're crushing it! 💪",
            "Outstanding! 🏆",
            "Incredible work! ⭐",
            "You're a genius! 🧠",
            "Perfect! 💯",
            "Spectacular! 🎉"
        ]
        self.streak_messages = [
            "Keep the streak alive! 🔥",
            "You're unstoppable! ⚡",
            "Nothing can stop you now! 💫",
            "You're in the zone! 🎯",
            "What a winning streak! 🏆"
        ]
        
    def setup_sounds(self):
        """Setup sound effects"""
        try:
            # Ensure sound files exist
            ensure_sound_files()
            
            # Get absolute paths for sound files
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            timer_sound = os.path.join(base_dir, "assets", "timer_alert.wav")
            success_sound = os.path.join(base_dir, "assets", "success.wav")
            
            # Create sound effects
            self.timer_alert = QSoundEffect()
            self.timer_alert.setSource(QUrl.fromLocalFile(timer_sound))
            self.timer_alert.setVolume(0.5)
            
            self.success_sound = QSoundEffect()
            self.success_sound.setSource(QUrl.fromLocalFile(success_sound))
            self.success_sound.setVolume(0.5)
            
            logger.info("Sound effects initialized successfully")
                
        except Exception as e:
            logger.error(f"Error setting up sounds: {e}")
            # Create dummy sound effects that do nothing
            self.timer_alert = type('DummySound', (), {'play': lambda: None})()
            self.success_sound = type('DummySound', (), {'play': lambda: None})()

    def create_async_callback(self, coro_func, *args, **kwargs):
        """Helper to create proper async callbacks"""
        @asyncSlot(bool)
        async def callback(checked=False):
            try:
                await coro_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in async callback: {e}")
                QMessageBox.critical(self, "Error", str(e))
        return callback

    def setup_ui(self):
        self.setWindowTitle("AI Trivia Game")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Top bar with stats and buttons
        top_bar = QHBoxLayout()
        
        # Stats area
        stats_layout = QHBoxLayout()
        self.level_label = QLabel("Level: 1")
        self.points_label = QLabel("Points: 0")
        self.streak_label = QLabel("Streak: 0")
        for label in [self.level_label, self.points_label, self.streak_label]:
            label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.level_label)
        stats_layout.addWidget(self.points_label)
        stats_layout.addWidget(self.streak_label)
        top_bar.addLayout(stats_layout)
        
        # Spacer to push buttons to the right
        top_bar.addStretch()
        
        # Pause button
        self.pause_button = QPushButton("⏸️ Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        top_bar.addWidget(self.pause_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.show_settings)
        top_bar.addWidget(self.settings_button)
        
        # Help button
        self.help_button = QPushButton("❓ Help")
        self.help_button.clicked.connect(self.show_help)
        top_bar.addWidget(self.help_button)
        
        # Achievements button
        self.achievements_button = QPushButton("🏆 Achievements")
        self.achievements_button.clicked.connect(self.show_achievements)
        top_bar.addWidget(self.achievements_button)
        
        layout.addLayout(top_bar)
        
        # Category label
        self.category_label = QLabel("")
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.category_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.category_label)
        
        # Question area
        question_frame = QFrame()
        question_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        question_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)
        question_layout = QVBoxLayout(question_frame)
        
        self.question_label = QLabel("Welcome to AI Trivia!")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setFont(QFont("Arial", 14))
        question_layout.addWidget(self.question_label)
        
        layout.addWidget(question_frame)
        
        # Hint area
        hint_frame = QFrame()
        hint_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
        """)
        hint_layout = QHBoxLayout(hint_frame)
        self.hint_label = QLabel("")
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #666; font-style: italic;")
        self.hint_button = QPushButton("💡 Use Hint (50 points)")
        self.hint_button.clicked.connect(self.use_hint)
        self.hint_button.setEnabled(False)
        self.hint_button.setFixedWidth(150)
        hint_layout.addWidget(self.hint_label)
        hint_layout.addWidget(self.hint_button)
        layout.addWidget(hint_frame)
        
        # Answer buttons
        self.answer_buttons = []
        answer_grid = QHBoxLayout()
        for i in range(4):
            btn = QPushButton(f"Option {i+1}")
            btn.setFixedHeight(40)
            btn.setFixedWidth(300)
            # Store the callback as an instance variable to prevent garbage collection
            callback = self.create_async_callback(self.check_answer, i)
            setattr(self, f'_answer_callback_{i}', callback)
            btn.clicked.connect(getattr(self, f'_answer_callback_{i}'))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
            """)
            self.answer_buttons.append(btn)
            answer_grid.addWidget(btn)
        layout.addLayout(answer_grid)
        
        # Explanation area
        self.explanation_label = QLabel("")
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 5px;
                margin: 10px;
                font-style: italic;
                color: #444;
            }
        """)
        self.explanation_label.hide()
        layout.addWidget(self.explanation_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.next_button = QPushButton("Start Game")
        self._next_callback = self.create_async_callback(self.next_question)
        self.next_button.clicked.connect(self._next_callback)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        control_layout.addWidget(self.next_button)
        layout.addLayout(control_layout)
        
        # Timer area
        timer_layout = QHBoxLayout()
        
        # Create both timer widgets
        self.timer_bar = QProgressBar()
        self.timer_bar.setMaximum(100)
        self.timer_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 15px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        
        self.analog_clock = AnalogClock()
        self.analog_clock.setFixedSize(150, 150)
        
        # Add both to layout but hide one based on settings
        timer_layout.addWidget(self.timer_bar)
        timer_layout.addWidget(self.analog_clock)
        
        # Set initial visibility based on settings
        timer_style = os.getenv("TIMER_STYLE", "Digital")
        self.timer_bar.setVisible(timer_style == "Digital")
        self.analog_clock.setVisible(timer_style == "Analog")
        
        layout.addLayout(timer_layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
    
    def setup_token_display(self):
        """Setup the token counter display in the status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.token_label = QLabel()
        self.statusBar.addPermanentWidget(self.token_label)
        self.update_token_display()
        
        # Update token display every second
        self.token_timer = QTimer()
        self.token_timer.timeout.connect(self.update_token_display)
        self.token_timer.start(1000)
    
    def update_token_display(self):
        """Update the token counter display"""
        sent, received = self.token_counter.get_counts()
        self.token_label.setText(f"Tokens - Sent: {sent} | Received: {received}")
    
    def apply_settings(self):
        """Apply settings immediately"""
        # Update timer duration from instance variable or env
        if hasattr(self, 'timer_duration'):
            new_duration = self.timer_duration
        else:
            new_duration = int(os.getenv("DEFAULT_TIMER_DURATION", 20))
            self.timer_duration = new_duration
        
        # Update timer style
        timer_style = os.getenv("TIMER_STYLE", "Digital")
        self.timer_bar.setVisible(timer_style == "Digital")
        self.analog_clock.setVisible(timer_style == "Analog")
        
        # Only update timer if it's running
        if self.timer.isActive():
            if hasattr(self, 'time_remaining'):
                # Adjust remaining time proportionally
                ratio = self.time_remaining / self.timer_duration
                self.time_remaining = new_duration * ratio
            else:
                self.time_remaining = new_duration
            
            self.timer_bar.setMaximum(new_duration)
            self.timer_bar.setValue(int(self.time_remaining))
            self.analog_clock.set_time(new_duration, self.time_remaining)
        
        # Update the stored duration
        self.timer_duration = new_duration
        
        # Force update of timer displays
        self.timer_bar.setMaximum(new_duration)
        self.analog_clock.set_time(new_duration, new_duration)
        
        logger.info(f"Applied settings - Duration: {new_duration}, Style: {timer_style}")
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Settings are now applied immediately in the dialog
            pass
    
    def toggle_pause(self):
        if self.is_paused:
            self.resume_game()
        else:
            self.pause_game()
    
    def pause_game(self):
        if not self.is_paused and self.timer.isActive():
            self.timer.stop()
            self.is_paused = True
            self.pause_button.setText("▶️ Resume")
            self.pause_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            for btn in self.answer_buttons:
                btn.setEnabled(False)
    
    def resume_game(self):
        if self.is_paused:
            self.timer.start()
            self.is_paused = False
            self.pause_button.setText("⏸️ Pause")
            self.pause_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFA500;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FF8C00;
                }
            """)
            for btn in self.answer_buttons:
                btn.setEnabled(True)
    
    def show_achievements(self):
        dialog = AchievementsDialog(self.game_manager.player.achievements, self)
        dialog.exec()
    
    def show_help(self):
        dialog = HelpDialog(self)
        dialog.exec()
    
    def use_hint(self):
        if self.game_manager.player.points >= 50:
            hint = self.game_manager.get_hint(self.current_question)
            self.hint_label.setText(f"Hint: {hint}")
            self.game_manager.player.points -= 50
            self.game_manager.player.stats["hints_used"] += 1
            self.hint_button.setEnabled(False)
            self.update_stats()
        else:
            QMessageBox.warning(self, "Not Enough Points",
                              "You need 50 points to use a hint!")
    
    @asyncSlot()
    async def next_question(self):
        self.next_button.setEnabled(False)
        
        # Clear current question immediately
        self.question_label.setText("Loading next question...")
        self.category_label.setText("")
        self.hint_label.setText("")
        self.explanation_label.hide()
        for btn in self.answer_buttons:
            btn.setText("")
            btn.setEnabled(False)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 5px;
                    font-size: 12px;
                }
            """)
        
        try:
            # Get both the question and pre-fetch the additional info
            question, explanation = await self.game_manager.get_next_question()
            self.current_question = question
            self.current_explanation = explanation
            
            # Pre-fetch additional info
            try:
                self.additional_info = await self.game_manager.question_generator.get_additional_info(
                    question.text,
                    question.correct_answer
                )
            except Exception as e:
                logger.error(f"Error pre-fetching additional info: {str(e)}", exc_info=True)
                self.additional_info = None
            
            await self.display_question(question)
            self.start_timer()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.next_button.setEnabled(True)
    
    async def display_question(self, question):
        self.current_question = question
        self.category_label.setText(f"Category: {question.category}")
        self.question_label.setText(question.text)
        
        for i, (btn, option) in enumerate(zip(self.answer_buttons, question.options)):
            btn.setText(option)
            btn.setEnabled(True)
            try:
                btn.clicked.disconnect()  # Disconnect any existing connections
            except:
                pass
            # Create and store new callback
            callback = self.create_async_callback(self.check_answer, i)
            setattr(self, f'_answer_callback_{i}', callback)
            btn.clicked.connect(getattr(self, f'_answer_callback_{i}'))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
        
        self.hint_button.setEnabled(True)
    
    async def show_explanation(self, is_correct: bool):
        try:
            # Use pre-fetched additional info
            if hasattr(self, 'additional_info') and self.additional_info:
                full_explanation = f"{self.current_explanation}\n\n{self.additional_info}"
            else:
                full_explanation = self.current_explanation
            
            # Show the explanation with appropriate styling
            self.explanation_label.setText(full_explanation)
            self.explanation_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {('#e8f5e9' if is_correct else '#ffebee')};
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px;
                    font-style: italic;
                    color: #444;
                }}
            """)
            self.explanation_label.show()
            
        except Exception as e:
            logger.error(f"Error showing explanation: {str(e)}", exc_info=True)
            try:
                self.explanation_label.setText("Explanation not available.")
                self.explanation_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {('#e8f5e9' if is_correct else '#ffebee')};
                        padding: 15px;
                        border-radius: 5px;
                        margin: 10px;
                        font-style: italic;
                        color: #444;
                    }}
                """)
                self.explanation_label.show()
            except:
                logger.error("Failed to show fallback explanation", exc_info=True)
    
    async def check_answer(self, option_index):
        try:
            if self.is_paused:
                return
            
            logger.info(f"Checking answer for option {option_index}")
            selected = self.current_question.options[option_index]
            correct = selected == self.current_question.correct_answer
            logger.info(f"Selected: {selected}, Correct: {self.current_question.correct_answer}")
            
            self.timer.stop()
            for btn in self.answer_buttons:
                btn.setEnabled(False)
            
            # Highlight correct and wrong answers
            for i, btn in enumerate(self.answer_buttons):
                if self.current_question.options[i] == self.current_question.correct_answer:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            padding: 5px;
                            margin: 5px;
                            font-size: 12px;
                        }
                    """)
                elif i == option_index and not correct:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            padding: 5px;
                            margin: 5px;
                            font-size: 12px;
                        }
                    """)
            
            try:
                if correct:
                    # Play success sound
                    self.success_sound.play()
                    
                    time_bonus = max(0, int(self.time_remaining))
                    logger.info(f"Correct answer! Time bonus: {time_bonus}")
                    earned_points = self.game_manager.handle_correct_answer(time_bonus)
                    
                    # Generate success message with emojis
                    success_msg = random.choice(self.success_messages)
                    streak_msg = ""
                    if self.game_manager.player.streak > 1:
                        streak_msg = f"\n\n{random.choice(self.streak_messages)}"
                    
                    # Add level up message if applicable
                    level_msg = ""
                    if self.game_manager.player.points >= (self.game_manager.player.level * 500):
                        level_msg = f"\n\n🎮 Level Up! You're now level {self.game_manager.player.level}! 🎮"
                    
                    QMessageBox.information(
                        self, "Correct! 🌟",
                        f"{success_msg}\n\n" +
                        f"You earned {earned_points} points " +
                        f"(including {time_bonus} time bonus points)!" +
                        streak_msg +
                        level_msg
                    )
                else:
                    logger.info("Incorrect answer")
                    self.game_manager.handle_wrong_answer()
                    QMessageBox.warning(
                        self, "Incorrect",
                        f"The correct answer was: {self.current_question.correct_answer}\n\n" +
                        "Don't worry, you'll get it next time! 💪"
                    )
            except Exception as e:
                logger.error(f"Error handling answer result: {str(e)}", exc_info=True)
            
            # Show explanation immediately since we pre-fetched it
            try:
                logger.info("Showing explanation")
                await self.show_explanation(correct)
            except Exception as e:
                logger.error(f"Error showing explanation: {str(e)}", exc_info=True)
            
            try:
                # Check for new achievements
                logger.info("Checking achievements")
                new_achievements = self.game_manager.check_achievements(self.time_remaining)
                if new_achievements:
                    # Play success sound for achievements too
                    self.success_sound.play()
                    achievements_text = "\n".join(
                        f"🏆 {achievement.name}: {achievement.description}"
                        for achievement in new_achievements
                    )
                    QMessageBox.information(
                        self,
                        "Achievement Unlocked! 🎉",
                        f"Congratulations! You're amazing!\n\n" +
                        f"You've earned new achievements:\n\n{achievements_text}"
                    )
            except Exception as e:
                logger.error(f"Error checking achievements: {str(e)}", exc_info=True)
            
            try:
                self.update_stats()
            except Exception as e:
                logger.error(f"Error updating stats: {str(e)}", exc_info=True)
            
        except Exception as e:
            logger.error(f"Error in check_answer: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            # Always enable the next button and update its text
            self.next_button.setText("Next Question")
            self.next_button.setEnabled(True)
            logger.info("Next button enabled")
    
    def update_stats(self):
        player = self.game_manager.player
        self.level_label.setText(f"Level: {player.level}")
        self.points_label.setText(f"Points: {player.points}")
        self.streak_label.setText(f"Streak: {player.streak}")
    
    def start_timer(self, duration=None):
        if duration is None:
            duration = self.timer_duration
        self.time_remaining = duration
        self.timer_duration = duration  # Store the current duration
        self.timer_bar.setMaximum(duration)
        self.timer_bar.setValue(duration)
        self.timer_bar.setFormat("%v seconds")
        self.analog_clock.set_time(duration, duration)
        self._alert_played = False
        self.timer.start(100)  # Update every 100ms
        logger.info(f"Started timer with duration: {duration} seconds")
    
    def update_timer(self):
        try:
            if not hasattr(self, 'time_remaining'):
                self.time_remaining = self.timer_duration
            
            self.time_remaining -= 0.1
            
            # Update both timer displays
            self.timer_bar.setValue(int(self.time_remaining))
            self.analog_clock.set_time(self.timer_duration, self.time_remaining)
            
            # Change color and play sound when time is low
            if self.time_remaining <= 5:
                if not hasattr(self, '_alert_played') or not self._alert_played:
                    self.timer_alert.play()
                    self._alert_played = True
                elif self.time_remaining <= 3:
                    # Play alert sound every half second in last 3 seconds
                    if int(self.time_remaining * 2) != int((self.time_remaining + 0.1) * 2):
                        self.timer_alert.play()
                
                self.timer_bar.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        border-radius: 5px;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: #f44336;
                        border-radius: 5px;
                    }
                """)
            
            if self.time_remaining <= 0:
                self.timer.stop()
                self.time_up()
        except Exception as e:
            logger.error(f"Error in update_timer: {str(e)}")
            self.timer.stop()
            self.next_button.setEnabled(True)
    
    def time_up(self):
        self.timer.stop()
        for btn in self.answer_buttons:
            btn.setEnabled(False)
            if btn.text() == self.current_question.correct_answer:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
        
        QMessageBox.warning(
            self,
            "Time's Up!",
            f"The correct answer was: {self.current_question.correct_answer}"
        )
        
        self.game_manager.handle_wrong_answer()
        self.update_stats()
        self.next_button.setEnabled(True) 