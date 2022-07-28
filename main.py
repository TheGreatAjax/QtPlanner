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
        # self.scroll.setWidget(self.tasks)

        # Add new task button
        self.add_button = qtw.QPushButton('Add', self)
        self.add_button.clicked.connect(self.add_task)

        # Set the sidebar containing selector buttons
        self.tasks = qtw.QTabWidget()
        self.tasks.setCornerWidget(self.add_button, qtc.Qt.Corner.BottomRightCorner)
        # self.tasks.setTabPosition(qtw.QTabWidget.TabPosition.West)
    
        # Create tabs
        self.all_tab = qtw.QWidget()
        self.today_tab = qtw.QWidget()
        self.week_tab = qtw.QWidget()
        self.tasks.addTab(self.all_tab, 'All Tasks')
        self.tasks.addTab(self.today_tab, 'Today')
        self.tasks.addTab(self.week_tab, 'Week')

        # Populate tabs
        self.populate(self.all_tab)
        self.populate(self.today_tab,
                     condition='WHERE date=?',
                     parameters=[qtc.QDate.currentDate().toJulianDay()])
        self.populate(self.week_tab,
                     condition='WHERE date<=?',
                     parameters=[qtc.QDate.currentDate().addDays(7).toJulianDay()])

        # Place the sidebar on the left of the main window
        # self.tasksDock = qtw.QDockWidget()
        # self.tasksDock.setWidget(self.tasks)
        # self.addDockWidget(qtc.Qt.LeftDockWidgetArea, self.tasksDock)
        # self.tasks.setMinimumSize(self.width, self.height - 400)
        self.setCentralWidget(self.tasks)



    def populate(self, tab, condition='', parameters=[]):
        tab.layout = qtw.QVBoxLayout()
        tasks = self.db.get_connection().execute(
            'SELECT id FROM tasks ' + condition, parameters
        ).fetchall()
        for task_id in tasks:
            db_task = Task(self.db, task_id['id'])
            tab.layout.addWidget(db_task)
        tab.setLayout(tab.layout)

    def add_task(self):
        dlg = taskInput(self)
        result = dlg.exec_()
        if result == qtw.QDialog.Accepted:
            cur = self.db.get_cursor()
            desc = dlg.description.text()
            date = dlg.date.date().toJulianDay()
            cur.execute(
                'INSERT INTO tasks (description, date) VALUES (?, ?)',
                [desc, date]
            )
            self.db.get_connection().commit()

            # Add the task to the appropriate tabs
            task = Task(self.db, cur.lastrowid)
            today = qtc.QDate.currentDate().toJulianDay()
            tabs = [self.all_tab] # Tabs to which the task belongs
            if date <= today + 7:
                tabs.append(self.week_tab)
            if date == today:
                tabs.append(self.today_tab)
            for tab in tabs:
                tab.layout.addWidget(task)
                tab.setLayout(tab.layout)

def main():
    app = qtw.QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
