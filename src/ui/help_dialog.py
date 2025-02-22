from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QTabWidget, QLineEdit,
    QHBoxLayout, QListWidget, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QKeySequence, QShortcut


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_shortcuts()
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Tab navigation shortcuts
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tab_widget.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tab_widget.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.tab_widget.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.tab_widget.setCurrentIndex(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.tab_widget.setCurrentIndex(4))
        QShortcut(QKeySequence("Ctrl+6"), self, lambda: self.tab_widget.setCurrentIndex(5))
        QShortcut(QKeySequence("Ctrl+7"), self, lambda: self.tab_widget.setCurrentIndex(6))
        
        # Search shortcut
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.search_input.setFocus())
        
        # Close dialog shortcut
        QShortcut(QKeySequence("Esc"), self, self.accept)
    
    @pyqtSlot(str)
    def search_help(self, text):
        """Search help content and show matching items"""
        self.search_results.clear()
        if not text:
            self.stacked_widget.setCurrentIndex(0)
            return
            
        search_text = text.lower()
        results = []
        
        # Search in all help content
        for tab_index in range(self.tab_widget.count()):
            tab_text = self.tab_widget.tabText(tab_index)
            widget = self.tab_widget.widget(tab_index)
            content = widget.findChild(QLabel).text().lower()
            
            if search_text in content:
                # Find specific matching sections
                sections = content.split("<h3>")
                for section in sections:
                    if search_text in section:
                        # Extract section title
                        title = section.split("</h3>")[0].strip() if "</h3>" in section else tab_text
                        results.append(f"{tab_text} → {title}")
        
        self.search_results.addItems(results)
        self.stacked_widget.setCurrentIndex(1)
    
    @pyqtSlot(str)
    def on_result_selected(self, item):
        """Handle search result selection"""
        if not item:
            return
        # Extract tab name and switch to it
        tab_name = item.split(" → ")[0]
        for i in range(self.tab_widget.count()):
            if tab_name in self.tab_widget.tabText(i):
                self.tab_widget.setCurrentIndex(i)
                break
        self.stacked_widget.setCurrentIndex(0)
        self.search_input.clear()
        
    def setup_ui(self):
        self.setWindowTitle("Game Help")
        self.setMinimumSize(800, 600)  # Increased size for better readability
        
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search help (Ctrl+F)")
        self.search_input.textChanged.connect(self.search_help)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Stacked widget for main content and search results
        self.stacked_widget = QStackedWidget()
        
        # Main content widget
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # What's New tab
        whats_new_tab = QWidget()
        whats_new_layout = QVBoxLayout(whats_new_tab)
        whats_new_text = """
        <h2>What's New</h2>
        
        <h3>Latest Updates:</h3>
        <ul>
            <li><b>🔍 Search Function</b>
                <ul>
                    <li>Quick search across all help topics (Ctrl+F)</li>
                    <li>Real-time search results</li>
                    <li>Direct navigation to relevant sections</li>
                </ul>
            </li>
            <li><b>⌨️ Keyboard Shortcuts</b>
                <ul>
                    <li>Added shortcuts for all major functions</li>
                    <li>Quick tab navigation with Ctrl+1 through Ctrl+7</li>
                    <li>Easy dialog navigation with Esc key</li>
                </ul>
            </li>
            <li><b>🎯 Category Examples</b>
                <ul>
                    <li>Added specific examples for each category</li>
                    <li>Improved category descriptions</li>
                    <li>Better difficulty level explanations</li>
                </ul>
            </li>
            <li><b>🔧 Troubleshooting Guide</b>
                <ul>
                    <li>Comprehensive error resolution steps</li>
                    <li>Performance optimization tips</li>
                    <li>Common issues and solutions</li>
                </ul>
            </li>
        </ul>
        
        <h3>Coming Soon:</h3>
        <ul>
            <li>Interactive tutorial mode</li>
            <li>More achievements and rewards</li>
            <li>Additional question categories</li>
            <li>Performance improvements</li>
        </ul>
        """
        whats_new_label = QLabel(whats_new_text)
        whats_new_label.setWordWrap(True)
        whats_new_label.setTextFormat(Qt.TextFormat.RichText)
        whats_new_layout.addWidget(whats_new_label)
        self.tab_widget.addTab(whats_new_tab, "What's New (Ctrl+1)")
        
        # Getting Started tab
        getting_started_tab = QWidget()
        getting_started_layout = QVBoxLayout(getting_started_tab)
        getting_started_text = """
        <h2>Getting Started</h2>
        <p>Welcome to AI Trivia! This game uses artificial intelligence to create dynamic and engaging questions 
        tailored to your performance level.</p>
        
        <h3>Quick Start:</h3>
        <ol>
            <li>Click "Start Game" to begin</li>
            <li>Read the question carefully</li>
            <li>Select your answer before the timer runs out</li>
            <li>Earn points and unlock achievements as you play</li>
        </ol>
        
        <h3>Game Controls:</h3>
        <ul>
            <li><b>⏸️ Pause</b> (Space): Pause the current game</li>
            <li><b>⚙️ Settings</b> (Ctrl+S): Adjust game settings</li>
            <li><b>❓ Help</b> (F1): View this help menu</li>
            <li><b>🏆 Achievements</b> (Ctrl+A): View your achievements</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
            <li><b>1-4</b>: Select answer options</li>
            <li><b>H</b>: Use hint (if available)</li>
            <li><b>N</b>: Next question</li>
            <li><b>Space</b>: Pause/Resume game</li>
            <li><b>Esc</b>: Close dialogs</li>
        </ul>
        
        <h3>Timer Styles:</h3>
        <ul>
            <li><b>Digital</b>: Shows remaining seconds numerically</li>
            <li><b>Analog</b>: Shows a clock-style countdown</li>
        </ul>
        """
        getting_started_label = QLabel(getting_started_text)
        getting_started_label.setWordWrap(True)
        getting_started_label.setTextFormat(Qt.TextFormat.RichText)
        getting_started_layout.addWidget(getting_started_label)
        self.tab_widget.addTab(getting_started_tab, "Getting Started (Ctrl+2)")
        
        # Scoring System tab
        scoring_tab = QWidget()
        scoring_layout = QVBoxLayout(scoring_tab)
        scoring_text = """
        <h2>Scoring System</h2>
        
        <h3>Points Calculation:</h3>
        <ul>
            <li><b>Base Points</b>: 10-100 points based on question difficulty</li>
            <li><b>Time Bonus</b>: 2 points per second remaining</li>
            <li><b>Streak Bonus</b>: +10% per correct answer (max 100%)</li>
        </ul>
        
        <h3>Leveling System:</h3>
        <ul>
            <li>Level up every 500 points</li>
            <li>Higher levels unlock harder questions</li>
            <li>Each level increases potential point rewards</li>
        </ul>
        
        <h3>Streaks:</h3>
        <ul>
            <li>Build streaks by answering correctly</li>
            <li>Each correct answer adds to your streak</li>
            <li>Wrong answers reset your streak to 0</li>
            <li>Higher streaks mean bigger point bonuses</li>
        </ul>
        
        <h3>Hints:</h3>
        <ul>
            <li>Cost: 50 points per hint</li>
            <li>Shows first letter and length of answer</li>
            <li>Use wisely to maintain high scores</li>
        </ul>
        """
        scoring_label = QLabel(scoring_text)
        scoring_label.setWordWrap(True)
        scoring_label.setTextFormat(Qt.TextFormat.RichText)
        scoring_layout.addWidget(scoring_label)
        self.tab_widget.addTab(scoring_tab, "Scoring (Ctrl+3)")
        
        # Categories tab with examples
        categories_tab = QWidget()
        categories_layout = QVBoxLayout(categories_tab)
        categories_text = """
        <h2>Question Categories</h2>
        
        <h3>Available Categories:</h3>
        <ul>
            <li><b>🔬 Science</b>: Physics, Chemistry, Biology, and more
                <ul>
                    <li>Example: "What is the speed of light in a vacuum?"</li>
                    <li>Example: "Which element has the atomic number 6?"</li>
                </ul>
            </li>
            <li><b>📚 History</b>: World events, civilizations, and important figures
                <ul>
                    <li>Example: "Who was the first President of the United States?"</li>
                    <li>Example: "In which year did World War II end?"</li>
                </ul>
            </li>
            <li><b>🌍 Geography</b>: Countries, capitals, landmarks, and cultures
                <ul>
                    <li>Example: "What is the capital of Japan?"</li>
                    <li>Example: "Which river is the longest in the world?"</li>
                </ul>
            </li>
            <li><b>🎬 Entertainment</b>: Movies, TV shows, music, and celebrities
                <ul>
                    <li>Example: "Who directed the movie 'Inception'?"</li>
                    <li>Example: "Which band performed 'Bohemian Rhapsody'?"</li>
                </ul>
            </li>
            <li><b>⚽ Sports</b>: Athletes, teams, championships, and records
                <ul>
                    <li>Example: "Who holds the record for most Olympic gold medals?"</li>
                    <li>Example: "Which team won the first FIFA World Cup?"</li>
                </ul>
            </li>
            <li><b>💻 Technology</b>: Computers, internet, gadgets, and innovation
                <ul>
                    <li>Example: "Who co-founded Apple Computer with Steve Jobs?"</li>
                    <li>Example: "What does CPU stand for?"</li>
                </ul>
            </li>
            <li><b>🎨 Arts</b>: Paintings, sculpture, architecture, and artists
                <ul>
                    <li>Example: "Who painted the Mona Lisa?"</li>
                    <li>Example: "Which architectural style features flying buttresses?"</li>
                </ul>
            </li>
            <li><b>📖 Literature</b>: Books, authors, poems, and literary works
                <ul>
                    <li>Example: "Who wrote 'Romeo and Juliet'?"</li>
                    <li>Example: "What is the first book in The Lord of the Rings trilogy?"</li>
                </ul>
            </li>
        </ul>
        
        <h3>Difficulty Levels:</h3>
        <p>Questions adapt to your performance:</p>
        <ul>
            <li><b>Basic</b> (Levels 1-3): Fundamental knowledge</li>
            <li><b>Intermediate</b> (Levels 4-7): More challenging concepts</li>
            <li><b>Advanced</b> (Levels 8-10): Expert-level questions</li>
        </ul>
        """
        categories_label = QLabel(categories_text)
        categories_label.setWordWrap(True)
        categories_label.setTextFormat(Qt.TextFormat.RichText)
        categories_layout.addWidget(categories_label)
        self.tab_widget.addTab(categories_tab, "Categories (Ctrl+4)")
        
        # Achievements tab
        achievements_tab = QWidget()
        achievements_layout = QVBoxLayout(achievements_tab)
        achievements_text = """
        <h2>Achievements</h2>
        
        <h3>Milestone Achievements:</h3>
        <ul>
            <li><b>🌟 First Steps</b>: Answer your first question correctly</li>
            <li><b>🔥 Hot Streak</b>: Get 5 correct answers in a row</li>
            <li><b>⚡ Unstoppable</b>: Get 10 correct answers in a row</li>
            <li><b>💎 Point Collector</b>: Earn 100 points</li>
            <li><b>🏅 Point Master</b>: Earn 500 points</li>
            <li><b>👑 Point Champion</b>: Earn 1000 points</li>
        </ul>
        
        <h3>Special Achievements:</h3>
        <ul>
            <li><b>⭐ Rising Star</b>: Reach level 5</li>
            <li><b>🎓 Knowledge Master</b>: Reach level 10</li>
            <li><b>🎯 Jack of All Trades</b>: Answer questions from all categories</li>
            <li><b>⚡ Speed Demon</b>: Answer 5 questions with >10 seconds remaining</li>
        </ul>
        
        <h3>Achievement Benefits:</h3>
        <ul>
            <li>Track your progress</li>
            <li>Show off your expertise</li>
            <li>Set personal goals</li>
            <li>Unlock special recognition</li>
        </ul>
        """
        achievements_label = QLabel(achievements_text)
        achievements_label.setWordWrap(True)
        achievements_label.setTextFormat(Qt.TextFormat.RichText)
        achievements_layout.addWidget(achievements_label)
        self.tab_widget.addTab(achievements_tab, "Achievements (Ctrl+5)")
        
        # Tips & Tricks tab
        tips_tab = QWidget()
        tips_layout = QVBoxLayout(tips_tab)
        tips_text = """
        <h2>Tips & Tricks</h2>
        
        <h3>Maximizing Points:</h3>
        <ul>
            <li>Answer quickly for time bonus points</li>
            <li>Build and maintain answer streaks</li>
            <li>Save hints for really tough questions</li>
            <li>Focus on your strongest categories first</li>
        </ul>
        
        <h3>Time Management:</h3>
        <ul>
            <li>Read the question carefully but quickly</li>
            <li>Use process of elimination</li>
            <li>Don't spend too long on any one question</li>
            <li>Watch the timer color for last 5 seconds</li>
        </ul>
        
        <h3>Learning Strategy:</h3>
        <ul>
            <li>Read explanations after each question</li>
            <li>Pay attention to additional facts provided</li>
            <li>Try different categories to expand knowledge</li>
            <li>Challenge yourself with harder difficulties</li>
        </ul>
        
        <h3>Common Mistakes to Avoid:</h3>
        <ul>
            <li>Don't rush without reading carefully</li>
            <li>Don't waste points on unnecessary hints</li>
            <li>Don't ignore the explanations</li>
            <li>Don't stick to only one category</li>
        </ul>
        """
        tips_label = QLabel(tips_text)
        tips_label.setWordWrap(True)
        tips_label.setTextFormat(Qt.TextFormat.RichText)
        tips_layout.addWidget(tips_label)
        self.tab_widget.addTab(tips_tab, "Tips & Tricks (Ctrl+6)")
        
        # Add Troubleshooting tab
        troubleshooting_tab = QWidget()
        troubleshooting_layout = QVBoxLayout(troubleshooting_tab)
        troubleshooting_text = """
        <h2>Troubleshooting</h2>
        
        <h3>Common Issues:</h3>
        <ul>
            <li><b>Game Won't Start</b>:
                <ul>
                    <li>Check if OpenAI API key is correctly set in .env file</li>
                    <li>Verify internet connection</li>
                    <li>Restart the application</li>
                </ul>
            </li>
            <li><b>Questions Load Slowly</b>:
                <ul>
                    <li>Check internet connection speed</li>
                    <li>Consider switching to GPT-3.5-turbo model</li>
                    <li>Wait for pre-fetching to complete</li>
                </ul>
            </li>
            <li><b>Sound Issues</b>:
                <ul>
                    <li>Check system volume</li>
                    <li>Verify sound files in assets folder</li>
                    <li>Restart the application</li>
                </ul>
            </li>
            <li><b>UI Problems</b>:
                <ul>
                    <li>Update PyQt6 to latest version</li>
                    <li>Check display resolution settings</li>
                    <li>Clear application cache</li>
                </ul>
            </li>
        </ul>
        
        <h3>Error Messages:</h3>
        <ul>
            <li><b>"API Key Invalid"</b>: Check .env file configuration</li>
            <li><b>"Rate Limit Exceeded"</b>: Wait a few minutes or upgrade API plan</li>
            <li><b>"Connection Error"</b>: Check internet connection</li>
            <li><b>"Model Not Available"</b>: Switch to a different OpenAI model</li>
        </ul>
        
        <h3>Performance Tips:</h3>
        <ul>
            <li>Close other resource-intensive applications</li>
            <li>Ensure stable internet connection</li>
            <li>Keep the game updated to latest version</li>
            <li>Clear old log files periodically</li>
        </ul>
        
        <h3>Getting Help:</h3>
        <ul>
            <li>Check the logs in the logs/ directory</li>
            <li>Visit the project's GitHub page</li>
            <li>Submit an issue with error details</li>
            <li>Contact support with logs attached</li>
        </ul>
        """
        troubleshooting_label = QLabel(troubleshooting_text)
        troubleshooting_label.setWordWrap(True)
        troubleshooting_label.setTextFormat(Qt.TextFormat.RichText)
        troubleshooting_layout.addWidget(troubleshooting_label)
        self.tab_widget.addTab(troubleshooting_tab, "Troubleshooting (Ctrl+6)")
        
        main_layout.addWidget(self.tab_widget)
        
        # Search results widget
        search_results_widget = QWidget()
        search_results_layout = QVBoxLayout(search_results_widget)
        self.search_results = QListWidget()
        self.search_results.itemClicked.connect(lambda item: self.on_result_selected(item.text()))
        search_results_layout.addWidget(QLabel("Search Results:"))
        search_results_layout.addWidget(self.search_results)
        
        # Add widgets to stacked widget
        self.stacked_widget.addWidget(main_content)
        self.stacked_widget.addWidget(search_results_widget)
        
        layout.addWidget(self.stacked_widget)
        
        # Close button with shortcut hint
        close_button = QPushButton("Close (Esc)")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button) 