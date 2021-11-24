from PyQt5.QtWidgets import QStatusBar, QFormLayout, QHeaderView, QTabWidget, QCheckBox, QGridLayout, QComboBox, QLineEdit, QLabel, QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QTextStream
import pyqtgraph as pg
import traceback
from datetime import datetime


from utils.tables import *
from modules.combat import CombatModule
from views.configuration import ConfigTab
from chat import ChatReader
from config import CONFIG, save_config
from version import VERSION
from helpers import resource_path
from windows.streamer import StreamerWindow


MAIN_EVENT_LOOP_TICK = 0.1
TICK_COUNTER = 0


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.config = CONFIG

        # Other Windows
        self.streamer_window = None
        self.streamer_window_btn = QPushButton("Show Streamer UI")
        self.streamer_window_btn.released.connect(self.on_toggle_streamer_ui)

        self.setWindowTitle("Loot Nanny")
        self.resize(600, 320)
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Modules
        self.config_tab = ConfigTab(self)

        self.chat_reader = ChatReader(self)
        self.combat_module = CombatModule(self)

        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(self.lootTabUI(), "Loot")
        tabs.addTab(self.analysisTabUI(), "Analysis")
        tabs.addTab(self.skillTabUI(), "Skills")
        tabs.addTab(self.combatTabUI(), "Combat")

        tabs.addTab(self.config_tab, "Config")
        layout.addWidget(tabs)

        statusBar = QStatusBar()

        self.logging_toggle_btn = QPushButton("Start Logging")
        self.logging_toggle_btn.setStyleSheet("background-color: green")
        self.logging_toggle_btn.released.connect(self.on_toggle_logging)

        self.logging_pause_btn = QPushButton("Pause Logging", enabled=False)
        self.logging_pause_btn.setStyleSheet("background-color: grey; color: white;")
        self.logging_pause_btn.released.connect(self.on_pause_logging)

        statusBar.addWidget(QLabel(f"Version: {VERSION}"))

        statusBar.addWidget(self.logging_toggle_btn)
        statusBar.addWidget(self.logging_pause_btn)

        statusBar.addWidget(self.streamer_window_btn)

        self.theme = "dark"
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.clicked.connect(lambda: self.toggle_stylesheet())
        self.theme_btn.setStyleSheet("background-color: white; color: black;")
        statusBar.addWidget(self.theme_btn)

        layout.addWidget(statusBar)

        self.initialize_from_config()

    def initialize_from_config(self):
        if not self.config:
            return

        self.config_tab.load_from_config(self.config)
        self.combat_module.active_weapon = self.config["weapon"]
        self.combat_module.active_amp = self.config["amp"]
        self.combat_module.damage_enhancers = self.config["damage_enhancers"]
        self.combat_module.accuracy_enhancers = self.config["accuracy_enhancers"]
        self.combat_module.active_character = self.config.get("name", "")
        self.config_tab.chat_location_text.setText(self.config.get("location", ""))
        self.config_tab.chat_location = self.config.get("location", "")
        self.config_tab.recalculateWeaponFields()

        self.theme = self.config.get("theme", "dark")
        if self.theme == "light":
            self.set_stylesheet(self, "light.qss")
            self.theme_btn.setStyleSheet("background-color: #222222; color: white;")

    def save_config(self):
        config = {
            "weapon": self.combat_module.active_weapon,
            "amp": self.combat_module.active_amp,
            "damage_enhancers": self.combat_module.damage_enhancers,
            "accuracy_enhancers": self.combat_module.accuracy_enhancers,
            "name": self.combat_module.active_character,
            "location": self.config_tab.chat_location,
            "theme": self.theme,
        }

        save_config(config)

    def on_toggle_streamer_ui(self):
        if self.streamer_window:
            self.streamer_window.close()
            self.streamer_window = None
        else:
            self.streamer_window = StreamerWindow(self)
            if self.theme == "light":
                self.set_stylesheet(self.streamer_window, "light.qss")
            else:
                self.set_stylesheet(self.streamer_window, "dark.qss")

    def on_toggle_logging(self):
        if self.combat_module.is_logging:
            self.combat_module.is_logging = False
            self.combat_module.is_paused = False
            self.combat_module.active_run.time_end = datetime.now()
            self.combat_module.active_run = None
            self.logging_toggle_btn.setStyleSheet("background-color: green")
            self.logging_toggle_btn.setText("Start Logging")
            self.logging_pause_btn.setEnabled(False)
            self.logging_pause_btn.setText("Pause Logging")
            self.logging_pause_btn.setStyleSheet("background-color: grey: color; white;")
        else:
            self.combat_module.is_logging = True
            self.combat_module.is_paused = False
            self.logging_toggle_btn.setStyleSheet("background-color: red")
            self.logging_toggle_btn.setText("Stop Logging")
            self.logging_pause_btn.setEnabled(True)
            self.logging_pause_btn.setText("Pause Logging")
            self.logging_pause_btn.setStyleSheet("background-color: green")

    def on_pause_logging(self):
        if self.combat_module.is_paused:
            self.combat_module.is_paused = False
            self.logging_pause_btn.setStyleSheet("background-color: green")
            self.logging_pause_btn.setText("Pause Logging")
        else:
            self.combat_module.is_paused = True
            self.logging_pause_btn.setStyleSheet("background-color: red")
            self.logging_pause_btn.setText("Unpause Logging")

    def on_tick(self):
        global TICK_COUNTER
        try:
            TICK_COUNTER += 1
            if not TICK_COUNTER % 5:
                TICK_COUNTER %= 5
                self.combat_module.save_runs()

            self.chat_reader.delay_start_reader()

            # Grab all recent lines in the chat and process them incrementally
            all_lines_this_tick = []
            while True:
                line = self.chat_reader.getline()
                if not line or len(all_lines_this_tick) > 5:
                    break
                all_lines_this_tick.append(line)

            self.combat_module.tick(all_lines_this_tick)

        except Exception as e:
            traceback.print_exc()
            print(e)

    def lootTabUI(self):
        """Create the General page UI."""
        generalTab = QWidget()

        layout = QVBoxLayout()

        # Create a QFormLayout instance
        form_inputs = QFormLayout()
        # Add widgets to the layout

        looted_text = QLineEdit(enabled=False)
        form_inputs.addRow("Creatures Looted:", looted_text)

        total_cost_text = QLineEdit(enabled=False)
        form_inputs.addRow("Total Cost:", total_cost_text)

        total_return_text = QLineEdit(enabled=False)
        form_inputs.addRow("Total Return:", total_return_text)

        return_perc_text = QLineEdit(enabled=False)
        form_inputs.addRow("% Return:", return_perc_text)

        globals = QLineEdit(enabled=False)
        form_inputs.addRow("Globals:", globals)

        hofs = QLineEdit(enabled=False)
        form_inputs.addRow("HOFs:", hofs)

        table = LootTableView({"Item": [], "Value": [], "Count": []}, 30, 3)
        runs = RunsView({"Start": [], "End": [], "Spend": [], "Enhancers": [],
                         "Extra Spend": [], "Return": [], "%": []}, 15, 7)

        self.combat_module.loot_table = table
        self.combat_module.runs_table = runs
        self.combat_module.loot_fields = {
            "looted_text": looted_text,
            "total_cost_text": total_cost_text,
            "total_return_text": total_return_text,
            "return_perc_text": return_perc_text,
            "globals": globals,
            "hofs": hofs
        }

        # eulogger.table_view = table
        layout.addLayout(form_inputs)
        layout.addWidget(runs)
        layout.addWidget(table)

        generalTab.setLayout(layout)
        return generalTab

    def analysisTabUI(self):
        analysisTab = QWidget()
        layout = QVBoxLayout()

        return_graph = pg.PlotWidget()
        return_graph.plot([])
        return_graph.setTitle("Run TT Return (%)")
        return_graph.setLabel('left', 'Return (%)')

        multi_graph = pg.PlotWidget()
        multi_graph.plot([])
        multi_graph.setTitle("Cost to kill vs Return")
        multi_graph.setLabel('bottom', 'Cost To Kill (PED)')
        multi_graph.setLabel('left', 'Return (PED)')

        self.combat_module.multiplier_graph = multi_graph
        self.combat_module.return_graph = return_graph
        layout.addWidget(return_graph)
        layout.addWidget(multi_graph)
        analysisTab.setLayout(layout)
        return analysisTab

    def skillTabUI(self):
        """Create the General page UI."""
        skillTab = QWidget()

        layout = QVBoxLayout()

        # Create a QFormLayout instance
        form_inputs = QFormLayout()
        # Add widgets to the layout

        total_skills = QLineEdit(enabled=False)
        form_inputs.addRow("Total Skill Gain:", total_skills)
        # eulogger.total_skills = total_skills

        total_skills_mu = QLineEdit(enabled=False)
        form_inputs.addRow("Total Skill Gain (MU):", total_skills_mu)
        # eulogger.total_skills_mu = total_skills_mu

        table = SkillTableView({"Skill": [], "Value": []}, 10, 2)

        # eulogger.skill_table = table
        layout.addLayout(form_inputs)
        layout.addWidget(table)

        skillTab.setLayout(layout)
        self.combat_module.skill_table = table
        return skillTab

    def combatTabUI(self):
        """Create the Network page UI."""

        combatTab = QWidget()

        layout = QVBoxLayout()

        form_inputs = QFormLayout()

        shots_text = QLineEdit(enabled=False)
        form_inputs.addRow("Shots Fired:", shots_text)

        damage_text = QLineEdit(enabled=False)
        form_inputs.addRow("Total Damage:", damage_text)

        critical_rate = QLineEdit(enabled=False)
        form_inputs.addRow("Critical Chance:", critical_rate)

        miss_rate = QLineEdit(enabled=False)
        form_inputs.addRow("Miss Chance:", miss_rate)

        dpp = QLineEdit(enabled=False)
        form_inputs.addRow("dpp:", dpp)

        table = EnhancerTableView({"Enhancer": [], "Breaks": []}, 10, 2)

        self.combat_module.combat_fields = {
            "attacks": shots_text,
            "damage": damage_text,
            "crits": critical_rate,
            "misses": miss_rate,
            "dpp": dpp,
            "enhancer_table": table
        }
        self.combat_module.enhancer_table = table

        layout.addLayout(form_inputs)
        layout.addWidget(table)

        combatTab.setLayout(layout)
        return combatTab

    def toggle_stylesheet(self):
        '''
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on
        system).

        :path:      A full path to a resource or file on system
        '''
        if self.theme == "light":
            self.theme_btn.setStyleSheet("background-color: #222222; color: white;")
            self.theme = "dark"
            path = "dark.qss"
        else:
            self.theme_btn.setStyleSheet("background-color: white; color: black;")
            self.theme = "light"
            path = "light.qss"

        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        self.set_stylesheet(self, path)

    def set_stylesheet(self, target, path):
        file = QFile(resource_path(path))
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        target.setStyleSheet(stream.readAll())

        self.save_config()


def create_ui():
    app = QApplication([])
    app.setStyle('Fusion')

    window = Window()
    window.set_stylesheet(window, "dark.qss")
    window.show()

    timer = QtCore.QTimer()
    timer.timeout.connect(window.on_tick)
    timer.start(MAIN_EVENT_LOOP_TICK * 1000)

    app.exec()


if __name__ == "__main__":
    create_ui()
