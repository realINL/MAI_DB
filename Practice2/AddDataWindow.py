from PyQt5.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from db import Database

LOOKUP_LABELS = {
    "fam": "Фамилия",
    "nam": "Имя",
    "otc": "Отчество",
    "street": "Улица",
}


class AddDataWindow(QMainWindow):
    def __init__(self, db: Database, on_data_changed=None, parent=None):
        super().__init__(parent)
        self.db = db
        self._on_data_changed = on_data_changed
        self._lookups = {}
        self.initUI()
        self.load_lookups()

    def initUI(self):
        self.setWindowTitle("Добавление данных")
        self.resize(520, 320)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        lookup_group = QGroupBox("Справочник", self)
        lookup_layout = QVBoxLayout(lookup_group)
        lookup_row = QHBoxLayout()
        self.lookup_kind = QComboBox(self)
        for key, label in LOOKUP_LABELS.items():
            self.lookup_kind.addItem(label, key)
        self.lookup_value_input = QLineEdit(self)
        self.lookup_value_input.setPlaceholderText("Новое значение")
        self.btn_add_lookup = QPushButton("Добавить", self)
        self.btn_add_lookup.clicked.connect(self.add_lookup_value)
        lookup_row.addWidget(QLabel("Тип:", self))
        lookup_row.addWidget(self.lookup_kind)
        lookup_row.addWidget(self.lookup_value_input, stretch=1)
        lookup_row.addWidget(self.btn_add_lookup)
        lookup_layout.addLayout(lookup_row)
        layout.addWidget(lookup_group)

        person_group = QGroupBox("Запись в таблицу people", self)
        person_layout = QVBoxLayout(person_group)

        row1 = QHBoxLayout()
        self.add_combo_fam = self._make_add_combo("Фамилия")
        self.add_combo_nam = self._make_add_combo("Имя")
        self.add_combo_otc = self._make_add_combo("Отчество")
        self.add_combo_street = self._make_add_combo("Улица")
        for w in (
            self.add_combo_fam,
            self.add_combo_nam,
            self.add_combo_otc,
            self.add_combo_street,
        ):
            row1.addWidget(w["box"])
        person_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.input_bldn = QLineEdit(self)
        self.input_bldn.setPlaceholderText("Дом")
        self.input_bldn_k = QLineEdit(self)
        self.input_bldn_k.setPlaceholderText("Корп.")
        self.input_appr = QLineEdit(self)
        self.input_appr.setPlaceholderText("Квартира")
        self.input_telef = QLineEdit(self)
        self.input_telef.setPlaceholderText("Телефон")
        self.btn_add_person = QPushButton("Добавить запись", self)
        self.btn_add_person.clicked.connect(self.add_person)
        for w in (
            self.input_bldn,
            self.input_bldn_k,
            self.input_appr,
            self.input_telef,
        ):
            row2.addWidget(w)
        row2.addWidget(self.btn_add_person)
        person_layout.addLayout(row2)
        layout.addWidget(person_group)

        layout.addStretch()

    def _make_add_combo(self, title: str):
        wrapper = QWidget(self)
        row = QVBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(2)
        label = QLabel(title, wrapper)
        combo = QComboBox(wrapper)
        combo.addItem("— выберите —", None)
        row.addWidget(label)
        row.addWidget(combo)
        return {"box": wrapper, "combo": combo}

    def _repopulate_combo(self, combo: QComboBox, rows):
        saved = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("— выберите —", None)
        for u_id, val in rows:
            combo.addItem(str(val), u_id)
        idx = combo.findData(saved)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def load_lookups(self):
        specs = (
            ("fam", self.add_combo_fam),
            ("nam", self.add_combo_nam),
            ("otc", self.add_combo_otc),
            ("street", self.add_combo_street),
        )
        for table, ui in specs:
            rows = self.db.fetch_lookup(table)
            self._lookups[table] = rows
            self._repopulate_combo(ui["combo"], rows)

    def _notify_changed(self):
        if self._on_data_changed:
            self._on_data_changed()

    def _select_in_add_combos(self, table: str, u_id: int):
        mapping = {
            "fam": self.add_combo_fam,
            "nam": self.add_combo_nam,
            "otc": self.add_combo_otc,
            "street": self.add_combo_street,
        }
        ui = mapping[table]
        idx = ui["combo"].findData(u_id)
        if idx >= 0:
            ui["combo"].setCurrentIndex(idx)

    def add_lookup_value(self):
        table = self.lookup_kind.currentData()
        value = self.lookup_value_input.text().strip()
        if not value:
            QMessageBox.warning(self, "Справочник", "Введите значение.")
            return
        try:
            new_id = self.db.insert_lookup(table, value)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить значение:\n{e}")
            return

        self.lookup_value_input.clear()
        self.load_lookups()
        self._select_in_add_combos(table, new_id)
        self._notify_changed()
        QMessageBox.information(
            self,
            "Справочник",
            f"Добавлено: «{value}» (id={new_id})",
        )

    def add_person(self):
        fam_id = self.add_combo_fam["combo"].currentData()
        nam_id = self.add_combo_nam["combo"].currentData()
        otc_id = self.add_combo_otc["combo"].currentData()
        street_id = self.add_combo_street["combo"].currentData()

        bldn = self.input_bldn.text().strip() or None
        bldn_k = self.input_bldn_k.text().strip() or None
        telef_n = self.input_telef.text().strip() or None
        appr_raw = self.input_appr.text().strip()
        appr = None
        if appr_raw:
            try:
                appr = int(appr_raw)
            except ValueError:
                QMessageBox.warning(self, "Запись", "Квартира должна быть числом.")
                return

        try:
            new_id = self.db.insert_person(
                fam_id,
                nam_id,
                otc_id,
                street_id,
                bldn=bldn,
                bldn_k=bldn_k,
                appr=appr,
                telef_n=telef_n,
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{e}")
            return

        self.input_bldn.clear()
        self.input_bldn_k.clear()
        self.input_appr.clear()
        self.input_telef.clear()
        self._notify_changed()
        QMessageBox.information(self, "Запись", f"Добавлен человек (id={new_id}).")
