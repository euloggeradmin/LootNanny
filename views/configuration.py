from decimal import Decimal
import os
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QFileDialog, QTextEdit, QFormLayout, QHBoxLayout, QHeaderView, QTabWidget, QCheckBox, QGridLayout, QComboBox, QLineEdit, QLabel, QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem

from data.weapons import ALL_WEAPONS
from data.sights_and_scopes import SIGHTS, SCOPES
from data.attachments import ALL_ATTACHMENTS
from modules.combat import Loadout
from utils.tables import WeaponTable


class ConfigTab(QWidget):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app: "LootNanny" = app

        layout = QVBoxLayout()

        form_inputs = QFormLayout()
        # Add widgets to the layout

        # Chat Location
        self.chat_location_text = QLineEdit(text=self.app.config.location.ui_value)
        form_inputs.addRow("Chat Location:", self.chat_location_text)
        self.chat_location_text.editingFinished.connect(self.onChatLocationChanged)

        btn = QPushButton("Find File")
        form_inputs.addWidget(btn)
        btn.clicked.connect(self.open_files)

        self.character_name = QLineEdit(text=self.app.config.name.ui_value)
        form_inputs.addRow("Character Name:", self.character_name)
        self.character_name.editingFinished.connect(self.onNameChanged)

        self.weapons = WeaponTable({"Name": [], "Amp": [], "Scope": [], "Sight 1": [],
                         "Sight 2": [], "Damage": [], "Accuracy": []}, 25, 7)
        self.weapons.itemClicked.connect(self.weapon_table_selected)
        self.redraw_weapons()
        form_inputs.addRow("Weapons", self.weapons)

        # Other Windows
        self.select_loadout_btn = QPushButton("Select Loadout")
        self.select_loadout_btn.released.connect(self.select_loadout)
        self.select_loadout_btn.hide()
        form_inputs.addWidget(self.select_loadout_btn)

        self.delete_weapon_btn = QPushButton("Delete Loadout")
        self.delete_weapon_btn.released.connect(self.delete_loadout)
        self.delete_weapon_btn.hide()
        form_inputs.addWidget(self.delete_weapon_btn)

        self.add_weapon_btn = QPushButton("Add Weapon Loadout")
        self.add_weapon_btn.released.connect(self.add_new_weapon)
        form_inputs.addWidget(self.add_weapon_btn)

        self.active_loadout = QLineEdit(text="", enabled=False)
        form_inputs.addRow("Active Loadout:", self.active_loadout)

        # Calculated Configuration
        self.ammo_burn_text = QLineEdit(text="0", enabled=False)
        form_inputs.addRow("Ammo Burn:", self.ammo_burn_text)

        self.weapon_decay_text = QLineEdit(text="0.0", enabled=False)
        form_inputs.addRow("Tool Decay:", self.weapon_decay_text)

        # Screenshots
        self.screenshots_enabled = True
        self.screenshot_directory = "~/Documents/Globals/"
        self.screenshot_delay_ms = 500

        self.screenshots_checkbox = QCheckBox()
        self.screenshots_checkbox.setChecked(True)
        form_inputs.addRow("Take Screenshot On global/hof", self.screenshots_checkbox)

        self.screenshots_directory_text = QLineEdit(text=self.app.config.screenshot_directory.ui_value)
        form_inputs.addRow("Screenshot Directory:", self.screenshots_directory_text)
        self.screenshots_directory_text.textChanged.connect(self.update_screenshot_fields)

        self.screenshots_delay = QLineEdit(text=self.app.config.screenshot_delay.ui_value)
        form_inputs.addRow("Screenshot Delay (ms):", self.screenshots_delay)
        self.screenshots_delay.textChanged.connect(self.update_screenshot_fields)

        self.screenshot_threshold = QLineEdit(text=self.app.config.screenshot_threshold.ui_value)
        form_inputs.addRow("Screenshot Threshold (PED):", self.screenshot_threshold)
        self.screenshot_threshold.textChanged.connect(self.update_screenshot_fields)

        self.streamer_window_layout_text = QTextEdit()
        self.streamer_window_layout_text.setText(self.app.config.streamer_layout.ui_value)
        self.streamer_window_layout_text.textChanged.connect(self.set_new_streamer_layout)

        form_inputs.addRow("Streamer Window Layout:", self.streamer_window_layout_text)

        # Set Layout
        layout.addLayout(form_inputs)

        self.setLayout(layout)

        if self.app.config.selected_loadout.value:
            self.active_loadout.setText(self.app.config.selected_loadout.value[0])
            self.recalculateWeaponFields()

        if not os.path.exists(os.path.expanduser(self.screenshot_directory)):
            os.makedirs(os.path.expanduser(self.screenshot_directory))

    def weapon_table_selected(self):
        indexes = self.weapons.selectionModel().selectedRows()
        if not indexes:
            self.delete_weapon_btn.hide()
            self.select_loadout_btn.hide()
            self.selected_index = None
            return

        self.delete_weapon_btn.show()
        self.select_loadout_btn.show()
        self.selected_index = indexes[-1].row()
        self.delete_weapon_btn.setEnabled(True)

    def select_loadout(self):
        self.app.config.selected_loadout = self.app.config.loadouts.value[self.selected_index]
        self.active_loadout.setText(self.app.config.selected_loadout.value[0])
        self.recalculateWeaponFields()

    def delete_loadout(self):
        del self.app.config.loadouts.value[self.selected_index]
        self.app.config.save()
        self.redraw_weapons()

    def loadout_to_data(self):
        d = {"Name": [], "Amp": [], "Scope": [], "Sight 1": [],
                         "Sight 2": [], "Damage": [], "Accuracy": []}
        for loadout in self.app.config.loadouts.value:
            if isinstance(loadout, list):
                loadout = Loadout(*loadout)
            loadout: Loadout
            d["Name"].append(loadout.weapon)
            d["Amp"].append(loadout.amp)
            d["Scope"].append(loadout.scope)
            d["Sight 1"].append(loadout.sight_1)
            d["Sight 2"].append(loadout.sight_2)
            d["Damage"].append(loadout.damage_enh)
            d["Accuracy"].append(loadout.accuracy_enh)
        return d

    def redraw_weapons(self):
        self.weapons.clear()
        self.weapons.setData(self.loadout_to_data())

    def add_new_weapon(self):
        weapon_popout = WeaponPopOut(self)
        if self.app.config.theme == "light":
            self.set_stylesheet(weapon_popout, "light.qss")
        else:
            self.set_stylesheet(weapon_popout, "dark.qss")
        self.add_weapon_btn.setEnabled(False)

    def add_weapon_cancled(self):
        self.add_weapon_btn.setEnabled(True)

    def on_added_weapon(self, weapon: str, amp: str, scope: str, sight_1: str, sight_2: str, d_enh: int, a_enh: int):
        new_loadout = Loadout(weapon, amp, scope, sight_1, sight_2, d_enh, a_enh)
        self.app.config.loadouts.value.append(new_loadout)
        self.app.config.save()
        self.redraw_weapons()

    def update_screenshot_fields(self):
        self.app.config.screenshot_threshold = int(self.screenshot_threshold.text())
        self.app.config.screenshot_delay = int(self.screenshots_delay.text())
        self.app.config.screenshot_directory = self.screenshots_directory_text.text()

    def set_new_streamer_layout(self):
        try:
            self.app.config.streamer_layout = json.loads(self.streamer_window_layout_text.toPlainText())
            self.streamer_window_layout_text.setStyleSheet("color: white;" if self.app.theme == "dark" else "color: black;")
        except:
            self.streamer_window_layout_text.setStyleSheet("color: red;")

    def open_files(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
        self.app.config.location = path[0]
        self.chat_location_text.setText(path[0])
        self.onChatLocationChanged()

    def recalculateWeaponFields(self):
        loadout = Loadout(*self.app.config.selected_loadout.value)
        weapon = ALL_WEAPONS[loadout.weapon]
        amp = ALL_ATTACHMENTS.get(loadout.amp)
        ammo = weapon["ammo"] * (1 + (0.1 * loadout.damage_enh))
        decay = weapon["decay"] * Decimal(1 + (0.1 * loadout.accuracy_enh))
        if amp:
            ammo += amp["ammo"]
            decay += amp["decay"]
        self.ammo_burn_text.setText(str(int(ammo)))
        self.weapon_decay_text.setText("%.6f" % decay)

        scope = SCOPES.get(loadout.scope)
        if scope:
            decay += scope["decay"]
            ammo += scope["ammo"]

        sight_1 = SIGHTS.get(loadout.sight_1)
        if sight_1:
            decay += sight_1["decay"]
            ammo += sight_1["ammo"]

        sight_2 = SIGHTS.get(loadout.sight_2)
        if sight_2:
            decay += sight_2["decay"]
            ammo += sight_2["ammo"]

        self.app.combat_module.decay = decay
        self.app.combat_module.ammo_burn = ammo

        self.app.save_config()
        self.app.combat_module.update_active_run_cost()

    def onNameChanged(self):
        self.app.config.name = self.character_name.text()
        self.app.save_config()

    def onChatLocationChanged(self):
        if "*" in self.chat_location_text.text():
            print("Probably an error trying to resave this value, don't update")
            return
        self.app.config.location = self.chat_location_text.text()


class WeaponPopOut(QWidget):
    def __init__(self, parent: ConfigTab):
        super().__init__()

        self.parent = parent

        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # set the title
        self.setWindowTitle("Add Weapon")

        # setting  the geometry of window
        self.setGeometry(100, 100, 340, 100)


        self.weapon = ""
        self.amp = "Unamped"
        self.scope = "None"
        self.sight_1 = "None"
        self.sight_2 = "None"
        self.damage_enhancers = 0
        self.accuracy_enhancers = 0

        self.layout = self.create_widgets()
        self.resize_to_contents()

        self.show()

    def resize_to_contents(self):
        self.setFixedSize(self.layout.sizeHint())

    def create_widgets(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        form_inputs = QFormLayout()

        # Weapon Configuration
        self.weapon_option = QComboBox()
        self.weapon_option.addItems(sorted(ALL_WEAPONS))
        form_inputs.addRow("Weapon:", self.weapon_option)
        self.weapon_option.currentIndexChanged.connect(self.on_field_changed)

        self.amp_option = QComboBox()
        self.amp_option.addItems(["Unamped"] + sorted(ALL_ATTACHMENTS))
        form_inputs.addRow("Amplifier:", self.amp_option)
        self.amp_option.currentIndexChanged.connect(self.on_field_changed)

        self.scope_option = QComboBox()
        self.scope_option.addItems(["None"] + sorted(SCOPES))
        form_inputs.addRow("Scope:", self.scope_option)
        self.scope_option.currentIndexChanged.connect(self.on_field_changed)

        self.sight_1_option = QComboBox()
        self.sight_1_option.addItems(["None"] + sorted(SIGHTS))
        form_inputs.addRow("Sight 1:", self.sight_1_option)
        self.sight_1_option.currentIndexChanged.connect(self.on_field_changed)

        self.sight_2_option = QComboBox()
        self.sight_2_option.addItems(["None"] + sorted(SIGHTS))
        form_inputs.addRow("Sight 2:", self.sight_2_option)
        self.sight_2_option.currentIndexChanged.connect(self.on_field_changed)

        self.damage_enhancers_txt = QLineEdit(text="0")
        form_inputs.addRow("Damage Enhancers:", self.damage_enhancers_txt)
        self.damage_enhancers_txt.editingFinished.connect(self.on_field_changed)

        self.accuracy_enhancers_txt = QLineEdit(text="0")
        form_inputs.addRow("Accuracy Enhancers:", self.accuracy_enhancers_txt)
        self.accuracy_enhancers_txt.editingFinished.connect(self.on_field_changed)
        layout.addLayout(form_inputs)

        h_layout = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.released.connect(self.cancel)

        confirm = QPushButton("Confirm")
        confirm.released.connect(self.confirm)

        h_layout.addWidget(cancel)
        h_layout.addWidget(confirm)

        layout.addLayout(h_layout)

        layout.addStretch()
        return layout

    def cancel(self):
        self.parent.add_weapon_cancled()
        self.close()

    def confirm(self):
        self.parent.on_added_weapon(
            self.weapon,
            self.amp,
            self.scope,
            self.sight_1,
            self.sight_2,
            self.damage_enhancers,
            self.accuracy_enhancers
        )
        self.close()

    def on_field_changed(self):
        self.scope = self.scope_option.currentText()
        self.sight_1 = self.sight_1_option.currentText()
        self.sight_2 = self.sight_2_option.currentText()
        self.weapon = self.weapon_option.currentText()
        self.amp = self.amp_option.currentText()
        self.damage_enhancers = min(10, int(self.damage_enhancers_txt.text()))
        self.accuracy_enhancers = min(10, int(self.accuracy_enhancers_txt.text()))

        self.damage_enhancers_txt.setText(str(self.damage_enhancers))
        self.accuracy_enhancers_txt.setText(str(self.accuracy_enhancers))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):
        event.accept()  # let the window close
