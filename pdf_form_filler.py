import cv2
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import sqlite3
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMenuBar, QAction
import csv

# SQLite Database Setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

def export_logs():
    with open("form_filling_logs.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Father Name", "CNIC", "DOB"])
        writer.writerow(["Example Name", "Example Father", "12345-6789012-3", "01-01-2000"])  # Dummy data for now
    QtWidgets.QMessageBox.information(None, "Export Logs", "Logs exported successfully as CSV!")

# Function to extract text from an image
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(img)
    return text.strip()

class FormFillerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Birth Registration Form Filler")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("background-color: #333; color: white; font-size: 14px;")

        layout = QtWidgets.QVBoxLayout()
        
        # Menu Bar
        menubar = QMenuBar(self)
        settingsMenu = menubar.addMenu("Settings")
        toggleThemeAction = QAction("Toggle Light/Dark Mode", self)
        toggleThemeAction.triggered.connect(self.toggle_theme)
        settingsMenu.addAction(toggleThemeAction)
        layout.setMenuBar(menubar)

        self.uploadButton = QtWidgets.QPushButton("Upload ID Card Image")
        self.uploadButton.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.uploadButton.clicked.connect(self.upload_image)
        layout.addWidget(self.uploadButton)
        
        self.imageLabel = QLabel()
        layout.addWidget(self.imageLabel)
        
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setStyleSheet("background-color: #444; color: white;")
        layout.addWidget(self.textEdit)
        
        self.previewButton = QtWidgets.QPushButton("Preview PDF")
        self.previewButton.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.previewButton.clicked.connect(self.preview_pdf)
        layout.addWidget(self.previewButton)
        
        self.saveButton = QtWidgets.QPushButton("Save & Fill PDF")
        self.saveButton.setStyleSheet("background-color: #008CBA; color: white; padding: 10px; border-radius: 5px;")
        self.saveButton.clicked.connect(self.save_and_fill_pdf)
        layout.addWidget(self.saveButton)
        
        self.exportLogsButton = QtWidgets.QPushButton("Export Logs")
        self.exportLogsButton.setStyleSheet("background-color: #FF4500; color: white; padding: 10px; border-radius: 5px;")
        self.exportLogsButton.clicked.connect(export_logs)
        layout.addWidget(self.exportLogsButton)
        
        self.setLayout(layout)

    def toggle_theme(self):
        if self.styleSheet() == "background-color: #333; color: white; font-size: 14px;":
            self.setStyleSheet("background-color: #FFF; color: black; font-size: 14px;")
            self.textEdit.setStyleSheet("background-color: #EEE; color: black;")
        else:
            self.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
            self.textEdit.setStyleSheet("background-color: #444; color: white;")
    
    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select ID Card Image", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            pixmap = QPixmap(file_path)
            self.imageLabel.setPixmap(pixmap.scaled(400, 300))
            text_data = extract_text_from_image(file_path)
            self.textEdit.setText(text_data)
    
    def preview_pdf(self):
        os.system("start filled_form.pdf")  # Opens the generated PDF for preview
    
    def save_and_fill_pdf(self):
        text_data = self.textEdit.toPlainText().split('\n')
        parsed_data = {
            "name": text_data[0] if len(text_data) > 0 else "",
            "father_name": text_data[1] if len(text_data) > 1 else "",
            "cnic": text_data[2] if len(text_data) > 2 else "",
            "dob": text_data[3] if len(text_data) > 3 else ""
        }
        fill_pdf("new_birth_registration_form.pdf", "filled_form.pdf", parsed_data)
        QtWidgets.QMessageBox.information(self, "Success", "PDF filled and saved successfully!")

if __name__ == "__main__":
    import sys
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    loginWindow = FormFillerApp()
    loginWindow.show()
    sys.exit(app.exec_())
