from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import Database

LOOKUP_LABELS = {
    "fam": "Фамилии",
    "nam": "Имена",
    "otc": "Отчества",
    "street": "Улицы",
}

HEADERS = ["ID", "Значение", "Использований"]


class EditDataWindow(QMainWindow):

    def __init__(self, db: Database, on_data_changed=None, parent=None):
        super().__init__(parent)
        self.db = db
        self._on_data_changed = on_data_changed
        self._rows = []          # текущее содержимое таблицы (u_id, value, used)
        self.initUI()
        self.reload()

    # ---------- UI ----------

    def initUI(self):
        self.setWindowTitle("Справочники")
        self.resize(640, 520)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        top.addWidget(QLabel("Справочник:", self))
        self.kind_combo = QComboBox(self)
        for key, label in LOOKUP_LABELS.items():
            self.kind_combo.addItem(label, key)
        self.kind_combo.currentIndexChanged.connect(self.reload)
        top.addWidget(self.kind_combo, stretch=1)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_value)
        layout.addWidget(self.table)

        self.status = QLabel("", self)
        layout.addWidget(self.status)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Добавить", self)
        self.btn_add.clicked.connect(self.add_value)
        self.btn_edit = QPushButton("Изменить", self)
        self.btn_edit.clicked.connect(self.edit_value)
        self.btn_delete = QPushButton("Удалить", self)
        self.btn_delete.clicked.connect(self.delete_value)
        # self.btn_refresh = QPushButton("Обновить", self)
        # self.btn_refresh.clicked.connect(self.reload)
        for b in (self.btn_add, self.btn_edit, self.btn_delete):
            btns.addWidget(b)
        btns.addStretch()
        layout.addLayout(btns)

    # ---------- данные ----------

    def _current_table(self) -> str:
        return self.kind_combo.currentData()

    def _selected_u_id(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rows):
            return None
        return self._rows[row][0]

    def reload(self):
        table = self._current_table()
        try:
            rows = self.db.fetch_lookup(table)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить справочник:\n{e}")
            return

        self._rows = []
        self.table.setRowCount(0)
        print("count:")
        for u_id, val in rows:
            try:
                used = self.db.count_lookup_usage(table, u_id)
            except Exception:
                used = 0
            self._rows.append((u_id, val, used))

        self.table.setRowCount(len(self._rows))
        for r, (u_id, val, used) in enumerate(self._rows):
            id_item = QTableWidgetItem(str(u_id))
            id_item.setData(Qt.UserRole, u_id)
            self.table.setItem(r, 0, id_item)
            self.table.setItem(r, 1, QTableWidgetItem(str(val)))
            used_item = QTableWidgetItem(str(used))
            used_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 2, used_item)

        self.table.resizeColumnsToContents()
        self.status.setText(f"Значений в справочнике: {len(self._rows)}")

    def _notify_changed(self):
        if self._on_data_changed:
            self._on_data_changed()

    # ---------- действия ----------

    def add_value(self):
        table = self._current_table()
        label = LOOKUP_LABELS[table]

        text, ok = QInputDialog.getText(
            self, "Новое значение", f"Новое значение для «{label}»:"
        )
        if not ok:
            return
        text = text.strip()
        if not text:
            QMessageBox.warning(self, "Справочник", "Пустое значение недопустимо.")
            return

        try:
            new_id = self.db.insert_lookup(table, text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить:\n{e}")
            return

        self.reload()
        self._select_by_u_id(new_id)
        self._notify_changed()

    def edit_value(self):
        u_id = self._selected_u_id()
        if u_id is None:
            QMessageBox.warning(self, "Изменение", "Выберите строку.")
            return

        table = self._current_table()
        old_text = self.table.item(self.table.currentRow(), 1).text()

        text, ok = QInputDialog.getText(
            self, "Изменение значения", "Новое значение:", text=old_text
        )
        if not ok:
            return
        text = text.strip()
        if not text or text == old_text:
            return

        try:
            self.db.update_lookup(table, u_id, text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить:\n{e}")
            return

        self.reload()
        self._select_by_u_id(u_id)
        self._notify_changed()

    def delete_value(self):
        u_id = self._selected_u_id()
        if u_id is None:
            QMessageBox.warning(self, "Удаление", "Выберите строку.")
            return

        table = self._current_table()
        row = self.table.currentRow()
        text = self.table.item(row, 1).text()
        used = self._rows[row][2]

        if used:
            reply = QMessageBox.question(
                self,
                "Удаление",
                f"Значение «{text}» используется в {used} записях people.\n"
                "Удалить все связанные данные из таблицы people?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            try:
                self.db.delete_people(**{f"{table}_id": u_id})
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось удалить связанные данные:\n{e}"
                )
                return

        reply = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить значение «{text}» из справочника?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.db.delete_lookup(table, u_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")
            return

        self.reload()
        self._notify_changed()

    # ---------- вспомогательное ----------

    def _select_by_u_id(self, u_id):
        for r, (row_id, _, _) in enumerate(self._rows):
            if row_id == u_id:
                self.table.selectRow(r)
                self.table.scrollToItem(self.table.item(r, 0))
                return