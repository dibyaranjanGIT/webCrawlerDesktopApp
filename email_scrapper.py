import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class EmailScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.url_label = QLabel('Enter URL:')
        layout.addWidget(self.url_label)

        self.url_entry = QLineEdit(self)
        layout.addWidget(self.url_entry)

        self.scrape_button = QPushButton('Scrape and Save', self)
        self.scrape_button.clicked.connect(self.scrape_and_save)
        layout.addWidget(self.scrape_button)

        self.setLayout(layout)
        self.setWindowTitle('Web Scraper')
        self.setGeometry(300, 300, 400, 200)
        self.show()

    def scrape_data(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, text)
            return emails
        else:
            QMessageBox.critical(self, 'Error', f"Failed to retrieve content from {url}")
            return []

    def save_to_csv(self, emails, file_path):
        df = pd.DataFrame(emails, columns=["Email"])
        df.to_csv(file_path, index=False)
        QMessageBox.information(self, 'Success', "Data saved to CSV successfully")

    def scrape_and_save(self):
        url = self.url_entry.text()
        if not url:
            QMessageBox.warning(self, 'Error', "Please enter a URL")
            return

        emails = self.scrape_data(url)
        if emails:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV files (*.csv)")
            if file_path:
                self.save_to_csv(emails, file_path)
        else:
            QMessageBox.information(self, 'No Data', "No email addresses found.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EmailScraperApp()
    sys.exit(app.exec_())
