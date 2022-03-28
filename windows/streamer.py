from PyQt5.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPoint
from enum import Enum
from typing import Dict, List
from collections import defaultdict

import sys
from decimal import Decimal


class LayoutValue(str, Enum):
    PERCENTAGE_RETURN = "PERCENTAGE_RETURN"
    PERCENTAGE_RETURN_MU = "PERCENTAGE_RETURN_MU"
    TOTAL_LOOTS = "TOTAL_LOOTS"
    TOTAL_SPEND = "TOTAL_SPEND"
    TT_RETURN = "TT_RETURN"
    TOTAL_RETURN = "TOTAL_RETURN"
    PROFIT = "PROFIT"
    TT_PROFIT = "TT_PROFIT"
    DPP = "DPP"
    GLOBALS = "GLOBALS"
    HOFS = "HOFS"


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

        self.widget_mappings: Dict[LayoutValue, QWidget] = defaultdict(lambda: [])
        self.layout = self.create_widgets()
        self.set_text_from_data(0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0)
        self.resize_to_contents()

        # show all the widgets
        self.oldPos = self.pos()

        self.show()

    def resize_to_contents(self):
         self.setFixedSize(self.layout.sizeHint())

    def create_widgets(self):
        """
        Layout is specified as json:

        layout = {
            "layout": [
                [
                    ["{}%", "PERCENTAGE_RETURN", "font-size: 20pt;]
                ],
                [
                    ["Total Loots: {}", "TOTAL_LOOTS"],
                    ["Total Spend: {} PED", "TOTAL_SPEND"],
                    ["Total Return: {} PED", "TOTAL_RETURN"]
                ]
            ],
            "style": "color: red; font-size: 12pt;"
        }
        """
        layout = QHBoxLayout()
        self.setLayout(layout)

        for column in self.app.config.streamer_layout.value["layout"]:

            # Create a new column layout and add it to the horizontal box
            column_layout = QVBoxLayout()
            layout.addLayout(column_layout)

            for column_fields in column:
                if len(column_fields) == 3:
                    this_style = column_fields[2]
                else:
                    this_style = ""
                value_type = LayoutValue(column_fields[1])
                format_str = column_fields[0]

                this_label = QLabel()
                this_label.setStyleSheet(self.app.config.streamer_layout.value.get("style", "") + this_style)
                column_layout.addWidget(this_label)

                self.widget_mappings[value_type].append((format_str, this_label))

        layout.addStretch()
        return layout

    def set_text_from_module(self, combat_module: "CombatModule"):
        self.set_text_from_data(
            combat_module.active_run.loot_instances,
            combat_module.active_run.total_cost + combat_module.active_run.extra_spend,
            combat_module.active_run.tt_return,
            combat_module.active_run.hofs,
            combat_module.active_run.globals,
            combat_module.active_run.dpp,
            combat_module.active_run.total_return_mu,
            combat_module.active_run.total_return_mu_perc,
            combat_module.active_run.total_return_mu - (combat_module.active_run.total_cost - combat_module.active_run.extra_spend)
        )

    def set_text_from_data(self, loots, cost, returns, hofs, globals, dpp, total_returns, total_return_mu_perc, profit):
        data = {
            LayoutValue.DPP: f"{dpp:.4f}",
            LayoutValue.GLOBALS: f"{globals:,}",
            LayoutValue.HOFS: f"{hofs:,}",
            LayoutValue.TOTAL_LOOTS: f"{loots:,}",
            LayoutValue.TT_RETURN: f"{returns:.2f}",
            LayoutValue.TOTAL_SPEND: f"{cost:.2f}",
            LayoutValue.TT_PROFIT: f"{returns - cost:.2f}",
            LayoutValue.TOTAL_RETURN: f"{total_returns:.2f}",
            LayoutValue.PROFIT: f"{profit:.2f}"
        }
        if cost > 0:
            data[LayoutValue.PERCENTAGE_RETURN] = "%.2f" % (Decimal(returns) / Decimal(cost) * Decimal(100.0))
            data[LayoutValue.PERCENTAGE_RETURN_MU] = "%.2f" % total_return_mu_perc
        else:
            data[LayoutValue.PERCENTAGE_RETURN] = "0.00"
            data[LayoutValue.PERCENTAGE_RETURN_MU] = "0.00"

        for data_type, widget_data in self.widget_mappings.items():
            for format_str, widget in widget_data:
                widget.setText(format_str.format(data[data_type]))

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
