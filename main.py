import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from database.db import Db
from task import Task, taskInput

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 600
        self.setWindowTitle('Planner')

        self.db = Db()
        self.initUI()
    
    def initUI(self):
        self.resize(self.width, self.height)

        # Set the vertical scroll bar
        # self.scroll = qtw.QScrollArea(self)
        # self.scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)
        # self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        # self.scroll.setWidget(self.tabs_widget)

        # Create the central widget and layout
        self.main_widget = qtw.QWidget()
        self.main_layout = qtw.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Tabs widget holds pages with the tasks
        # organized by category
        self.tabs_widget = qtw.QTabWidget()
    
        # Create tabs
        tab_names = ['All Tasks', 'Today', 'Upcoming 7 days', 
                    'Completed', 'Missed']
        self.tabs = dict()
        for name in tab_names:
            tab = self.tabs[name] = qtw.QWidget()
            self.tabs_widget.addTab(tab, name)
            tab_layout = qtw.QVBoxLayout()
            tab_layout.setSpacing(0)
            tab.setLayout(tab_layout)
        self.active_tab = self.tabs['All Tasks'] # Keep track of the opened tab
        self.tabs_widget.currentChanged.connect(self.cleanupTab)

        # Populate the tabs
        for db_item in self.db.get_connection().execute(
            'SELECT * FROM tasks'
        ).fetchall():

            # Find and add copies of the task
            # to the tabs the task belongs to
            tabs = Task.tabs_for(db_item, self.tabs)
            for tab in tabs:
                tab.layout().addWidget(Task(
                    self.db, db_item['id'], self.tabs, parent=self.tabs_widget))

        # Setup action buttons
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

        # Add widgets to layouts
        self.actions_layout.addWidget(self.add_button)
        self.actions_layout.addWidget(self.prioritize_button)

        self.main_layout.addWidget(self.tabs_widget, stretch=9)
        self.main_layout.addWidget(self.actions, stretch=1, alignment=qtc.Qt.AlignRight)

    def add_task(self):

        # Call the dialog
        dlg = taskInput(parent=self)
        result = dlg.exec_()
        if result == qtw.QDialog.Accepted:

            # Get the task's data
            # and insert into database
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
        # Completed and missed tasks are shown on the bottom
        today = qtc.QDate().currentDate().toJulianDay()
        tasks.sort(
            key=lambda t: (
                t.db_item['difficulty'] * (not t.db_item['completed']) / 
                (t.db_item['date'] - today + 0.5)), # +0.5 so to avoid div by zero 
            reverse=True)
        
        # Add newly sorted tasks
        for t in tasks:
            layout.addWidget(t)
    
    # Close up all open tasks
    def cleanupTab(self):
        tasks = self.active_tab.children()[1:]
        for task in tasks:
            if task.description.toggled:
                task.description.toggleDescription(checked=False)

        self.active_tab = self.tabs_widget.currentWidget()
    

def main():
    app = qtw.QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
