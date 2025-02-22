from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen
import math


class AnalogClock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_time = 20  # Default time in seconds
        self.time_remaining = self.total_time
        self.setMinimumSize(100, 100)  # Minimum size for the clock
        self.alert_threshold = 5  # Seconds remaining when to start alert color
        self.is_alert = False
    
    def set_time(self, total_time: int, time_remaining: float):
        """Set the clock time"""
        self.total_time = total_time
        self.time_remaining = time_remaining
        self.is_alert = time_remaining <= self.alert_threshold
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate clock dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        center = QPoint(width // 2, height // 2)
        radius = (size - 10) // 2  # Leave some margin
        
        # Draw clock face
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(center, radius, radius)
        
        # Draw time markers
        for i in range(12):
            angle = i * 30  # 360 degrees / 12 markers
            rad_angle = math.radians(angle - 90)  # -90 to start at 12 o'clock
            outer_x = center.x() + int(radius * 0.9 * math.cos(rad_angle))
            outer_y = center.y() + int(radius * 0.9 * math.sin(rad_angle))
            inner_x = center.x() + int(radius * 0.8 * math.cos(rad_angle))
            inner_y = center.y() + int(radius * 0.8 * math.sin(rad_angle))
            painter.drawLine(inner_x, inner_y, outer_x, outer_y)
        
        # Draw time remaining arc
        if self.time_remaining > 0:
            angle = int((self.time_remaining / self.total_time) * 360)
            # Use red color for alert
            if self.is_alert:
                painter.setPen(QPen(QColor("#f44336"), 6))
            else:
                painter.setPen(QPen(QColor("#4CAF50"), 6))
            
            # Create a rectangle for the arc
            arc_rect = QRect(
                center.x() - radius + 5,
                center.y() - radius + 5,
                2 * radius - 10,
                2 * radius - 10
            )
            painter.drawArc(arc_rect, 90 * 16, -angle * 16)  # Qt uses 1/16th of a degree
        
        # Draw hand
        if self.time_remaining > 0:
            angle = (self.time_remaining / self.total_time) * 360 - 90  # -90 to start at 12 o'clock
            rad_angle = math.radians(angle)
            hand_length = radius * 0.7
            end_x = center.x() + int(hand_length * math.cos(rad_angle))
            end_y = center.y() + int(hand_length * math.sin(rad_angle))
            
            # Use red color for alert
            if self.is_alert:
                painter.setPen(QPen(QColor("#f44336"), 3))
            else:
                painter.setPen(QPen(Qt.GlobalColor.black, 3))
            painter.drawLine(center, QPoint(end_x, end_y))
        
        # Draw center dot
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.black)
        painter.drawEllipse(center, 4, 4)
        
        # Draw time text
        painter.setPen(Qt.GlobalColor.black)
        text = f"{int(self.time_remaining)}s"
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        text_rect = painter.fontMetrics().boundingRect(text)
        painter.drawText(center.x() - text_rect.width() // 2,
                        center.y() + radius // 2,
                        text) 