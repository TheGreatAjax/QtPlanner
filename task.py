import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

# Class holding a task's description
# and also details which can be shown by click
class taskDescription(qtw.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db_item = parent.db_item

        self.initUI()
    
    def initUI(self):

        self.main_layout = qtw.QVBoxLayout()

        # Make the task clickable
        db_item = self.parent.db_item
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
        self.details.setStyleSheet('''
            max-height: 100px;
            background-color: white;
        ''')
        self.details_layout = qtw.QHBoxLayout()
        self.details.setLayout(self.details_layout)

        # Add the notes
        notes = qtw.QPlainTextEdit(db_item['notes'])
        notes.setStyleSheet('''
            border: 1px solid black;
        ''')
        notes.setReadOnly(True)

        # Add info: difficulty and deadline
        info = qtw.QFormLayout()
        info.addRow('&Difficulty: ',
            qtw.QLabel(str(db_item['difficulty'])))
        info.addRow('&Deadline: ',
            qtw.QLabel(qtc.QDate().fromJulianDay(db_item['date']).toString()))

        # Modify task button
        modify_button = qtw.QPushButton('Modify')
        modify_button.clicked.connect(self.parent.modify)
        info.addRow(modify_button)
        modify_button.setSizePolicy(qtw.QSizePolicy.Fixed,
                                 qtw.QSizePolicy.Fixed)

        # Add widgets to the layouts
        self.details_layout.addWidget(notes)
        self.details_layout.addLayout(info)

        self.main_layout.addWidget(self.main_text)
        self.setLayout(self.main_layout)
    
    # Toggle between showing and hiding the detailes
    def toggleDescription(self, checked):

        if checked:
            self.layout().addWidget(self.details)
        else:
            self.details.setParent(None)

class Task(qtw.QWidget):

   # Get appropriate tabs for a task
    def tabs_for(db_item, all_tabs):

        tabs = [all_tabs['All Tasks']] # The tabs
        date = db_item['date']
        today = qtc.QDate.currentDate().toJulianDay()
        if date < today and not db_item['completed']:
            tabs.append(all_tabs['Missed'])
        else:
            if date <= today + 7:
                tabs.append(all_tabs['Upcoming 7 days'])
            if date == today:
                tabs.append(all_tabs['Today'])
            if db_item['Completed']:
                tabs.append(all_tabs['Completed'])

        return tabs

    # Find index of the task with id in the layout
    # return -1 if not found    
    def getAt(id, layout):

        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget().id == id:
                    return i
        return -1
    
    def __init__(self, db, db_index, all_tabs, parent=None):

        self.parent = parent
        super().__init__(self.parent)
        self.db = db
        self.id = db_index
        self.all_tabs = all_tabs # All possible tabs 
                                 #(save for modification)
        self.db_item = db.get_connection().execute(
            'SELECT * FROM tasks WHERE id=?', [db_index]
        ).fetchone()

        # Tabs the task belongs to
        self.tabs = Task.tabs_for(self.db_item, self.all_tabs)

        self.initUI()
    
    def initUI(self):

        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)

        # Layout:
        # | Task Description | Checkbox + Remove button |
        self.main_layout = qtw.QHBoxLayout()
        self.setLayout(self.main_layout)

        # The task's description
        self.description = taskDescription(parent=self)

        # Actions with the task: remove and check out
        self.actions_layout = qtw.QVBoxLayout()

        # Add checkbox
        self.checkBox = qtw.QCheckBox()
        self.checkBox.stateChanged.connect(self.checkout)

        # Add remove button
        self.remove_button = qtw.QPushButton('Remove')
        self.remove_button.clicked.connect(self.remove)
        self.remove_button.setEnabled(False)

        # Put items to layouts
        self.actions_layout.addWidget(self.checkBox)
        self.actions_layout.addWidget(self.remove_button)

        self.main_layout.addWidget(self.description, stretch=9)
        self.main_layout.addLayout(self.actions_layout, stretch=1)

        # Set checkout state
        if self.db_item['completed']:
            self.__checkoutUtil(2)
        
        # The task was missed: disable the checkbox
        elif self.all_tabs['Missed'] in self.tabs:
            self.checkBox.setEnabled(False)
            self.remove_button.setEnabled(True)
    
    # Set the relevant graphics for checked/unchecked task
    def __checkoutUtil(self, s):
        f = self.description.main_text.font()
        if s == qtc.Qt.Checked:
            f.setStrikeOut(True)
            self.remove_button.setEnabled(True)
        else:
            f.setStrikeOut(False)
            self.remove_button.setEnabled(False)
        
        # Disconnect temporarily so to avoid infinite recursion
        self.checkBox.stateChanged.disconnect(self.checkout)
        self.checkBox.setCheckState(s)
        self.checkBox.stateChanged.connect(self.checkout)
        self.description.main_text.setFont(f)

    # Mark the task as completed on all tabs
    def checkout(self, s):

        # Update the database
        con = self.db.get_connection()
        con.execute(
            'UPDATE tasks SET completed=? WHERE id=?',
            [int(s), self.id]
        )
        con.commit()

        # Remove the task from Completed tab if was uncheked
        # and add to it otherwise
        completed = self.all_tabs['Completed']

        # Remove
        if completed in self.tabs:
            index = Task.getAt(self.id, completed.layout())
            item = completed.layout().takeAt(index)
            item.widget().setParent(None)
            del item
            self.tabs.remove(completed)
        
        # Add
        else:
            completed.layout().addWidget(Task(
                self.db, self.id, self.all_tabs, self.parent
            ))
            self.tabs.append(completed)
        
        # Mark as completed on each tab
        for tab in self.tabs:
            layout = tab.layout()
            index = Task.getAt(self.id, layout)
            layout.itemAt(index).widget().__checkoutUtil(s)
    
    # Remove the task from all tabs it belongs to
    def remove(self):

        # Go through each tab
        for tab in self.tabs:
            # If belongs to the tab, delete it
            index = Task.getAt(self.id, tab.layout())
            if index != -1:
                item = tab.layout().takeAt(index)
                item.widget().setParent(None)
                del item
                
        # Delete from the database
        con = self.db.get_connection()
        con.execute('DELETE FROM tasks WHERE id=?', [self.id])
        con.commit()
    
    # Modify the task
    def modify(self):

        dlg = taskInput(task_item=self.db_item, parent=self.parent)
        result = dlg.exec_()
        if result == qtw.QDialog.Accepted:

            # Get the task's data
            # and update the database
            cur = self.db.get_cursor()
            desc = dlg.description.text()
            date = dlg.date.date().toJulianDay()
            notes = dlg.notes.toPlainText()
            if not notes:
                notes = '-'
            dif = dlg.difficulty.value()
            cur.execute(
                'UPDATE tasks SET '
                'description=?, notes=?, difficulty=?, date=? '
                'WHERE id=?', 
                [desc, notes, dif, date, self.id]
            )
            self.db.get_connection().commit()
            self.db_item = cur.execute(
                'SELECT * FROM tasks WHERE id=?', [self.id]
            ).fetchone()

            # Modify the item in all tabs
            belonged = [tab for tab in self.tabs] # Tabs the tasks belonged to
            self.tabs = Task.tabs_for(self.db_item, self.all_tabs) # New tabs 

            for tab in set(belonged + self.tabs):
                index = Task.getAt(self.id, tab.layout())

                # The task was found in the tab
                # Then it belonged to the tab
                if index != -1:
                    item = tab.layout().takeAt(index)
                    item.widget().setParent(None)
                    del item

                    # Replace with modifief version
                    # if it stil belongs to the tab
                    if tab in self.tabs:
                        modified = Task(
                            self.db, self.id, self.all_tabs, self.parent
                        )
                        tab.layout().insertWidget(index, modified)

                # Else it belongs to a new tab             
                else:
                    tab.layout().addWidget(Task(
                        self.db, self.id, self.all_tabs, self.parent
                    ))   

