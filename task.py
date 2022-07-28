import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

class Task(qtw.QLabel):

    def __init__(self, db, db_index):
        self.db = db
        self.id = db_index
        self.db_item = db.get_connection().execute(
            'SELECT * FROM tasks WHERE id=?', [db_index]
        ).fetchone()
        super().__init__(self.db_item['description'])

        self.height = 100

        self.initUI()
    
    def initUI(self):
        self.setFixedHeight(self.height)
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)
        self.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Plain)

        self.remove_button = qtw.QPushButton('Remove', self)
        self.remove_button.clicked.connect(self.remove)
    
    # Remove the task from the list and from the database
    def remove(self):
        self.setParent(None)
        con = self.db.get_connection()
        con.execute('DELETE FROM tasks WHERE id=?', [self.id])
        con.commit()


# Get new task
class taskInput(qtw.QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Add Task')
        
        # The input form
        form = qtw.QFormLayout()
        self.setLayout(form)

        # Get the tasks's description
        self.description = qtw.QLineEdit()

        # Get the deadline
        self.date = qtw.QDateEdit(qtc.QDate.currentDate())
        self.date.setDateRange(qtc.QDate.currentDate(), qtc.QDate.currentDate().addDays(365))
        
        # The dialog's buttons
        self.buttonBox = qtw.QDialogButtonBox(
            qtw.QDialogButtonBox.Save | qtw.QDialogButtonBox.Cancel)
        # Link actions on the button box with the dialog
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        form.addRow('&Description', self.description)
        form.addRow('&Deadline:', self.date)
        form.addWidget(self.buttonBox)