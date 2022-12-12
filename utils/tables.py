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

        self.clipboard = QApplication.clipboard()
        self.clipboard.clear()

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

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        # If table cells are copied via CTRL+C, we should copy them to the clipboard
        # in a format that is readable via most spreadsheets ( tab deliniated )
        if event.key() == QtCore.Qt.Key_C and (event.modifiers() & QtCore.Qt.ControlModifier):
            clipdata = []
            rowdata = []
            selected_rows = set([])
            current_row = None
            
            # Get a list of selected rows
            for index in self.selectedIndexes():
                selected_rows.add(index.row())
            
            # Append the headers
            for header in self.COLUMNS:
                rowdata.append(header)
            clipdata.append('\t'.join(rowdata))
            rowdata = []

            # Add all cells from the selected rows to the copy data
            # Note: We can't just loop through selectedIndexes because 
            # QAbstractItemView.SelectRows does not select empty cells
            for row in selected_rows:
                i = 0
                while i <= len(self.COLUMNS):
                    try:
                        cell_data = self.item(row,i).text()
                    except:
                        cell_data = ""
                    rowdata.append(cell_data)
                    i += 1
                clipdata.append('\t'.join(rowdata))
                rowdata = []

            # Add the data to the clipboard
            self.clipboard.setText('\r\n'.join(clipdata))


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

        self.setSelectionBehavior(QAbstractItemView.SelectRows)


class EnhancerTableView(BaseTableView):
    COLUMNS = ("Enhancer", "Breaks")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)


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


class CraftingTableView(BaseTableView):
    COLUMNS = ("Resource", "Per Click", "Total", "TT Cost", "Markup", "Total Cost")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