# Dialog for getting new task or modifying one
class taskInput(qtw.QDialog):

    def __init__(self, task_item=None, parent=None):

        super().__init__(parent)
        self.setFixedSize(400, 200)

        # The input form
        form = qtw.QFormLayout()
        self.setLayout(form)

        # Get the tasks's description and notes
        self.description = qtw.QLineEdit()
        self.notes = qtw.QPlainTextEdit()

        # Get the deadline and difficulty
        self.date = qtw.QDateEdit()
        self.date.setDateRange(qtc.QDate.currentDate(),
                         qtc.QDate.currentDate().addDays(365))

        self.difficulty = qtw.QSpinBox()
        self.difficulty.setRange(1, 5)

        # Fill the fields if modifying existing task
        if task_item is not None:
            self.description.setText(task_item['description'])
            self.notes.setPlainText(task_item['notes'])
            self.date.setDate(qtc.QDate().fromJulianDay(task_item['date']))
            self.difficulty.setValue(task_item['difficulty'])
            self.setWindowTitle('Modify task')
        else:
            self.date.setDate(qtc.QDate.currentDate())
            self.setWindowTitle('Add Task')

        # The dialog's buttons
        self.buttonBox = qtw.QDialogButtonBox(
            qtw.QDialogButtonBox.Save | qtw.QDialogButtonBox.Cancel)

        # Link actions on the button box with the dialog
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Fill the form
        form.addRow('&Description', self.description)
        form.addRow('&Notes (optional): ', self.notes)
        form.addRow('&Deadline: ', self.date)
        form.addRow('&Task difficulty: ', self.difficulty)
        form.addWidget(self.buttonBox)