# -*- coding: utf-8 -*-


import os
import shutil
from uuid import uuid4

from PySide2.QtWidgets import *
from PySide2.QtGui import QFont
from qt_material import QtStyleTools, list_themes
import re


class CustomQST(QtStyleTools):
    def __init__(self):
        super(self).__init__()

    def add_menu_theme(self, parent, menu: QMenu):
        for theme in ['default'] + list_themes():
            action = QAction(parent)
            action.setText(theme.split(".")[0])

            action.triggered.connect(self._wrapper(
                parent, theme, self.extra_colors, self.update_buttons))
            menu.addAction(action)


class CustomListWidgetItem(QListWidgetItem):

    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except:
            return QListWidgetItem().__lt__(other)


class UiMainWindow(QWidget, CustomQST):
    def __init__(self):
        super().__init__()
        # initialize variables
        self.isDataLoaded = False
        self.foldersData = {}
        self.applied_regex = None
        self.opened_folder = ""
        self.hLayout = QHBoxLayout()
        self.hLayout2 = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        self.groupBox = QGroupBox()
        self.groupBox2 = QGroupBox()
        self.gridLayout = QGridLayout()
        self.dw = QDesktopWidget()
        self.regex_input = QLineEdit()
        self.path_input = QLineEdit()
        self.apply_stylesheet(self, "dark_yellow.xml")
        self.init_window_size()
        self.list_view = QListWidget()
        self.regexLabel = QLabel("Enter Regex:")
        self.btn4 = QPushButton("Apply")
        self.enter_path_label = QLabel("Enter Folder Path:")
        self.enter_path_label.setFont(QFont("Times", 12))
        self.menu_bar = QMenuBar()

        self.path_input.setPlaceholderText(r"C:\Users\Erfan\Desktop\Projects")
        self.path_input.setFont(QFont("Times", 11))
        self.path_input.textChanged.connect(self.handle_open_change)

        self.open_path_button = QPushButton("Open")
        self.open_path_button.setFixedSize(100, 60)

        self.btn4.clicked.connect(self.apply)

        self.list_view.setSortingEnabled(True)
        self.list_view.setDragEnabled(True)
        self.list_view.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_view.setGeometry(200, 200, 200, 200)

        self.themes = self.menu_bar.addMenu("themes")
        self.add_menu_theme(self, self.themes)

        self.hLayout.addWidget(self.enter_path_label)
        self.hLayout.addWidget(self.path_input)
        self.hLayout.addWidget(self.open_path_button)

        self.regexLabel.setFont(QFont("Times", 12))

        self.regex_input.setFont(QFont("Times", 11))
        self.regex_input.setPlaceholderText(r"(\d*)")
        self.regex_input.textChanged.connect(self.apply_regex_buttonEnabeldHandel)
        self.apply_regex_button = QPushButton("Apply")
        self.apply_regex_button.setFixedSize(100, 60)
        self.apply_regex_button.clicked.connect(self.apply_regex)
        self.hLayout2.addWidget(self.regexLabel)
        self.hLayout2.addWidget(self.regex_input)
        self.hLayout2.addWidget(self.apply_regex_button)

        self.groupBox.setLayout(self.hLayout)
        self.groupBox2.setLayout(self.hLayout2)

        self.vLayout.addWidget(self.groupBox)
        self.vLayout.addWidget(self.groupBox2)
        self.vLayout.addWidget(self.list_view)
        self.vLayout.addWidget(self.btn4)

        self.open_path_button.clicked.connect(self.open)

        self.gridLayout.addLayout(self.vLayout, 0, 0)
        self.gridLayout.setMenuBar(self.menu_bar)
        self.setLayout(self.gridLayout)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Erfan Folder Renamer')
        self.show()

    def init_window_size(self) -> None:

        self.setMinimumWidth(int(self.dw.width() * 0.6))
        self.setMinimumHeight(int(self.dw.height() * 0.7))

    def regex_change_handel(self, text):
        self.apply_regex_button.setEnabled(text != self.applied_regex)

    def apply_regex(self) -> None:
        if self.isDataLoaded:
            print(self.foldersData)
            pat = self.regex_input.text()
            self.apply_regex_button.setEnabled(False)
            self.applied_regex = pat
            items = [self.list_view.item(i).text() for i in range(self.list_view.count())]
            for e, fol in enumerate(items, start=1):
                newName = re.sub(pat, str(e), fol)
                self.foldersData[fol] = newName
            self.list_view.clear()
            for k in self.foldersData:
                self.list_view.addItem(CustomListWidgetItem(k))

    def apply(self) -> None:
        if self.isDataLoaded:

            last_names = self.foldersData.keys()
            new_names = {}
            for fol in last_names:
                name = str(uuid4())
                shutil.move(os.path.join(self.path_input.text(), str(fol)), os.path.join(self.path_input.text(), name))
                print(os.path.join(self.path_input.text(), str(fol)), " to ",
                      os.path.join(self.path_input.text(), name))
                new_names[name] = self.foldersData[fol]
            for k, v in zip(new_names.keys(), new_names.values()):
                shutil.move(os.path.join(self.path_input.text(), str(k)), os.path.join(self.path_input.text(), str(v)))
                print(os.path.join(self.path_input.text(), str(k)), " to ",
                      os.path.join(self.path_input.text(), str(v)))

            self.list_view.clear()

            for item in os.scandir(self.path_input.text()):
                if item.is_dir and not item.name.startswith('.') and not item.name.startswith('$'):
                    self.list_view.addItem(CustomListWidgetItem(item.name))
            self.list_view.sortItems()
            self.foldersData.clear()

    def open(self) -> None:

        if os.path.exists(self.path_input.text()):
            self.list_view.clear()
            self.applied_regex = None
            self.regex_input.setText("")
            self.open_path_button.setEnabled(False)
            self.opened_folder = self.path_input.text()
            for e, item in enumerate(os.scandir(self.path_input.text()), start=1):
                if item.is_dir and not item.name.startswith('.') and not item.name.startswith('$'):
                    self.foldersData[item.name] = e
                    self.list_view.addItem(CustomListWidgetItem(item.name))
        self.isDataLoaded = True

        self.list_view.sortItems()

    def handle_open_change(self, text):
        self.open_path_button.setEnabled(text != self.opened_folder)


if __name__ == "__main__":
    app = QApplication([])
    UiMainWindow()
    app.exec_()
