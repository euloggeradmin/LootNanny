from PyQt5.QtWidgets import QAbstractItemView, QFormLayout, QHeaderView, QTabWidget, QCheckBox, QGridLayout, QComboBox, QLineEdit, QLabel, QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore


class BaseTableView(QTableWidget):
    COLUMNS = ("Item", "Count", "Value")

    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData(self.data)
        self.resizeColumnsToContents()

        self.resizeRowsToContents()

    def setData(self, data):
        self.data = data
        horHeaders = []
        for n, key in enumerate(self.COLUMNS):
            horHeaders.append(key)
            if key in data:
                for m, item in enumerate(data[key]):
                    newitem = QTableWidgetItem(str(item))
                    self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)


class RunsView(BaseTableView):
    COLUMNS = ("Notes", "Start", "End", "Spend", "Enhancers", "Extra Spend", "Return", "%", "mu%")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)


class LootTableView(BaseTableView):
    COLUMNS = ("Item", "Count", "Value", "Markup", "Total Value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)


class SkillTableView(BaseTableView):
    COLUMNS = ("Skill", "Value", "Procs", "Proc %")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)


class EnhancerTableView(BaseTableView):
    COLUMNS = ("Enhancer", "Breaks")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)


class WeaponTable(BaseTableView):
    COLUMNS = ("Name", "Amp", "Scope", "Sight 1", "Sight 2", "Damage", "Accuracy")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.cellChanged.connect(self.onCellChanged)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
