from ctypes import alignment
import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from db import Db
from task import Task, taskInput


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 600
        self.setWindowTitle('Planner')

        self.db = Db('tasks.db')
        self.initUI()
    
    def initUI(self):
        self.resize(self.width, self.height)

        # Set the vertical scroll bar
        # self.scroll = qtw.QScrollArea(self)
        # self.scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)
        # self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        # self.scroll.setWidget(self.tabs_widget)

        self.main_widget = qtw.QWidget()
        self.main_layout = qtw.QVBoxLayout()

        self.tabs_widget = qtw.QTabWidget()
    
        # Create tabs
        tab_names = ['All Tasks', 'Today', 'Week']
        self.tabs = dict()
        for name in tab_names:
            tab = self.tabs[name] = qtw.QWidget()
            self.tabs_widget.addTab(tab, name)
            tab.setLayout(qtw.QVBoxLayout())

        # Populate the tabs
        for task_db in self.db.get_connection().execute(
            'SELECT * FROM tasks'
        ).fetchall():
            tabs = Task.tabs_for(task_db, self.tabs)
            for tab in tabs:
                tab.layout().addWidget(Task(
                    self.db, task_db['id'], self.tabs, parent=self.tabs_widget))

        self.actions = qtw.QWidget()
        self.actions_layout = qtw.QHBoxLayout()
        self.actions.setLayout(self.actions_layout)

        # Add new task button
        self.add_button = qtw.QPushButton('Add')
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)

        # Prioritize button
        self.prioritize_button = qtw.QPushButton('Prioritize')
        self.prioritize_button.clicked.connect(self.prioritize)
        self.prioritize_button.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)

        self.actions_layout.addWidget(self.add_button)
        self.actions_layout.addWidget(self.prioritize_button)

        self.main_layout.addWidget(self.tabs_widget, stretch=9)
        self.main_layout.addWidget(self.actions, stretch=1, alignment=qtc.Qt.AlignRight)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    # Adding new task
    def add_task(self):

        # Call the dialog
        dlg = taskInput(parent=self)
        result = dlg.exec_()
        if result == qtw.QDialog.Accepted:

            # Get the task's data
            # and add to database
            cur = self.db.get_cursor()
            desc = dlg.description.text()
            date = dlg.date.date().toJulianDay()
            notes = dlg.notes.toPlainText()
            if not notes:
                notes = '-'
            dif = dlg.difficulty.value()
            cur.execute(
                'INSERT INTO tasks '
                '(description, notes, difficulty, date) '
                'VALUES (?, ?, ?, ?)',
                [desc, notes, dif, date]
            )
            self.db.get_connection().commit()

            # Add the task to appripriate tabs
            tabs = Task.tabs_for(cur.execute(
                'SELECT * FROM tasks WHERE id=?', [cur.lastrowid]
                ).fetchone(), self.tabs)
                
            for tab in tabs:
                tab.layout().addWidget(
                    Task(self.db, cur.lastrowid, self.tabs, parent=self.tabs_widget))
        
    # Prioritize tasks by ~[DIFFICULTY / DEADLINE]
    def prioritize(self):
        
        # Get the current page
        page = self.tabs_widget.currentWidget()
        layout = page.layout()
        tasks = page.children()[1:]

        # Clean the layout
        for t in tasks:
            layout.removeWidget(t)
            
        # Sort the tasks
        tasks.sort(
            key=lambda t: t.db_item['difficulty'] / (t.db_item['date'] - qtc.QDate().currentDate().toJulianDay() + 1),
            reverse=True)
        
        # Add newly sorted tasks
        for t in tasks:
            layout.addWidget(t)

def main():
    app = qtw.QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
