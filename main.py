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

        # The widget holding all the currently selected tasks
        self.tasks = qtw.QFrame(self)

        # Set the layout
        self.tasks_layout = qtw.QVBoxLayout()
        self.show_all()
        # tasks = self.db.get_connection().execute(
        #     'SELECT id FROM tasks',
        # ).fetchall()
        # for task_id in tasks:
        #     db_task = Task(self.db, task_id['id'])
        #     self.tasks_layout.addWidget(db_task)
        self.tasks.setLayout(self.tasks_layout)

        # Set the vertical scroll bar
        self.scroll = qtw.QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.tasks)

        # Set the sidebar containing selector buttons
        self.sidebar = qtw.QWidget()
        self.sidebar_layout = qtw.QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)

        # Show all tasks button
        self.all_button = qtw.QPushButton('All tasks', self)
        self.all_button.setCheckable(True)
        self.all_button.clicked.connect(self.show_all)
        self.sidebar_layout.addWidget(self.all_button)

        # Show today's tasks button
        self.today_button = qtw.QPushButton('Today', self)
        self.today_button.setCheckable(True)
        self.today_button.clicked.connect(self.show_today)
        self.sidebar_layout.addWidget(self.today_button)

        # Place the sidebar on the left of the main window
        self.sidebarDock = qtw.QDockWidget()
        self.sidebarDock.setWidget(self.sidebar)
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, self.sidebarDock)

        # Add new task button
        self.add_button = qtw.QPushButton('Add', self)
        self.add_button.clicked.connect(self.add_task)

        self.setCentralWidget(self.tasks)


    def add_task(self):
        dlg = taskInput(self)
        result = dlg.exec_()
        if result == qtw.QDialog.Accepted:
            cur = self.db.get_cursor()
            cur.execute(
                'INSERT INTO tasks (description, date) VALUES (?, ?)',
                [dlg.description.text(),
                 dlg.date.date().toJulianDay()]
            )
            self.db.get_connection().commit()
            self.tasks_layout.addWidget(Task(self.db, cur.lastrowid))
    
    # Remove all currently displayed tasks
    def clean_tasks(self):
        for i in reversed(range(self.tasks_layout.count())): 
            self.tasks_layout.itemAt(i).widget().setParent(None)

    def show_all(self):
        self.show_tasks()

    def show_today(self):
        self.show_tasks(
            condition='WHERE date=?',
            parameters=[qtc.QDate.currentDate().toJulianDay()])
        
    # Get tasks from database with specified condition
    def show_tasks(self, condition='', parameters=[]):

        self.clean_tasks()

        tasks = self.db.get_connection().execute(
            'SELECT id FROM tasks ' + condition, parameters
        ).fetchall()
        for task_id in tasks:
            db_task = Task(self.db, task_id['id'])
            self.tasks_layout.addWidget(db_task)

def main():
    app = qtw.QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
