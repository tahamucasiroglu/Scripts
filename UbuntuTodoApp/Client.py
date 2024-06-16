import sys
import json
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QDateTimeEdit, QTextEdit, QComboBox, QWidget, QMessageBox)
from PyQt5.QtCore import QDateTime

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Görev Ekleme İstemcisi")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.ip_input_layout = QHBoxLayout()
        
        self.ip_label = QLabel("Sunucu IP:")
        self.ip_input_layout.addWidget(self.ip_label)
        self.ip_input = QLineEdit()
        self.ip_input_layout.addWidget(self.ip_input)
        
        self.layout.addLayout(self.ip_input_layout)

        self.task_input_layout = QVBoxLayout()
        
        self.title_label = QLabel("Başlık:")
        self.task_input_layout.addWidget(self.title_label)
        self.title_input = QLineEdit()
        self.title_input.setMaxLength(50)
        self.task_input_layout.addWidget(self.title_input)
        
        self.desc_label = QLabel("Açıklama:")
        self.task_input_layout.addWidget(self.desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(50)
        self.task_input_layout.addWidget(self.desc_input)
        
        self.reminder_label = QLabel("Hatırlatma:")
        self.task_input_layout.addWidget(self.reminder_label)
        self.reminder_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.reminder_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.task_input_layout.addWidget(self.reminder_input)
        
        self.due_date_label = QLabel("Bitiş Tarihi:")
        self.task_input_layout.addWidget(self.due_date_label)
        self.due_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.due_date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.task_input_layout.addWidget(self.due_date_input)
        
        self.priority_label = QLabel("Öncelik:")
        self.task_input_layout.addWidget(self.priority_label)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["red", "yellow", "green"])
        self.task_input_layout.addWidget(self.priority_input)
        
        self.add_task_button = QPushButton("Görev Ekle")
        self.add_task_button.clicked.connect(self.send_task)
        self.task_input_layout.addWidget(self.add_task_button)

        self.layout.addLayout(self.task_input_layout)

    def send_task(self):
        ip_address = self.ip_input.text().strip()
        if not ip_address:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir IP adresi girin.")
            return

        task = {
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "reminder": self.reminder_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "due_date": self.due_date_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "priority": self.priority_input.currentText()
        }
        
        try:
            url = f'http://{ip_address}:5000/add_task'
            response = requests.post(url, json=task)
            if response.status_code == 200:
                QMessageBox.information(self, "Başarılı", "Görev başarıyla eklendi.")
            else:
                QMessageBox.warning(self, "Hata", f"Görev eklenemedi. Durum Kodu: {response.status_code}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Hata", f"Sunucuya bağlanılamadı: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientApp()
    window.show()
    sys.exit(app.exec_())
