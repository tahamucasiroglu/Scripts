import sys
import json
import threading
from flask import Flask, request, jsonify
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QMessageBox,
                             QComboBox, QLabel, QLineEdit, QDateTimeEdit, QTextEdit, QDialog, QGridLayout, QInputDialog)
from PyQt5.QtCore import Qt, QDateTime, QTimer

app = Flask(__name__)

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ToDo Uygulaması")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.task_input_layout = QHBoxLayout()
        
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
        self.add_task_button.clicked.connect(self.add_task_from_ui)
        self.task_input_layout.addWidget(self.add_task_button)

        self.layout.addLayout(self.task_input_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Başlık", "Açıklama", "Hatırlatma Zamanı", "Bitiş Zamanı", "Kalan Süre"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.edit_task)

        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Bitiş Zamanı (Yakına)", "Bitiş Zamanı (Uzağa)", "Hatırlatma Zamanı (Yakına)", "Hatırlatma Zamanı (Uzağa)", "Eklenme Zamanı (Yakına)", "Eklenme Zamanı (Uzağa)", "Öncelik"])
        self.sort_combo.currentIndexChanged.connect(self.sort_tasks)
        button_layout.addWidget(self.sort_combo)

        self.complete_button = QPushButton("Tamamla")
        self.complete_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.complete_button.clicked.connect(self.complete_task)

        self.delete_button = QPushButton("Sil")
        self.delete_button.setStyleSheet("background-color: #F44336; color: white; padding: 10px;")
        self.delete_button.clicked.connect(self.delete_task)

        self.show_completed_button = QPushButton("Tamamlananları Göster")
        self.show_completed_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.show_completed_button.clicked.connect(self.show_completed_tasks)

        button_layout.addWidget(self.complete_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.show_completed_button)

        self.layout.addLayout(button_layout)

        self.load_tasks()
        self.load_completed_tasks()
        self.load_deleted_tasks()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_remaining_times)
        self.timer.start(1000)

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as file:
                self.tasks = json.load(file)
        except FileNotFoundError:
            self.tasks = []

        self.table.setRowCount(0)
        for task in self.tasks:
            self.add_task_to_table(task)

    def save_tasks(self):
        with open("tasks.json", "w") as file:
            json.dump(self.tasks, file, indent=4)

    def load_completed_tasks(self):
        try:
            with open("completed_tasks.json", "r") as file:
                self.completed_tasks = json.load(file)
        except FileNotFoundError:
            self.completed_tasks = []

    def save_completed_tasks(self):
        with open("completed_tasks.json", "w") as file:
            json.dump(self.completed_tasks, file, indent=4)

    def load_deleted_tasks(self):
        try:
            with open("deleted_tasks.json", "r") as file:
                self.deleted_tasks = json.load(file)
        except FileNotFoundError:
            self.deleted_tasks = []

    def save_deleted_tasks(self):
        with open("deleted_tasks.json", "w") as file:
            json.dump(self.deleted_tasks, file, indent=4)

    def add_task_from_ui(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Hata", "Başlık boş olamaz!")
            return

        new_id = self.get_next_id()
        task = {
            "id": new_id,
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "reminder": self.reminder_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "due_date": self.due_date_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "priority": self.priority_input.currentText()
        }
        self.tasks.append(task)
        self.add_task_to_table(task)
        self.save_tasks()

    def add_task_from_api(self, task):
        new_id = self.get_next_id()
        task["id"] = new_id
        self.tasks.append(task)
        self.add_task_to_table(task)
        self.save_tasks()

    def add_task_to_table(self, task):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(str(task["id"])))
        self.table.setItem(row_position, 1, QTableWidgetItem(task["title"]))
        self.table.setItem(row_position, 2, QTableWidgetItem(task["description"]))
        self.table.setItem(row_position, 3, QTableWidgetItem(task["reminder"]))
        self.table.setItem(row_position, 4, QTableWidgetItem(task["due_date"]))
        self.table.setItem(row_position, 5, QTableWidgetItem())

        if task["priority"] == "red":
            self.set_row_color(row_position, Qt.red)
        elif task["priority"] == "yellow":
            self.set_row_color(row_position, Qt.yellow)
        elif task["priority"] == "green":
            self.set_row_color(row_position, Qt.green)

    def set_row_color(self, row, color):
        for column in range(self.table.columnCount()):
            self.table.item(row, column).setBackground(color)

    def get_next_id(self):
        if not self.tasks:
            return 1
        else:
            return max(task["id"] for task in self.tasks) + 1

    def complete_task(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            task_ids = set()
            for item in selected_items:
                task_id = int(self.table.item(item.row(), 0).text())
                task_ids.add(task_id)
            for task_id in task_ids:
                task = next(task for task in self.tasks if task["id"] == task_id)
                self.tasks = [task for task in self.tasks if task["id"] != task_id]
                self.completed_tasks.append(task)
            self.save_tasks()
            self.save_completed_tasks()
            self.load_tasks()
            QMessageBox.information(self, "Başarılı", "Görev tamamlandı.")

    def delete_task(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            task_ids = set()
            for item in selected_items:
                task_id = int(self.table.item(item.row(), 0).text())
                task_ids.add(task_id)
            for task_id in task_ids:
                task = next(task for task in self.tasks if task["id"] == task_id)
                self.tasks = [task for task in self.tasks if task["id"] != task_id]
                self.deleted_tasks.append(task)
            self.save_tasks()
            self.save_deleted_tasks()
            self.load_tasks()
            QMessageBox.information(self, "Başarılı", "Görev silindi.")

    def sort_tasks(self):
        criteria = self.sort_combo.currentText()
        if criteria == "Bitiş Zamanı (Yakına)":
            self.tasks.sort(key=lambda x: QDateTime.fromString(x["due_date"], "yyyy-MM-dd HH:mm"))
        elif criteria == "Bitiş Zamanı (Uzağa)":
            self.tasks.sort(key=lambda x: QDateTime.fromString(x["due_date"], "yyyy-MM-dd HH:mm"), reverse=True)
        elif criteria == "Hatırlatma Zamanı (Yakına)":
            self.tasks.sort(key=lambda x: QDateTime.fromString(x["reminder"], "yyyy-MM-dd HH:mm"))
        elif criteria == "Hatırlatma Zamanı (Uzağa)":
            self.tasks.sort(key=lambda x: QDateTime.fromString(x["reminder"], "yyyy-MM-dd HH:mm"), reverse=True)
        elif criteria == "Eklenme Zamanı (Yakına)":
            self.tasks.sort(key=lambda x: x["id"])
        elif criteria == "Eklenme Zamanı (Uzağa)":
            self.tasks.sort(key=lambda x: x["id"], reverse=True)
        elif criteria == "Öncelik":
            priority_map = {"red": 1, "yellow": 2, "green": 3}
            self.tasks.sort(key=lambda x: (priority_map[x["priority"]], QDateTime.fromString(x["due_date"], "yyyy-MM-dd HH:mm")))
        
        self.load_tasks()

    def edit_task(self, row, column):
        task_id = int(self.table.item(row, 0).text())
        task = next((task for task in self.tasks if task["id"] == task_id), None)
        if task:
            dialog = EditTaskDialog(self, task)
            if dialog.exec_() == QDialog.Accepted:
                self.save_tasks()
                self.load_tasks()

    def show_completed_tasks(self):
        self.completed_tasks_dialog = CompletedTasksDialog(self, self.completed_tasks)
        self.completed_tasks_dialog.exec_()

    def update_remaining_times(self):
        current_time = QDateTime.currentDateTime()
        for row in range(self.table.rowCount()):
            due_date_str = self.table.item(row, 4).text()
            due_date = QDateTime.fromString(due_date_str, "yyyy-MM-dd HH:mm")
            remaining_time = current_time.secsTo(due_date)

            days = remaining_time // 86400
            hours = (remaining_time % 86400) // 3600
            minutes = (remaining_time % 3600) // 60
            seconds = remaining_time % 60

            remaining_time_str = f"{days}g {hours}s {minutes}dk {seconds}sn"
            self.table.setItem(row, 5, QTableWidgetItem(remaining_time_str))

            # Hatırlatma zamanı kontrolü
            reminder_time = QDateTime.fromString(self.table.item(row, 3).text(), "yyyy-MM-dd HH:mm")
            if current_time >= reminder_time and not self.table.item(row, 0).text().startswith("R_"):
                self.show_reminder_popup(task=self.tasks[row])
                self.table.setItem(row, 0, QTableWidgetItem("R_" + self.table.item(row, 0).text()))

            # Bitiş zamanı kontrolü
            if current_time >= due_date:
                self.show_due_date_popup(task=self.tasks[row])

    def show_reminder_popup(self, task):
        reminder_popup = QMessageBox(self)
        reminder_popup.setWindowTitle("Hatırlatma")
        reminder_popup.setText(f"Hatırlatma Zamanı: {task['title']}\n\n{task['description']}")
        reminder_popup.setStandardButtons(QMessageBox.Ok)
        reminder_popup.exec_()

    def show_due_date_popup(self, task):
        due_date_popup = QMessageBox(self)
        due_date_popup.setWindowTitle("Bitiş Zamanı Geldi")
        due_date_popup.setText(f"Bitiş Zamanı Geldi: {task['title']}\n\n{task['description']}")
        due_date_popup.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Retry)
        
        ret = due_date_popup.exec_()
        if ret == QMessageBox.Discard:
            self.delete_task_with_id(task["id"])
        elif ret == QMessageBox.Save:
            self.complete_task_with_id(task["id"])
        elif ret == QMessageBox.Retry:
            new_due_date, ok = QInputDialog.getText(self, "Yeni Bitiş Tarihi", "Yeni bitiş tarihini girin (yyyy-MM-dd HH:mm):")
            if ok:
                task["due_date"] = new_due_date
                self.save_tasks()
                self.load_tasks()

    def delete_task_with_id(self, task_id):
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()
        self.load_tasks()

    def complete_task_with_id(self, task_id):
        task = next(task for task in self.tasks if task["id"] == task_id)
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.completed_tasks.append(task)
        self.save_tasks()
        self.save_completed_tasks()
        self.load_tasks()

class EditTaskDialog(QDialog):
    def __init__(self, parent, task):
        super().__init__(parent)

        self.task = task
        self.setWindowTitle("Görevi Düzenle")

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Başlık:")
        self.layout.addWidget(self.title_label, 0, 0)
        self.title_input = QLineEdit(task["title"])
        self.title_input.setMaxLength(50)
        self.layout.addWidget(self.title_input, 0, 1)

        self.desc_label = QLabel("Açıklama:")
        self.layout.addWidget(self.desc_label, 1, 0)
        self.desc_input = QTextEdit(task["description"])
        self.desc_input.setMaximumHeight(50)
        self.layout.addWidget(self.desc_input, 1, 1)

        self.reminder_label = QLabel("Hatırlatma:")
        self.layout.addWidget(self.reminder_label, 2, 0)
        self.reminder_input = QDateTimeEdit(QDateTime.fromString(task["reminder"], "yyyy-MM-dd HH:mm"))
        self.reminder_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.layout.addWidget(self.reminder_input, 2, 1)

        self.due_date_label = QLabel("Bitiş Tarihi:")
        self.layout.addWidget(self.due_date_label, 3, 0)
        self.due_date_input = QDateTimeEdit(QDateTime.fromString(task["due_date"], "yyyy-MM-dd HH:mm"))
        self.due_date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.layout.addWidget(self.due_date_input, 3, 1)

        self.priority_label = QLabel("Öncelik:")
        self.layout.addWidget(self.priority_label, 4, 0)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["red", "yellow", "green"])
        self.priority_input.setCurrentText(task["priority"])
        self.layout.addWidget(self.priority_input, 4, 1)

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_task)
        self.layout.addWidget(self.save_button, 5, 0, 1, 2)

    def save_task(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Hata", "Başlık boş olamaz!")
            return

        self.task["title"] = self.title_input.text()
        self.task["description"] = self.desc_input.toPlainText()
        self.task["reminder"] = self.reminder_input.dateTime().toString("yyyy-MM-dd HH:mm")
        self.task["due_date"] = self.due_date_input.dateTime().toString("yyyy-MM-dd HH:mm")
        self.task["priority"] = self.priority_input.currentText()
        self.accept()

class CompletedTasksDialog(QDialog):
    def __init__(self, parent, completed_tasks):
        super().__init__(parent)

        self.setWindowTitle("Tamamlanan Görevler")
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Başlık", "Açıklama", "Hatırlatma Zamanı", "Bitiş Zamanı"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Bitiş Zamanı (Yakına)", "Bitiş Zamanı (Uzağa)", "Hatırlatma Zamanı (Yakına)", "Hatırlatma Zamanı (Uzağa)", "Eklenme Zamanı (Yakına)", "Eklenme Zamanı (Uzağa)", "Öncelik"])
        self.sort_combo.currentIndexChanged.connect(self.sort_tasks)
        button_layout.addWidget(self.sort_combo)

        self.layout.addLayout(button_layout)

        self.completed_tasks = completed_tasks
        self.load_completed_tasks()

    def load_completed_tasks(self):
        self.table.setRowCount(0)
        for task in self.completed_tasks:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(task["id"])))
            self.table.setItem(row_position, 1, QTableWidgetItem(task["title"]))
            self.table.setItem(row_position, 2, QTableWidgetItem(task["description"]))
            self.table.setItem(row_position, 3, QTableWidgetItem(task["reminder"]))
            self.table.setItem(row_position, 4, QTableWidgetItem(task["due_date"]))

            if task["priority"] == "red":
                self.set_row_color(row_position, Qt.red)
            elif task["priority"] == "yellow":
                self.set_row_color(row_position, Qt.yellow)
            elif task["priority"] == "green":
                self.set_row_color(row_position, Qt.green)

    def set_row_color(self, row, color):
        for column in range(self.table.columnCount()):
            self.table.item(row, column).setBackground(color)

    def sort_tasks(self):
        criteria = self.sort_combo.currentText()
        if criteria == "Bitiş Zamanı (Yakına)":
            self.completed_tasks.sort(key=lambda x: QDateTime.fromString(x["due_date"], "yyyy-MM-dd HH:mm"))
        elif criteria == "Bitiş Zamanı (Uzağa)":
            self.completed_tasks.sort(key=lambda x: QDateTime.fromString(x["due_date"], "yyyy-MM-dd HH:mm"), reverse=True)
        elif criteria == "Hatırlatma Zamanı (Yakına)":
            self.completed_tasks.sort(key=lambda x: QDateTime.fromString(x["reminder"], "yyyy-MM-dd HH:mm"))
        elif criteria == "Hatırlatma Zamanı (Uzağa)":
            self.completed_tasks.sort(key=lambda x: QDateTime.fromString(x["reminder"], "yyyy-MM-dd HH:mm"), reverse=True)
        elif criteria == "Eklenme Zamanı (Yakına)":
            self.completed_tasks.sort(key=lambda x: x["id"])
        elif criteria == "Eklenme Zamanı (Uzağa)":
            self.completed_tasks.sort(key=lambda x: x["id"], reverse=True)
        elif criteria == "Öncelik":
            priority_map = {"red": 1, "yellow": 2, "green": 3}
            self.completed_tasks.sort(key=lambda x: (priority_map[x["priority"]], QDateTime.fromString(x["due_date"], "yyyy-MM-dd HH:mm")))
        
        self.load_completed_tasks()

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.json
    window.add_task_from_api(task)
    return jsonify({"status": "success"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.setDaemon(True)
    flask_thread.start()

    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())
