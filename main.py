import os
import sys

import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIntValidator

from arranger import check_format, arrange

room_inputs = {
    'room_no_input': (1, 1000),
    'no_of_benches_input': (1, 200),
    'no_of_rows_input': (1, 200),
    'no_of_columns_input': (1, 200)
}

room_details_map = {
    'room_no_input': 'room_no',
    'no_of_benches_input': 'benches',
    'no_of_rows_input': 'rows',
    'no_of_columns_input': 'columns' 
}


test_rooms_details = [
    {
        'room_no': 1,
        'benches': 45,
        'rows': 10,
        'columns': 5
    },
    {
        'room_no': 2,
        'benches': 61,
        'rows': 10,
        'columns': 7
    },
    {
        'room_no': 3,
        'benches': 50,
        'rows': 10,
        'columns': 5
    }
]

def val(obj):
    return int(obj.text())

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('arrangement.ui', self)
        self.setWindowTitle('Seating Arranger')

        self.csv_files = []
        self.student_details = []
        self.rooms_details = []
        # self.rooms_details = test_rooms_details
        self.status_bar: QStatusBar = self.findChild(QStatusBar, 'status_bar')
        self.tab_widget: QLineEdit = self.findChild(QTabWidget, 'tab_widget')

        self.room_no_input: QLineEdit = self.findChild(QLineEdit, 'room_no_input')
        self.no_of_benches_input: QLineEdit = self.findChild(QLineEdit, 'no_of_benches_input')
        self.no_of_rows_input: QLineEdit = self.findChild(QLineEdit, 'no_of_rows_input')
        self.no_of_columns_input: QLineEdit = self.findChild(QLineEdit, 'no_of_columns_input') 
        self.add_room_button: QPushButton = self.findChild(QPushButton, 'add_room_button')
        self.add_room_button.clicked.connect(self.evt_room_button_clicked)

        self.add_file_button: QPushButton = self.findChild(QPushButton, 'add_file_button')
        self.add_file_button.clicked.connect(self.evt_add_file_button_clicked)

        self.generate_arrangement_button: QPushButton = self.findChild(QPushButton, 'generate_arrangement_button')
        self.generate_arrangement_button.clicked.connect(self.generate_arrangement)
        self.scroll_area: QScrollArea = self.findChild(QScrollArea, 'scroll_area')
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(QVBoxLayout())
        self.scroll_area.setWidget(self.scroll_widget)

        self.init_inputs()

        self.show()

    def init_inputs(self):
        for inp in room_inputs:
            input_field: QLineEdit = getattr(self, inp)
            input_field.setValidator(QIntValidator(*room_inputs[inp]))



    def remove_widgets_of_layout(self, layout):
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)

    def show_dialog(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(message)
        # msg.setInformativeText("This is additional information")
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def evt_room_button_clicked(self):
        room = {}

        for inp in room_inputs:
            limits = room_inputs[inp]
            inp_field: QLineEdit = getattr(self, inp)
            
            if val(inp_field) not in range(limits[0], limits[1]+1):
                field = " ".join(inp.split('_')[:-1])
                # QMessageBox(self, 'Invalid Input', f'Invalid input in {field}').exec_()
                self.show_dialog('Invalid Input', f'Invalid input in {field}')
                inp_field.setText('')
                return

            room[room_details_map[inp]] = val(inp_field)

        if room['rows'] * room['columns'] < room['benches'] or room['rows'] * (room['columns']-1) >= room['benches']:
            # QMessageBox(self, 'Invalid Input', f'Invalid rows and columns').exec_()
            self.show_dialog('Invalid Input', f'Invalid number of rows and columns')            
            return

        for rd in self.rooms_details:
            if rd['room_no'] == room['room_no']:
                self.show_dialog('Info', 'This room number already exists')
                return          

        for inp in room_inputs:
            limits = room_inputs[inp]
            inp_field: QLineEdit = getattr(self, inp)
            inp_field.setText('')

        self.rooms_details.append(room)
        self.status_bar.showMessage('Room added Successfully')


    def evt_add_file_button_clicked(self):
        file_names = QFileDialog.getOpenFileName(self, 'Open the students details CSV file', '', "CSV files (*.csv)")
        file_names = file_names[:-1]
        for file_name in file_names:
            if not file_name: #in case the use cancels during file selection
                return

            message = check_format(file_name)
            if message != 'correct':
                # QMessageBox(self, 'Info', message).exec_()
                self.show_dialog('Info', message)
                return
        
        for file_name in file_names:
            temp_df = pd.read_csv(file_name)

            for sd in self.student_details:
                dep = temp_df['roll number'][0][:2]
                if sd['roll number'][0][:2] == dep:
                    self.show_dialog('Info', f'{dep}\'s csv already added')
                    break
            else:
                file = os.path.split(file_name)[1]
                self.show_dialog('Success!', f'File {file} added successfully!')
                self.student_details.append(temp_df)

        

    def generate_arrangement(self):
        arrangement = []
        if self.rooms_details:
            self.rooms_details.sort(key=lambda r:r['room_no'])
            arrangement = arrange(self.student_details, self.rooms_details)
            if not arrangement:
                self.show_dialog('Info', 'Insuficiant Benches')
                return
        
        
        sc_layout = self.scroll_widget.layout()
        self.remove_widgets_of_layout(sc_layout)
        for i, room in enumerate(arrangement):
            frame = QFrame(self)
            vertical = QSizePolicy.Fixed
            horizontal = QSizePolicy.Expanding
            frame.setSizePolicy(horizontal, vertical)
            frame.setMinimumHeight(563)
            
            label = QLabel(self)
            rm_no = self.rooms_details[i]['room_no'] 
            label.setText(f'room: {rm_no}')

            table = QTableWidget(self)
            table.setRowCount(len(room))
            table.setColumnCount(len(room.columns))
            hor_labels = list(map(str, map(lambda c: c+1, room.columns)))
            ver_labels = list(map(str, map(lambda r: r+1, range(len(room)))))
            table.setHorizontalHeaderLabels(hor_labels)
            table.setVerticalHeaderLabels(ver_labels)
            
            for c, col in enumerate(room.columns):
                for r, bench in enumerate(room[col]):
                    table.setItem(r, c, QTableWidgetItem(str(bench)))

            f_layout = QVBoxLayout()
            f_layout.addWidget(label)
            f_layout.addWidget(table)

            frame.setLayout(f_layout)
            sc_layout.addWidget(frame)

        

            
        

if __name__ == '__main__':
	app = QApplication(sys.argv)

	window = MainWindow()
	
	sys.exit(app.exec_())