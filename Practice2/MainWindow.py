from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from AddDataWindow import AddDataWindow
from EditDataWindow import EditDataWindow
from db import Database

PEOPLE_HEADERS = [
    "ID",
    "Фамилия",
    "Имя",
    "Отчество",
    "Улица",
    "Дом",
    "Корп.",
    "Кв.",
    "Телефон",
]


class MyWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._lookups = {}
        self._add_window = None
        self._editData_window = None
        self._people_view = True
        self.initUI()
        self.load_lookups()
        self.refresh_table()

    def initUI(self):
        self.setWindowTitle("Люди")
        self.resize(960, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        filter_row = QHBoxLayout()
        self.combo_fam = self._make_filter_combo("Фамилия")
        self.combo_nam = self._make_filter_combo("Имя")
        self.combo_otc = self._make_filter_combo("Отчество")
        self.combo_street = self._make_filter_combo("Улица")
        self.home_combo = QLineEdit(self)
        self.home_combo.setPlaceholderText("№ Дома")
        self.telef_combo = QLineEdit(self)
        self.telef_combo.setPlaceholderText("Телефон")
        for filter in (
            self.combo_fam,
            self.combo_nam,
            self.combo_otc,
            self.combo_street,
        ):
            filter_row.addWidget(filter["box"])
        filter_row.addWidget(self.home_combo)
        filter_row.addWidget(self.telef_combo)


        layout.addLayout(filter_row)

        buttons_row = QHBoxLayout()
        self.btn_add = QPushButton("Добавить данные…", self)
        self.btn_add.clicked.connect(self.open_add_window)
        self.btn_edit = QPushButton("Изменить данные…", self)
        self.btn_edit.clicked.connect(self.open_edit_window)
        self.btn_filter = QPushButton("Применить фильтр", self)
        self.btn_filter.clicked.connect(self.refresh_table)
        self.btn_reset = QPushButton("Сбросить", self)
        self.btn_reset.clicked.connect(self.reset_filters)
        self.btn_delete_filter = QPushButton("Удалить по фильтру", self)
        self.btn_delete_filter.clicked.connect(self.delete_by_filter)
        self.btn_delete_selected = QPushButton("Удалить выбранные", self)
        self.btn_delete_selected.clicked.connect(self.delete_selected)
        self.btn_refresh = QPushButton("Обновить", self)
        self.btn_refresh.clicked.connect(self.refresh_table)

        for btn in (
            self.btn_add,
            self.btn_edit,
            self.btn_filter,
            self.btn_reset,
            self.btn_delete_filter,
            self.btn_delete_selected,
            self.btn_refresh,
        ):
            buttons_row.addWidget(btn)
        layout.addLayout(buttons_row)

        sql_row = QHBoxLayout()
        self.sql_input = QLineEdit(self)
        self.sql_input.setPlaceholderText("SQL-запрос (SELECT, INSERT, …)")
        self.btn_sql = QPushButton("Выполнить SQL", self)
        self.btn_sql.clicked.connect(self.run_sql)
        sql_row.addWidget(self.sql_input, stretch=1)
        sql_row.addWidget(self.btn_sql)
        layout.addLayout(sql_row)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(PEOPLE_HEADERS))
        self.table.setHorizontalHeaderLabels(PEOPLE_HEADERS)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def open_add_window(self):
        if self._add_window is None:
            self._add_window = AddDataWindow(
                self.db,
                on_data_changed=self.on_data_changed,
                parent=self,
            )
        self._add_window.load_lookups()
        self._add_window.show()
        self._add_window.raise_()
        self._add_window.activateWindow()

    def open_edit_window(self):
        if self._editData_window is None:
            self._editData_window = EditDataWindow(
                self.db,
                on_data_changed=self.on_data_changed,
                parent=self,
            )
        else:
            self._editData_window.reload()
        self._editData_window.show()
        self._editData_window.raise_()
        self._editData_window.activateWindow()

    def on_data_changed(self):
        self.load_lookups()
        self.refresh_table()

    def _make_filter_combo(self, title: str):
        wrapper = QWidget(self)
        row = QVBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(2)
        label = QLabel(title, wrapper)
        combo = QComboBox(wrapper)
        combo.addItem("— все —", None)
        row.addWidget(label)
        row.addWidget(combo)
        return {"box": wrapper, "combo": combo}

    def _repopulate_combo(self, combo: QComboBox, rows):
        saved = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("— все —", None)
        for u_id, val in rows:
            combo.addItem(str(val), u_id)
        idx = combo.findData(saved)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def load_lookups(self):
        specs = (
            ("fam", self.combo_fam),
            ("nam", self.combo_nam),
            ("otc", self.combo_otc),
            ("street", self.combo_street),
        )
        for table, ui in specs:
            rows = self.db.fetch_lookup(table)
            self._lookups[table] = rows
            self._repopulate_combo(ui["combo"], rows)

    def _filter_ids(self):
        phone = self.telef_combo.text().strip() or None
        home = self.home_combo.text().strip() or None
        return (
            self.combo_fam["combo"].currentData(),
            self.combo_nam["combo"].currentData(),
            self.combo_otc["combo"].currentData(),
            self.combo_street["combo"].currentData(),
            phone,
            home
        )

    def reset_filters(self):
        for key in ("combo_fam", "combo_nam", "combo_otc", "combo_street"):
            getattr(self, key)["combo"].setCurrentIndex(0)
        self.telef_combo.clear()
        self.home_combo.clear()
        self.refresh_table()

    def _fill_table(self, columns, rows, *, people_view: bool):
        self._people_view = people_view
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem("" if val is None else str(val))
                if people_view and col_idx == 0:
                    item.setData(Qt.UserRole, val)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def run_sql(self):
        query = self.sql_input.text().strip()
        if not query:
            QMessageBox.warning(self, "SQL", "Введите запрос.")
            return
        try:
            result = self.db.execute_sql(query)
        except Exception as e:
            QMessageBox.critical(self, "SQL", f"Ошибка выполнения:\n{e}")
            return

        if result["kind"] == "command":
            self.on_data_changed()
            self.status_label.setText(
                f"Запрос выполнен. Затронуто строк: {result['rowcount']}"
            )
            return

        self._fill_table(result["columns"], result["rows"], people_view=False)
        self.status_label.setText(f"Строк в результате: {result['rowcount']}")

    def refresh_table(self):
        fam_id, nam_id, otc_id, street_id, telef_n, home_n = self._filter_ids()
        try:
            rows = self.db.fetch_people(fam_id, nam_id, otc_id, street_id, telef_n, home_n)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{e}")
            return

        self._fill_table(PEOPLE_HEADERS, rows, people_view=True)
        self.status_label.setText(f"Записей: {len(rows)}")

    def delete_by_filter(self):
        fam_id, nam_id, otc_id, street_id, phone_n, home_n = self._filter_ids()
        if all(x is None for x in (fam_id, nam_id, otc_id, street_id)):
            QMessageBox.warning(
                self,
                "Удаление",
                "Задайте хотя бы один фильтр, чтобы удалить записи.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            "Удалить все записи people, подходящие под текущий фильтр?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            deleted = self.db.delete_people(fam_id, nam_id, otc_id, street_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")
            return

        QMessageBox.information(self, "Удаление", f"Удалено записей: {deleted}")
        self.refresh_table()

    def delete_selected(self):
        if not self._people_view:
            QMessageBox.warning(
                self,
                "Удаление",
                "Удаление выбранных доступно только в таблице people "
                "(«Обновить» или «Применить фильтр»).",
            )
            return
        ids = []
        for item in self.table.selectedItems():
            if item.column() == 0:
                uid = item.data(Qt.UserRole)
                if uid is not None and uid not in ids:
                    ids.append(uid)

        if not ids:
            QMessageBox.warning(self, "Удаление", "Выберите одну или несколько строк.")
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить выбранные записи ({len(ids)} шт.)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            deleted = self.db.delete_people_by_ids(ids)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")
            return

        QMessageBox.information(self, "Удаление", f"Удалено записей: {deleted}")
        self.refresh_table()
