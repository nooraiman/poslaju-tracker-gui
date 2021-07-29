from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
import requests, sys
from bs4 import BeautifulSoup as BS

class PLTracker(QDialog):
    def __init__(self):
        super(PLTracker, self).__init__()
        loadUi("PL Tracker.ui", self)

        # Tables
        self.tblTracking.setColumnWidth(0,170)
        self.tblTracking.setColumnWidth(1,250)
        self.tblTracking.setColumnWidth(2,300)

        # Handles Button Track and Call Track
        self.btnTrack.clicked.connect(self.Track)


    def formatPL(self, tr):
        status = False
        length = 2
        los = []
        for i in range(0, len(tr), length):
            los.append(tr[i:length])
        

        if len(tr) == 14 and los[0] in ['EE','EH','EP','ER','EN','EM','PL']:
            status = True
        else: 
            status = False

        return status

    def loadTracking(self):
        url = "https://sendparcel.poslaju.com.my/open/trace"
        tracking = self.inTracking.text()
        payload = {"tno":tracking}
        header = {
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
        

        res = requests.get(url,payload, headers = header)
        html_data = res.content

        # Get Table Row and Columns
        table_data = [[cell.text for cell in row("td")]
            for row in BS(html_data, features="lxml")("tr")]

        curRow = 0
        self.tblTracking.setRowCount(len(table_data))

        print(table_data)
        if len(table_data) > 0 and table_data[1][1] != "No record found":
            del table_data[0] # Remove First Item - Contain Nothing

            for date,status,place in table_data:
                self.tblTracking.setItem(curRow, 0, QTableWidgetItem(date))
                self.tblTracking.setItem(curRow, 1, QTableWidgetItem(place))
                self.tblTracking.setItem(curRow, 2, QTableWidgetItem(status))
                curRow += 1
        else:
            al = QMessageBox(self)
            al.setText("Tracking Not Found!")
            al.setWindowTitle("Warning!")
            al.show()

    def StopSpam(self):            
        QTimer.singleShot(5000, lambda: self.btnTrack.setDisabled(False))

    def Track(self):
        al = QMessageBox(self)
        
        tmp = self.inTracking.text()
        if tmp == "":
            al.setText("Tracking Number is Empty!")
            al.setWindowTitle("Warning!")
            al.show()
        elif self.formatPL(tmp) == False:
            al.setText("Tracking Number Format is Invalid!")
            al.setWindowTitle("Warning!")
            al.show()
        else:
            if (requests.get("https://sendparcel.poslaju.com.my/open/trace")).status_code == 200:
                # Clear Table
                for i in reversed(range(self.tblTracking.rowCount())):
                    self.tblTracking.removeRow(i)

                self.StopSpam()
                self.loadTracking()
            else:
                print("Poslaju Server is Unreachable!")



app = QApplication(sys.argv)
win = PLTracker()
win.show()
sys.exit(app.exec_())
