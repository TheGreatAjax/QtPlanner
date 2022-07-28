import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

class taskDescription(qtw.QWidget):
    def __init__(self, db_item, parent=None):
        # super().__init__(db_item['description'])
        super().__init__(parent)
        self.layout = qtw.QVBoxLayout()

        # Make the task clickable
        self.main_text = qtw.QPushButton(db_item['description'])
        self.main_text.setStyleSheet('''
            height: 30px;
            padding: 2px;
            background-color: white;
            text-align: left
        ''')
        self.main_text.setCheckable(True)
        self.main_text.clicked.connect(self.toggleDescription)

        # The details which are shown when the task gets clicked
        self.details = qtw.QWidget()
        self.details.layout = qtw.QHBoxLayout()
        
        notes = qtw.QLabel(db_item['notes'])

        info = qtw.QFormLayout()
        info.addRow('&Difficulty: ',
            qtw.QLabel(str(db_item['difficulty'])))
        info.addRow('&Deadline: ',
            qtw.QLabel(qtc.QDate().fromJulianDay(db_item['date']).toString()))

        self.details.layout.addWidget(notes)
        self.details.layout.addLayout(info)
        self.details.setLayout(self.details.layout)

        self.layout.addWidget(self.main_text)
        self.setLayout(self.layout)
    
    def toggleDescription(self, checked):
        if checked:
            self.layout.addWidget(self.details)
        else:
            self.details.setParent(None)
        
        self.setLayout(self.layout)


class Task(qtw.QWidget):

    def __init__(self, db, db_index, tabs):
        self.db = db
        self.id = db_index
        self.tabs = tabs

        self.db_item = db.get_connection().execute(
            'SELECT * FROM tasks WHERE id=?', [db_index]
        ).fetchone()
        super().__init__()
        # super().__init__(self.db_item['description'])
        self.initUI()
    
    def initUI(self):
        # self.setFixedHeight(self.height)
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)

        # Layout:
        # Task | Checkbox or Remove button
        self.layout = qtw.QHBoxLayout()
        self.description = taskDescription(self.db_item, self)
        # self.description = qtw.QLabel(self.db_item['description'])
        # self.description.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Plain)

        # Actions with the task: remove and check out
        self.actions_layout = qtw.QVBoxLayout()

        # Add checkbox
        self.checkBox = qtw.QCheckBox()
        self.checkBox.stateChanged.connect(self.checkout)

        # Add remove button
        self.remove_button = qtw.QPushButton('Remove')
        self.remove_button.clicked.connect(self.remove)
        self.remove_button.setEnabled(False)

        # Put it together
        self.actions_layout.addWidget(self.checkBox)
        self.actions_layout.addWidget(self.remove_button)

        self.layout.addWidget(self.description)
        self.layout.addLayout(self.actions_layout)

        self.layout.setStretch(0, 9)
        self.layout.setStretch(1, 1)

        self.setLayout(self.layout)
    
    def checkout(self, s):
        f = self.description.font()
        if s == qtc.Qt.Checked:
            f.setStrikeOut(True)
            self.remove_button.setEnabled(True)
        else:
            f.setStrikeOut(False)
            self.remove_button.setEnabled(False)
        self.description.setFont(f)
    
    # Remove the task from all tabs it belongs to
    def remove(self):

        # Go through each tab
        for tab in self.tabs:

            # Go through layout and check
            # Whether ids match
            if tab.layout():
                for i in range(tab.layout().count()):
                    item = tab.layout().itemAt(i)

                    # If match, delete the item
                    if item.widget().id == self.id:
                        item = tab.layout().takeAt(i)
                        item.widget().setParent(None)
                        del item
                        break
                
        # Delete from database
        con = self.db.get_connection()
        con.execute('DELETE FROM tasks WHERE id=?', [self.id])
        con.commit()


# Get new task
class taskInput(qtw.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Task')
        self.setFixedSize(400, 200)

        # The input form
        form = qtw.QFormLayout()
        self.setLayout(form)

        # Get the tasks's description and notes
        self.description = qtw.QLineEdit()
        self.notes = qtw.QPlainTextEdit()

        # Get the deadline and difficulty
        self.date = qtw.QDateEdit(qtc.QDate.currentDate())
        self.date.setDateRange(qtc.QDate.currentDate(),
                         qtc.QDate.currentDate().addDays(365))

        self.difficulty = qtw.QSpinBox()
        self.difficulty.setRange(1, 5)

        # The dialog's buttons
        self.buttonBox = qtw.QDialogButtonBox(
            qtw.QDialogButtonBox.Save | qtw.QDialogButtonBox.Cancel)
        # Link actions on the button box with the dialog
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        form.addRow('&Description', self.description)
        form.addRow('&Notes (optional): ', self.notes)
        form.addRow('&Deadline: ', self.date)
        form.addRow('&Task difficulty: ', self.difficulty)
        form.addWidget(self.buttonBox)