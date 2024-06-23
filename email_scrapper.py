import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar
)
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, urlunparse

class EmailScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.file_label = QLabel('Select Excel File with URLs:')
        layout.addWidget(self.file_label)

        self.file_entry = QLineEdit(self)
        layout.addWidget(self.file_entry)

        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)

        self.scrape_button = QPushButton('Scrape and Save', self)
        self.scrape_button.clicked.connect(self.scrape_and_save)
        layout.addWidget(self.scrape_button)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setWindowTitle('Web Scraper')
        self.setGeometry(300, 300, 400, 200)
        self.show()

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx; *.xls)", options=options)
        if file_path:
            self.file_entry.setText(file_path)

    def validate_and_format_url(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            parsed_url = parsed_url._replace(scheme='http')
        if not parsed_url.netloc:
            parsed_url = parsed_url._replace(netloc=parsed_url.path, path='')
        return urlunparse(parsed_url)

    def scrape_data(self, url):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(url)
            final_url = driver.current_url
            # body_text = driver.find_element(By.TAG_NAME, 'body').text
            body_element = driver.find_element(By.TAG_NAME, 'body')
            body_text = body_element.get_attribute('innerText') if body_element else ""
            if not isinstance(body_text, str):
                body_text = str(body_text)
            # Print the text content to debug
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, body_text)
            print(final_url)
            print(emails)
            # time.sleep(5)
            return final_url, emails
        except Exception as e:
            print(f"Error occurred: {e} - URL: {url}")
            return url, []
        finally:
            driver.quit()

    def save_to_csv(self, all_emails, file_path):
        df = pd.DataFrame(all_emails, columns=["URL", "Email"])
        df.to_csv(file_path, index=False)
        QMessageBox.information(self, 'Success', "Data saved to CSV successfully")

    def scrape_and_save(self): 
        file_path = self.file_entry.text()
        if not file_path:
            QMessageBox.warning(self, 'Error', "Please select an Excel file")
            return
        try:
            urls_df = pd.read_excel(file_path, header=None)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Failed to read the Excel file: {e}")
            return

        # TODO : Remove this filter
        urls_df = urls_df.iloc[0:50]

        all_emails = []
        failed_urls = []
        total_urls = len(urls_df)

        self.progress.setMaximum(total_urls)

        for index, row in urls_df.iterrows():
            raw_url = row[0]
            formatted_url = self.validate_and_format_url(raw_url)
            final_url, emails = self.scrape_data(formatted_url)
            if emails:
                for email in emails:
                    all_emails.append({"URL": final_url, "Email": email})
            else:
                failed_urls.append(final_url)
            self.progress.setValue(index + 1)
            QApplication.processEvents()

        if all_emails:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV files (*.csv)")
            if save_path:
                self.save_to_csv(all_emails, save_path)
        else:
            QMessageBox.information(self, 'No Data', "No email addresses found.")

        if failed_urls:
            failed_urls_str = "\n".join(failed_urls)
            QMessageBox.warning(self, 'Failed URLs', f"Failed to retrieve content from the following URLs:\n{failed_urls_str}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EmailScraperApp()
    sys.exit(app.exec_())
