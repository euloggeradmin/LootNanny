from PyQt5.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPoint
import sys
from decimal import Decimal


class StreamerWindow(QWidget):
    def __init__(self, app):
        super().__init__()

        self.app = app

        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # set the title
        self.setWindowTitle("Streamer Window")

        # setting  the geometry of window
        self.setGeometry(100, 100, 340, 100)

        self.create_widgets()
        self.set_text_from_data(0, 0.0, 0.0)

        # show all the widgets
        self.oldPos = self.pos()
        self.show()

    def create_widgets(self):

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.perc = QLabel()
        self.perc.setStyleSheet("font-size: 20pt;")
        layout.addWidget(self.perc)

        v_layout = QVBoxLayout()
        self.kills = QLabel()
        self.kills.setStyleSheet("font-size: 12pt;")
        v_layout.addWidget(self.kills)

        self.spend = QLabel()
        self.spend.setStyleSheet("font-size: 12pt;")
        v_layout.addWidget(self.spend)

        self.returns = QLabel()
        self.returns.setStyleSheet("font-size: 12pt;")
        v_layout.addWidget(self.returns)

        layout.addLayout(v_layout)
        layout.addStretch()

    def set_text_from_module(self, combat_module):
        self.set_text_from_data(
            combat_module.active_run.loot_instances,
            combat_module.active_run.total_cost,
            combat_module.active_run.tt_return
        )

    def set_text_from_data(self, loots, cost, returns):
        self.kills.setText(f"Total Kills: {loots:,}")
        self.spend.setText(f"Total Spend: {cost:.2f}")
        self.returns.setText(f"Total Return: {returns:.2f}")
        if cost > 0:
            self.perc.setText("%.2f" % (Decimal(returns) / Decimal(cost) * Decimal(100.0)) + "%")
        else:
            self.perc.setText("0.00%")

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):
        self.app.streamer_window = None
        event.accept()  # let the window close
