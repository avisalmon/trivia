from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QWidget, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from typing import List
from src.models.player import Achievement


class AchievementsDialog(QDialog):
    def __init__(self, achievements: List[Achievement], parent=None):
        super().__init__(parent)
        self.achievements = achievements
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Achievements")
        self.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Your Achievements")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Scroll area for achievements
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add achievements
        for achievement in self.achievements:
            achievement_widget = self.create_achievement_widget(achievement)
            scroll_layout.addWidget(achievement_widget)
        
        # Add stretch to push achievements to the top
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def create_achievement_widget(self, achievement: Achievement) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Achievement icon (locked/unlocked)
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        if achievement.unlocked_at:
            icon_label.setText("🏆")  # Unicode trophy for unlocked
        else:
            icon_label.setText("🔒")  # Unicode lock for locked
        layout.addWidget(icon_label)
        
        # Achievement details
        details_layout = QVBoxLayout()
        
        name_label = QLabel(achievement.name)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        details_layout.addWidget(name_label)
        
        desc_label = QLabel(achievement.description)
        desc_label.setWordWrap(True)
        details_layout.addWidget(desc_label)
        
        if achievement.unlocked_at:
            unlocked_label = QLabel(f"Unlocked: {achievement.unlocked_at.strftime('%Y-%m-%d %H:%M')}")
            unlocked_label.setStyleSheet("color: green;")
            details_layout.addWidget(unlocked_label)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        # Style the widget
        widget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
        """)
        
        return widget 