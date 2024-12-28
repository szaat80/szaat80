from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QHBoxLayout,
    QTableWidget, QTabWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QDate  # QDate hozzáadva
from PySide6.QtWidgets import QMainWindow

import sqlite3

class DatabaseManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = sqlite3.connect('fuvarok.db')
        self.setupDatabase()
        self.setupFuelDatabase()
        self.initUI()

    def setupDatabase(self):
        cursor = self.conn.cursor()
        
        # Sofőr tábla létrehozása
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                birth_date TEXT,
                birth_place TEXT,
                address TEXT,
                mothers_name TEXT,
                tax_number TEXT,
                social_security_number TEXT,
                bank_name TEXT,
                bank_account TEXT,
                drivers_license_number TEXT,
                drivers_license_expiry TEXT
            )
        ''')
        
        # Gépjármű tábla létrehozása
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY,
                plate_number TEXT NOT NULL,
                type TEXT,
                brand TEXT,
                model TEXT,
                year_of_manufacture INTEGER,
                chassis_number TEXT,
                engine_number TEXT,
                engine_type TEXT,
                fuel_type TEXT,
                max_weight INTEGER,
                own_weight INTEGER,
                payload_capacity INTEGER,
                seats INTEGER,
                technical_review_date TEXT,
                tachograph_type TEXT,
                tachograph_calibration_date TEXT,
                fire_extinguisher_expiry TEXT
            )
        ''')
        
        self.conn.commit()
        
    def initUI(self):
        self.setWindowTitle("Törzsadat Kezelő")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(self.createFactoriesTab(), "Gyárak")
        tabs.addTab(self.createAddressesTab(), "Címek")
        tabs.addTab(self.createVacationTab(), "Szabadság")
        tabs.addTab(self.createDriversTab(), "Sofőrök")
        tabs.addTab(self.createVehiclesTab(), "Gépjárművek")
        tabs.addTab(self.createFuelTab(), "Üzemanyag")
        layout.addWidget(tabs)
        
        self.setLayout(layout)

    def createDriversTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Űrlap létrehozása
        form_layout = QFormLayout()
        
        # Személyes adatok
        self.driver_name = QLineEdit()
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_place = QLineEdit()
        self.address = QLineEdit()
        self.mothers_name = QLineEdit()
        
        # Hivatalos azonosítók
        self.tax_number = QLineEdit()
        self.social_security_number = QLineEdit()
        self.drivers_license_number = QLineEdit()
        self.drivers_license_expiry = QDateEdit()
        self.drivers_license_expiry.setCalendarPopup(True)
        
        # Banki adatok
        self.bank_name = QLineEdit()
        self.bank_account = QLineEdit()
        
        # Mezők hozzáadása
        form_layout.addRow("Név:", self.driver_name)
        form_layout.addRow("Születési idő:", self.birth_date)
        form_layout.addRow("Születési hely:", self.birth_place)
        form_layout.addRow("Lakcím:", self.address)
        form_layout.addRow("Anyja neve:", self.mothers_name)
        form_layout.addRow("Adószám:", self.tax_number)
        form_layout.addRow("TAJ szám:", self.social_security_number)
        form_layout.addRow("Jogosítvány száma:", self.drivers_license_number)
        form_layout.addRow("Jogosítvány lejárata:", self.drivers_license_expiry)
        form_layout.addRow("Bank neve:", self.bank_name)
        form_layout.addRow("Bankszámlaszám:", self.bank_account)
        
        # Gombok
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Hozzáadás")
        save_btn = QPushButton("Mentés")
        delete_btn = QPushButton("Törlés")
        
        add_btn.clicked.connect(self.addDriver)
        save_btn.clicked.connect(self.saveDriverChanges)
        delete_btn.clicked.connect(self.deleteDriver)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        
        # Táblázat
        self.drivers_table = QTableWidget()
        self.drivers_table.setColumnCount(11)
        self.drivers_table.setHorizontalHeaderLabels([
            "ID", "Név", "Születési idő", "Születési hely", "Lakcím",
            "Anyja neve", "Adószám", "TAJ szám", "Jogosítvány száma",
            "Bank neve", "Bankszámlaszám"
        ])
        self.drivers_table.itemClicked.connect(self.onDriverSelected)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.drivers_table)
        
        widget.setLayout(layout)
        self.loadDrivers()
        return widget

    def onDriverSelected(self, item):
       try:
           row = item.row()
           # Minden mező óvatos beállítása
           self.driver_name.setText(self.drivers_table.item(row, 1).text() if self.drivers_table.item(row, 1) else "")
           self.birth_date.setDate(QDate.fromString(self.drivers_table.item(row, 2).text(), 'yyyy-MM-dd') if self.drivers_table.item(row, 2) else QDate.currentDate())
           self.birth_place.setText(self.drivers_table.item(row, 3).text() if self.drivers_table.item(row, 3) else "")
           self.address.setText(self.drivers_table.item(row, 4).text() if self.drivers_table.item(row, 4) else "")
           self.mothers_name.setText(self.drivers_table.item(row, 5).text() if self.drivers_table.item(row, 5) else "")
           self.tax_number.setText(self.drivers_table.item(row, 6).text() if self.drivers_table.item(row, 6) else "")
           self.social_security_number.setText(self.drivers_table.item(row, 7).text() if self.drivers_table.item(row, 7) else "")
           self.drivers_license_number.setText(self.drivers_table.item(row, 8).text() if self.drivers_table.item(row, 8) else "")
           self.drivers_license_expiry.setDate(QDate.fromString(self.drivers_table.item(row, 9).text(), 'yyyy-MM-dd') if self.drivers_table.item(row, 9) else QDate.currentDate())
           self.bank_name.setText(self.drivers_table.item(row, 10).text() if self.drivers_table.item(row, 10) else "")
           self.bank_account.setText(self.drivers_table.item(row, 11).text() if self.drivers_table.item(row, 11) else "")
       except Exception as e:
           QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def createVehiclesTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Alapadatok
        self.plate_number = QLineEdit()
        self.vehicle_type = QLineEdit()
        self.brand = QLineEdit()
        self.model = QLineEdit()
        self.year_of_manufacture = QSpinBox()
        self.year_of_manufacture.setRange(1900, QDate.currentDate().year())
        
        # Azonosítók
        self.chassis_number = QLineEdit()
        self.engine_number = QLineEdit()
        self.engine_type = QLineEdit()
        self.fuel_type = QComboBox()
        self.fuel_type.addItems(["Dízel", "Benzin", "Elektromos", "Hibrid"])
        
        # Műszaki adatok
        self.max_weight = QSpinBox()
        self.max_weight.setRange(0, 50000)
        self.max_weight.setSuffix(" kg")
        self.own_weight = QSpinBox()
        self.own_weight.setRange(0, 50000)
        self.own_weight.setSuffix(" kg")
        self.payload_capacity = QSpinBox()
        self.payload_capacity.setRange(0, 50000)
        self.payload_capacity.setSuffix(" kg")
        self.seats = QSpinBox()
        self.seats.setRange(1, 50)
        
        # Dátumok és speciális adatok
        self.technical_review_date = QDateEdit()
        self.technical_review_date.setCalendarPopup(True)
        self.tachograph_type = QLineEdit()
        self.tachograph_calibration_date = QDateEdit()
        self.tachograph_calibration_date.setCalendarPopup(True)
        self.fire_extinguisher_expiry = QDateEdit()
        self.fire_extinguisher_expiry.setCalendarPopup(True)
        
        # Mezők hozzáadása az űrlaphoz
        form_layout.addRow("Rendszám:", self.plate_number)
        form_layout.addRow("Típus:", self.vehicle_type)
        form_layout.addRow("Márka:", self.brand)
        form_layout.addRow("Model:", self.model)
        form_layout.addRow("Gyártási év:", self.year_of_manufacture)
        form_layout.addRow("Alvázszám:", self.chassis_number)
        form_layout.addRow("Motorszám:", self.engine_number)
        form_layout.addRow("Motor típus:", self.engine_type)
        form_layout.addRow("Üzemanyag:", self.fuel_type)
        form_layout.addRow("Össztömeg:", self.max_weight)
        form_layout.addRow("Saját tömeg:", self.own_weight)
        form_layout.addRow("Hasznos terhelés:", self.payload_capacity)
        form_layout.addRow("Ülések száma:", self.seats)
        form_layout.addRow("Műszaki vizsga:", self.technical_review_date)
        form_layout.addRow("Tachográf típus:", self.tachograph_type)
        form_layout.addRow("Tachográf hitelesítés:", self.tachograph_calibration_date)
        form_layout.addRow("Tűzoltó készülék lejárat:", self.fire_extinguisher_expiry)
        
        # Gombok
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Hozzáadás")
        save_btn = QPushButton("Mentés")
        delete_btn = QPushButton("Törlés")
        
        add_btn.clicked.connect(self.addVehicle)
        save_btn.clicked.connect(self.saveVehicleChanges)
        delete_btn.clicked.connect(self.deleteVehicle)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        
        # Táblázat
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(17)
        self.vehicles_table.setHorizontalHeaderLabels([
            "ID", "Rendszám", "Típus", "Márka", "Model", "Gyártási év",
            "Alvázszám", "Motorszám", "Motor típus", "Üzemanyag",
            "Össztömeg", "Saját tömeg", "Hasznos terhelés", "Ülések száma",
            "Műszaki vizsga", "Tachográf típus", "Tachográf hitelesítés"
        ])
        self.vehicles_table.itemClicked.connect(self.onVehicleSelected)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.vehicles_table)
        
        widget.setLayout(layout)
        self.loadVehicles()
        return widget

    def loadVehicles(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM vehicles")
            vehicles = cursor.fetchall()
        
            self.vehicles_table.setRowCount(len(vehicles))
            for row, vehicle in enumerate(vehicles):
                for col, value in enumerate(vehicle):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.vehicles_table.setItem(row, col, item)
                
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def addVehicle(self):
        try:
            if not self.plate_number.text():
                QMessageBox.warning(self, "Figyelmeztetés", "A rendszám megadása kötelező!")
                return
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO vehicles (
                    plate_number, type, brand, model, year_of_manufacture,
                    chassis_number, engine_number, engine_type, fuel_type,
                    max_weight, own_weight, payload_capacity, seats,
                    technical_review_date, tachograph_type,
                    tachograph_calibration_date, fire_extinguisher_expiry
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.plate_number.text(),
                self.vehicle_type.text(),
                self.brand.text(),
                self.model.text(),
                self.year_of_manufacture.value(),
                self.chassis_number.text(),
                self.engine_number.text(),
                self.engine_type.text(),
                self.fuel_type.currentText(),
                self.max_weight.value(),
                self.own_weight.value(),
                self.payload_capacity.value(),
                self.seats.value(),
                self.technical_review_date.date().toString('yyyy-MM-dd'),
                self.tachograph_type.text(),
                self.tachograph_calibration_date.date().toString('yyyy-MM-dd'),
                self.fire_extinguisher_expiry.date().toString('yyyy-MM-dd')
            ))
        
            self.conn.commit()
            self.loadVehicles()
            self.clearVehicleFields()
            QMessageBox.information(self, "Siker", "Gépjármű sikeresen hozzáadva!")
        
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def clearVehicleFields(self):
        self.plate_number.clear()
        self.vehicle_type.clear()
        self.brand.clear()
        self.model.clear()
        self.year_of_manufacture.setValue(QDate.currentDate().year())
        self.chassis_number.clear()
        self.engine_number.clear()
        self.engine_type.clear()
        self.fuel_type.setCurrentIndex(0)
        self.max_weight.setValue(0)
        self.own_weight.setValue(0)
        self.payload_capacity.setValue(0)
        self.seats.setValue(2)
        self.technical_review_date.setDate(QDate.currentDate())
        self.tachograph_type.clear()
        self.tachograph_calibration_date.setDate(QDate.currentDate())
        self.fire_extinguisher_expiry.setDate(QDate.currentDate())

    def addDriver(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO drivers (
                    name, birth_date, birth_place, address, mothers_name,
                    tax_number, social_security_number, drivers_license_number,
                    drivers_license_expiry, bank_name, bank_account
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.driver_name.text(),
                self.birth_date.date().toString('yyyy-MM-dd'),
                self.birth_place.text(),
                self.address.text(),
                self.mothers_name.text(),
                self.tax_number.text(),
                self.social_security_number.text(),
                self.drivers_license_number.text(),
                self.drivers_license_expiry.date().toString('yyyy-MM-dd'),
                self.bank_name.text(),
                self.bank_account.text()
            ))
            
            self.conn.commit()
            self.loadDrivers()
            QMessageBox.information(self, "Siker", "Sofőr sikeresen hozzáadva!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def saveDriverChanges(self):
        try:
            selected_items = self.drivers_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy sofőrt!")
                return
                
            driver_id = int(self.drivers_table.item(selected_items[0].row(), 0).text())
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE drivers SET
                    name = ?, birth_date = ?, birth_place = ?, address = ?,
                    mothers_name = ?, tax_number = ?, social_security_number = ?,
                    drivers_license_number = ?, drivers_license_expiry = ?,
                    bank_name = ?, bank_account = ?
                WHERE id = ?
            ''', (
                self.driver_name.text(),
                self.birth_date.date().toString('yyyy-MM-dd'),
                self.birth_place.text(),
                self.address.text(),
                self.mothers_name.text(),
                self.tax_number.text(),
                self.social_security_number.text(),
                self.drivers_license_number.text(),
                self.drivers_license_expiry.date().toString('yyyy-MM-dd'),
                self.bank_name.text(),
                self.bank_account.text(),
                driver_id
            ))
            
            self.conn.commit()
            self.loadDrivers()
            QMessageBox.information(self, "Siker", "Változások mentve!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def deleteDriver(self):
        try:
            selected_items = self.drivers_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy sofőrt!")
                return
            
            driver_id = int(self.drivers_table.item(selected_items[0].row(), 0).text())
        
            reply = QMessageBox.question(self, 'Megerősítés', 
                                       'Biztosan törli a kiválasztott sofőrt?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
            if reply == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
                self.conn.commit()
                self.loadDrivers()
                QMessageBox.information(self, "Siker", "Sofőr sikeresen törölve!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def loadDrivers(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM drivers
            ''')
        
            drivers = cursor.fetchall()
        
            self.drivers_table.setRowCount(len(drivers))
            for row, driver in enumerate(drivers):
                for col, value in enumerate(driver):
                    self.drivers_table.setItem(row, col, QTableWidgetItem(str(value)))
                
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def onVehicleSelected(self, item):
       try:
           row = item.row()
           # Minden mező óvatos beállítása
           self.plate_number.setText(self.vehicles_table.item(row, 1).text() if self.vehicles_table.item(row, 1) else "")
           self.vehicle_type.setText(self.vehicles_table.item(row, 2).text() if self.vehicles_table.item(row, 2) else "")
           self.brand.setText(self.vehicles_table.item(row, 3).text() if self.vehicles_table.item(row, 3) else "")
           self.model.setText(self.vehicles_table.item(row, 4).text() if self.vehicles_table.item(row, 4) else "")
           self.year_of_manufacture.setValue(int(self.vehicles_table.item(row, 5).text()) if self.vehicles_table.item(row, 5) and self.vehicles_table.item(row, 5).text().isdigit() else 1900)
           self.chassis_number.setText(self.vehicles_table.item(row, 6).text() if self.vehicles_table.item(row, 6) else "")
           self.engine_number.setText(self.vehicles_table.item(row, 7).text() if self.vehicles_table.item(row, 7) else "")
           self.engine_type.setText(self.vehicles_table.item(row, 8).text() if self.vehicles_table.item(row, 8) else "")
           self.fuel_type.setCurrentText(self.vehicles_table.item(row, 9).text() if self.vehicles_table.item(row, 9) else "Dízel")
           self.max_weight.setValue(int(self.vehicles_table.item(row, 10).text()) if self.vehicles_table.item(row, 10) and self.vehicles_table.item(row, 10).text().isdigit() else 0)
           self.own_weight.setValue(int(self.vehicles_table.item(row, 11).text()) if self.vehicles_table.item(row, 11) and self.vehicles_table.item(row, 11).text().isdigit() else 0)
           self.payload_capacity.setValue(int(self.vehicles_table.item(row, 12).text()) if self.vehicles_table.item(row, 12) and self.vehicles_table.item(row, 12).text().isdigit() else 0)
           self.seats.setValue(int(self.vehicles_table.item(row, 13).text()) if self.vehicles_table.item(row, 13) and self.vehicles_table.item(row, 13).text().isdigit() else 2)
       
           # Dátumok beállítása
           date_fields = [
               (self.technical_review_date, 14),
               (self.tachograph_calibration_date, 16),
               (self.fire_extinguisher_expiry, 17)
           ]
           for date_field, col in date_fields:
               if self.vehicles_table.item(row, col) and self.vehicles_table.item(row, col).text():
                   date_field.setDate(QDate.fromString(self.vehicles_table.item(row, col).text(), 'yyyy-MM-dd'))
               else:
                   date_field.setDate(QDate.currentDate())
       except Exception as e:
           QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def addVehicle(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO vehicles (
                    plate_number, type, brand, model, year_of_manufacture,
                    chassis_number, engine_number, engine_type, fuel_type,
                    max_weight, own_weight, payload_capacity, seats,
                    technical_review_date, tachograph_type,
                    tachograph_calibration_date, fire_extinguisher_expiry
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.plate_number.text(),
                self.vehicle_type.text(),
                self.brand.text(),
                self.model.text(),
                self.year_of_manufacture.value(),
                self.chassis_number.text(),
                self.engine_number.text(),
                self.engine_type.text(),
                self.fuel_type.currentText(),
                self.max_weight.value(),
                self.own_weight.value(),
                self.payload_capacity.value(),
                self.seats.value(),
                self.technical_review_date.date().toString('yyyy-MM-dd'),
                self.tachograph_type.text(),
                self.tachograph_calibration_date.date().toString('yyyy-MM-dd'),
                self.fire_extinguisher_expiry.date().toString('yyyy-MM-dd')
            ))
        
            self.conn.commit()
            self.loadVehicles()
            QMessageBox.information(self, "Siker", "Gépjármű sikeresen hozzáadva!")
        
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def saveVehicleChanges(self):
        try:
            selected_items = self.vehicles_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy gépjárművet!")
                return
            
            vehicle_id = int(self.vehicles_table.item(selected_items[0].row(), 0).text())
        
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE vehicles SET
                    plate_number = ?, type = ?, brand = ?, model = ?,
                    year_of_manufacture = ?, chassis_number = ?, engine_number = ?,
                    engine_type = ?, fuel_type = ?, max_weight = ?, own_weight = ?,
                    payload_capacity = ?, seats = ?, technical_review_date = ?,
                    tachograph_type = ?, tachograph_calibration_date = ?,
                    fire_extinguisher_expiry = ?
                WHERE id = ?
            ''', (
                self.plate_number.text(),
                self.vehicle_type.text(),
                self.brand.text(),
                self.model.text(),
                self.year_of_manufacture.value(),
                self.chassis_number.text(),
                self.engine_number.text(),
                self.engine_type.text(),
                self.fuel_type.currentText(),
                self.max_weight.value(),
                self.own_weight.value(),
                self.payload_capacity.value(),
                self.seats.value(),
                self.technical_review_date.date().toString('yyyy-MM-dd'),
                self.tachograph_type.text(),
                self.tachograph_calibration_date.date().toString('yyyy-MM-dd'),
                self.fire_extinguisher_expiry.date().toString('yyyy-MM-dd'),
                vehicle_id
            ))
        
            self.conn.commit()
            self.loadVehicles()
            QMessageBox.information(self, "Siker", "Változások mentve!")
        
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def deleteVehicle(self):
        try:
            selected_items = self.vehicles_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy gépjárművet!")
                return
            
            vehicle_id = int(self.vehicles_table.item(selected_items[0].row(), 0).text())
        
            reply = QMessageBox.question(self, 'Megerősítés', 
                                       'Biztosan törli a kiválasztott gépjárművet?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
            if reply == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
                self.conn.commit()
                self.loadVehicles()
                QMessageBox.information(self, "Siker", "Gépjármű sikeresen törölve!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def loadVehicles(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM vehicles
            ''')
        
            vehicles = cursor.fetchall()
        
            self.vehicles_table.setRowCount(len(vehicles))
            for row, vehicle in enumerate(vehicles):
                for col, value in enumerate(vehicle):
                    self.vehicles_table.setItem(row, col, QTableWidgetItem(str(value)))
                
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def onVehicleSelected(self, item):
        try:
            row = item.row()
            self.plate_number.setText(self.vehicles_table.item(row, 1).text())
            self.vehicle_type.setText(self.vehicles_table.item(row, 2).text())
            self.brand.setText(self.vehicles_table.item(row, 3).text())
            self.model.setText(self.vehicles_table.item(row, 4).text())
            self.year_of_manufacture.setValue(int(self.vehicles_table.item(row, 5).text()))
            self.chassis_number.setText(self.vehicles_table.item(row, 6).text())
            self.engine_number.setText(self.vehicles_table.item(row, 7).text())
            self.engine_type.setText(self.vehicles_table.item(row, 8).text())
            self.fuel_type.setCurrentText(self.vehicles_table.item(row, 9).text())
            self.max_weight.setValue(int(self.vehicles_table.item(row, 10).text()))
            self.own_weight.setValue(int(self.vehicles_table.item(row, 11).text()))
            self.payload_capacity.setValue(int(self.vehicles_table.item(row, 12).text()))
            self.seats.setValue(int(self.vehicles_table.item(row, 13).text()))
            self.technical_review_date.setDate(QDate.fromString(self.vehicles_table.item(row, 14).text(), 'yyyy-MM-dd'))
            self.tachograph_type.setText(self.vehicles_table.item(row, 15).text())
            self.tachograph_calibration_date.setDate(QDate.fromString(self.vehicles_table.item(row, 16).text(), 'yyyy-MM-dd'))
            self.fire_extinguisher_expiry.setDate(QDate.fromString(self.vehicles_table.item(row, 17).text(), 'yyyy-MM-dd'))
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def createVacationTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
    
        form_layout = QFormLayout()
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(year) for year in range(current_year-1, current_year+2)])
        self.year_combo.setCurrentText(str(current_year))
    
        self.vacation_days = QSpinBox()
        self.vacation_days.setRange(0, 100)
        self.vacation_days.setSingleStep(1)
    
        form_layout.addRow("Év:", self.year_combo)
        form_layout.addRow("Szabadság napok:", self.vacation_days)
    
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Mentés")
        delete_btn = QPushButton("Törlés")
        save_btn.clicked.connect(self.saveVacationDays)
        delete_btn.clicked.connect(self.deleteVacationDays)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
    
        self.vacation_table = QTableWidget()
        self.vacation_table.setColumnCount(3)
        self.vacation_table.setHorizontalHeaderLabels(["Év", "Összes nap", "Felhasznált napok"])
    
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.vacation_table)
        widget.setLayout(layout)
    
        self.loadVacationData()
        return widget

    def createFactoriesTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Gyár alapadatok bevitele
        form_layout = QFormLayout()
        self.factory_name = QLineEdit()
        self.waiting_fee = QSpinBox()
        self.waiting_fee.setRange(0, 100000)
        self.waiting_fee.setSingleStep(500)
        form_layout.addRow("Gyár neve:", self.factory_name)
        form_layout.addRow("Állásidő díj (Ft/15 perc):", self.waiting_fee)
        
        # Övezeti díj hozzáadása szekció
        zone_layout = QHBoxLayout()
        self.zone_combo = QComboBox()
        self.zone_combo.addItems([f"Övezet {i}-{i+5}" for i in range(0, 50, 5)])
        self.zone_price = QSpinBox()
        self.zone_price.setRange(0, 100000)
        self.zone_price.setSingleStep(500)
        
        zone_layout.addWidget(self.zone_combo)
        zone_layout.addWidget(self.zone_price)
        form_layout.addRow("Övezeti díj:", zone_layout)
        
        # Gombok
        btn_layout = QHBoxLayout()
        add_factory_btn = QPushButton("Gyár hozzáadása")
        add_factory_btn.clicked.connect(self.addFactory)
        add_zone_btn = QPushButton("Övezeti díj hozzáadása")
        add_zone_btn.clicked.connect(self.addZonePrice)
        save_changes_btn = QPushButton("Változások mentése")
        save_changes_btn.clicked.connect(self.saveFactoryChanges)
        delete_factory_btn = QPushButton("Gyár törlése")
        delete_factory_btn.clicked.connect(self.deleteFactory)
        
        btn_layout.addWidget(add_factory_btn)
        btn_layout.addWidget(add_zone_btn)
        btn_layout.addWidget(save_changes_btn)
        btn_layout.addWidget(delete_factory_btn)
        
        # Gyárak táblázat
        self.factory_table = QTableWidget()
        self.factory_table.setColumnCount(3)
        self.factory_table.setHorizontalHeaderLabels(["ID", "Név", "Állásidő díj"])
        self.factory_table.itemClicked.connect(self.onFactorySelected)
        
        # Övezeti díjak táblázat
        self.zone_prices_table = QTableWidget()
        self.zone_prices_table.setColumnCount(3)
        self.zone_prices_table.setHorizontalHeaderLabels(["Övezet", "Díj (Ft)", ""])
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.factory_table)
        layout.addWidget(self.zone_prices_table)
        
        widget.setLayout(layout)

        # Éves szabadság keret beállítása
        form_layout = QFormLayout()
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(year) for year in range(current_year-1, current_year+2)])
        self.year_combo.setCurrentText(str(current_year))
    
        self.vacation_days = QSpinBox()
        self.vacation_days.setRange(0, 100)
        self.vacation_days.setSingleStep(1)
    
        form_layout.addRow("Év:", self.year_combo)
        form_layout.addRow("Szabadság napok:", self.vacation_days)
    
        # Gombok
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Mentés")
        save_btn.clicked.connect(self.saveVacationDays)
        btn_layout.addWidget(save_btn)
    
        # Táblázat az éves szabadságokhoz
        self.vacation_table = QTableWidget()
        self.vacation_table.setColumnCount(3)
        self.vacation_table.setHorizontalHeaderLabels(["Év", "Összes nap", "Felhasznált napok"])
    
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.vacation_table)
        widget.setLayout(layout)
        
        # Adatok betöltése
        self.loadFactories()
        return widget

    def addFactory(self):
        name = self.factory_name.text()
        waiting_fee = self.waiting_fee.value()
        
        if not name:
            QMessageBox.warning(self, "Hiba", "A gyár nevét kötelező megadni!")
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Gyár alapadatok mentése
            cursor.execute("INSERT INTO factories (nev) VALUES (?)", (name,))
            factory_id = cursor.lastrowid
            
            # Állásidő díj mentése
            cursor.execute(
                "INSERT INTO factory_waiting_fees (factory_id, price_per_15_min) VALUES (?, ?)",
                (factory_id, waiting_fee)
            )
            
            # Automatikusan hozzáadjuk az összes övezetet 0 díjjal
            for i in range(0, 50, 5):
                zone_name = f"Övezet {i}-{i+5}"
                cursor.execute(
                    "INSERT INTO factory_zone_prices (factory_id, zone_name, price) VALUES (?, ?, 0)",
                    (factory_id, zone_name)
                )
            
            self.conn.commit()
            self.loadFactories()
            
            # Mezők törlése
            self.factory_name.clear()
            self.waiting_fee.setValue(0)
            
            QMessageBox.information(self, "Siker", "Gyár sikeresen hozzáadva!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def deleteFactory(self):
        selected_items = self.factory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hiba", "Először válasszon ki egy gyárat!")
            return
            
        factory_id = int(self.factory_table.item(selected_items[0].row(), 0).text())
        factory_name = self.factory_table.item(selected_items[0].row(), 1).text()
        
        reply = QMessageBox.question(self, 'Megerősítés', 
                                   f'Biztosan törölni szeretné a következő gyárat: {factory_name}?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                
                # Töröljük a gyárhoz tartozó összes kapcsolódó adatot
                cursor.execute("DELETE FROM factory_zone_prices WHERE factory_id = ?", (factory_id,))
                cursor.execute("DELETE FROM factory_waiting_fees WHERE factory_id = ?", (factory_id,))
                cursor.execute("DELETE FROM factories WHERE id = ?", (factory_id,))
                
                self.conn.commit()
                self.loadFactories()
                self.zone_prices_table.setRowCount(0)  # Töröljük az övezeti díjakat
                
                QMessageBox.information(self, "Siker", "Gyár sikeresen törölve!")
                
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def addZonePrice(self):
        selected_items = self.factory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hiba", "Először válasszon ki egy gyárat!")
            return
            
        factory_id = int(self.factory_table.item(selected_items[0].row(), 0).text())
        zone = self.zone_combo.currentText()
        price = self.zone_price.value()
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "UPDATE factory_zone_prices SET price = ? WHERE factory_id = ? AND zone_name = ?",
                (price, factory_id, zone)
            )
            
            self.conn.commit()
            self.loadZonePrices(factory_id)
            self.zone_price.setValue(0)
            
            QMessageBox.information(self, "Siker", "Övezeti díj sikeresen módosítva!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def createAddressesTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
    
        form_layout = QFormLayout()
        self.address = QLineEdit()
        self.address_price = QSpinBox()
        self.address_price.setRange(0, 1000000)
        form_layout.addRow("Cím:", self.address)
        form_layout.addRow("Egyedi ár:", self.address_price)
    
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Hozzáadás")
        add_btn.clicked.connect(self.addAddress)
        delete_btn = QPushButton("Törlés")
        delete_btn.clicked.connect(self.deleteAddress)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
    
        self.address_table = QTableWidget()
        self.address_table.setColumnCount(3)
        self.address_table.setHorizontalHeaderLabels(["ID", "Cím", "Ár"])
    
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.address_table)
        widget.setLayout(layout)
        self.loadAddresses()
    
        return widget

    def loadAddresses(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM addresses ORDER BY cim")
            addresses = cursor.fetchall()
    
            self.address_table.setRowCount(len(addresses))
            for row, (id, address, price) in enumerate(addresses):
                self.address_table.setItem(row, 0, QTableWidgetItem(str(id)))
                self.address_table.setItem(row, 1, QTableWidgetItem(address))
                self.address_table.setItem(row, 2, QTableWidgetItem(str(price)))
            
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def loadFactories(self):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT f.id, f.nev, COALESCE(fw.price_per_15_min, 0)
                FROM factories f
                LEFT JOIN factory_waiting_fees fw ON f.id = fw.factory_id
            """)
            
            factories = cursor.fetchall()
            
            self.factory_table.setRowCount(len(factories))
            for row, (id, name, waiting_fee) in enumerate(factories):
                self.factory_table.setItem(row, 0, QTableWidgetItem(str(id)))
                self.factory_table.setItem(row, 1, QTableWidgetItem(name))
                self.factory_table.setItem(row, 2, QTableWidgetItem(str(waiting_fee)))
                
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def loadZonePrices(self, factory_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT zone_name, price FROM factory_zone_prices WHERE factory_id = ?",
                (factory_id,)
            )
            
            prices = cursor.fetchall()
            
            self.zone_prices_table.setRowCount(len(prices))
            for row, (zone, price) in enumerate(prices):
                self.zone_prices_table.setItem(row, 0, QTableWidgetItem(zone))
                self.zone_prices_table.setItem(row, 1, QTableWidgetItem(str(price)))
                
                # Törlés gomb hozzáadása
                delete_btn = QPushButton("Törlés")
                delete_btn.clicked.connect(lambda checked, z=zone: self.deleteZonePrice(factory_id, z))
                self.zone_prices_table.setCellWidget(row, 2, delete_btn)
                
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az övezeti díjak betöltése során: {str(e)}")

    def onFactorySelected(self, item):
        factory_id = int(self.factory_table.item(item.row(), 0).text())
        self.loadZonePrices(factory_id)

    def deleteZonePrice(self, factory_id, zone):
        try:
            cursor = self.conn.cursor()
            # Övezeti díj nullázása törlés helyett
            cursor.execute(
                "UPDATE factory_zone_prices SET price = 0 WHERE factory_id = ? AND zone_name = ?",
                (factory_id, zone)
            )
            self.conn.commit()
            self.loadZonePrices(factory_id)
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def saveFactoryChanges(self):
        selected_items = self.factory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hiba", "Először válasszon ki egy gyárat!")
            return
            
        try:
            row = selected_items[0].row()
            factory_id = int(self.factory_table.item(row, 0).text())
            waiting_fee = int(self.factory_table.item(row, 2).text())
            
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE factory_waiting_fees SET price_per_15_min = ? WHERE factory_id = ?",
                (waiting_fee, factory_id)
            )
            
            self.conn.commit()
            QMessageBox.information(self, "Siker", "Változások mentve!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def addAddress(self):
        address = self.address.text()
        price = self.address_price.value()
        if address and price:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO addresses (cim, ar) VALUES (?, ?)", (address, price))
            self.conn.commit()
            self.loadAddresses()
            self.address.clear()
            self.address_price.setValue(0)

    def deleteAddress(self):
        try:
            selected_items = self.address_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy címet!")
                return
            
            address_id = int(self.address_table.item(selected_items[0].row(), 0).text())
            address = self.address_table.item(selected_items[0].row(), 1).text()
        
            reply = QMessageBox.question(self, 'Megerősítés', 
                                       f'Biztosan törölni szeretné a következő címet: {address}?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
            if reply == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM addresses WHERE id = ?", (address_id,))
                self.conn.commit()
                self.loadAddresses()
                QMessageBox.information(self, "Siker", "Cím sikeresen törölve!")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def onWorkTypeChanged(self, work_type):
        if work_type == "Szabadság":
            self.vacation_frame.show()
            self.updateVacationDisplay()
        else:
            self.vacation_frame.hide()

    def updateVacationDisplay(self):
        cursor = self.conn.cursor()
        current_year = QDate.currentDate().year()
    
        # Lekérjük az aktuális év szabadság keretét
        cursor.execute("""
            SELECT total_days, used_days 
            FROM vacation_allowance 
            WHERE year = ?
        """, (current_year,))
    
        result = cursor.fetchone()
        if result:
            total_days, used_days = result
            self.vacation_label.setText(f"Szabadság: {used_days}/{total_days}")
        else:
            # Ha nincs még rekord az aktuális évre
            cursor.execute("""
                INSERT INTO vacation_allowance (year, total_days, used_days)
                VALUES (?, 29, 0)  # Alapértelmezett 29 nap
            """, (current_year,))
            self.conn.commit()
            self.vacation_label.setText("Szabadság: 0/20")

    def saveVacationDays(self):
        try:
            year = int(self.year_combo.currentText())
            total_days = self.vacation_days.value()
        
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vacation_allowance (year, total_days, used_days)
                VALUES (?, ?, COALESCE((SELECT used_days FROM vacation_allowance WHERE year = ?), 0))
            """, (year, total_days, year))
        
            self.conn.commit()
            self.loadVacationData()
            QMessageBox.information(self, "Siker", "Szabadság keret sikeresen mentve!")
        
            # Értesítjük a főablakot a változásról
            if isinstance(self.parent(), QMainWindow):
                self.parent().updateVacationDisplay()
        
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def deleteVacationDays(self):
        try:
            selected_items = self.vacation_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy sort!")
                return
            
            row = selected_items[0].row()
            year = int(self.vacation_table.item(row, 0).text())
        
            reply = QMessageBox.question(self, 'Megerősítés', 
                                       f'Biztosan törli a {year} évi szabadság keretet?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
            if reply == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM vacation_allowance WHERE year = ?", (year,))
                self.conn.commit()
                self.loadVacationData()
            
                # Értesítjük a főablakot a változásról
                if isinstance(self.parent(), QMainWindow):
                    self.parent().updateVacationDisplay()
                
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def loadVacationData(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT year, total_days, used_days FROM vacation_allowance ORDER BY year DESC")
            data = cursor.fetchall()
        
            self.vacation_table.setRowCount(len(data))
            for row, (year, total, used) in enumerate(data):
                self.vacation_table.setItem(row, 0, QTableWidgetItem(str(year)))
                self.vacation_table.setItem(row, 1, QTableWidgetItem(str(total)))
                self.vacation_table.setItem(row, 2, QTableWidgetItem(str(used)))
            
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def setupFuelDatabase(self):
        cursor = self.conn.cursor()
    
        # Ellenőrizzük, hogy létezik-e már az avg_consumption oszlop
        try:
            cursor.execute("SELECT avg_consumption FROM fuel_consumption LIMIT 1")
        except:
            # Ha nem létezik, akkor hozzáadjuk
            cursor.execute("ALTER TABLE fuel_consumption ADD COLUMN avg_consumption REAL")
    
        # Létrehozzuk a táblát, ha még nem létezik
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_consumption (
                id INTEGER PRIMARY KEY,
                vehicle_id INTEGER,
                date TEXT,
                odometer_reading INTEGER,
                fuel_amount REAL,
                fuel_price REAL,
                total_cost REAL,
                location TEXT,
                full_tank BOOLEAN,
                avg_consumption REAL,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')
        self.conn.commit()

    def createFuelTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
    
        # Adatbeviteli űrlap
        form_layout = QFormLayout()
    
        self.fuel_vehicle_combo = QComboBox()
        self.loadVehiclesForFuel()
    
        self.fuel_date = QDateEdit()
        self.fuel_date.setCalendarPopup(True)
        self.fuel_date.setDate(QDate.currentDate())
    
        # Itt hozzuk létre az odometer QSpinBox-ot
        self.odometer = QSpinBox()
        self.odometer.setRange(0, 9999999)  # Megfelelő tartomány beállítása
        self.odometer.setSuffix(" km")      # Mértékegység hozzáadása
    
        self.fuel_amount = QDoubleSpinBox()
        self.fuel_amount.setRange(0, 1000)
        self.fuel_amount.setDecimals(2)
    
        self.fuel_price = QDoubleSpinBox()
        self.fuel_price.setRange(0, 10000)
        self.fuel_price.setDecimals(2)
    
        self.total_cost = QLineEdit()
        self.total_cost.setReadOnly(True)
    
        self.location = QLineEdit()
    
        self.full_tank = QCheckBox("Tele tank")
    
        # Mezők hozzáadása
        form_layout.addRow("Jármű:", self.fuel_vehicle_combo)
        form_layout.addRow("Dátum:", self.fuel_date)
        form_layout.addRow("Kilométeróra állás:", self.odometer)
        form_layout.addRow("Üzemanyag mennyiség (L):", self.fuel_amount)
        form_layout.addRow("Üzemanyag ár (Ft/L):", self.fuel_price)
        form_layout.addRow("Összköltség (Ft):", self.total_cost)
        form_layout.addRow("Helyszín:", self.location)
        form_layout.addRow("", self.full_tank)
    
        # Események
        self.fuel_amount.valueChanged.connect(self.calculateTotalCost)
        self.fuel_price.valueChanged.connect(self.calculateTotalCost)
    
        # Gombok
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Hozzáadás")
        add_btn.clicked.connect(self.addFuelRecord)
        delete_btn = QPushButton("Törlés")
        delete_btn.clicked.connect(self.deleteFuelRecord)
    
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
    
        # Táblázat
        self.fuel_table = QTableWidget()
        self.fuel_table.setColumnCount(10)
        self.fuel_table.setHorizontalHeaderLabels([
            "ID", "Jármű", "Dátum", "Kilométeróra", "Mennyiség (L)",
            "Ár (Ft/L)", "Összköltség (Ft)", "Helyszín", "Tele tank",
            "Átlagfogyasztás (L/100km)"
        ])
    
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.fuel_table)
    
        widget.setLayout(layout)
        self.loadFuelRecords()
        return widget

    def calculateFuelConsumption(self, previous_record, current_record):
        try:
            distance = current_record[3] - previous_record[3]  # kilométeróra különbség
            fuel_amount = current_record[4]  # üzemanyag mennyiség
        
            if distance > 0 and fuel_amount > 0:
                consumption = (fuel_amount / distance) * 100
                return round(consumption, 2)
            return 0
        except:
            return 0

    def addFuelRecord(self):
        try:
            cursor = self.conn.cursor()
            vehicle_id = self.fuel_vehicle_combo.currentData()
        
            # Előző tankolás adatainak lekérése
            cursor.execute('''
                SELECT odometer_reading, fuel_amount 
                FROM fuel_consumption 
                WHERE vehicle_id = ? AND full_tank = TRUE
                ORDER BY date DESC, odometer_reading DESC 
                LIMIT 1
            ''', (vehicle_id,))
        
            previous_record = cursor.fetchone()
        
            # Új tankolás adatai
            new_odometer = int(self.odometer.value())
            new_fuel_amount = float(self.fuel_amount.value())
        
            # Átlagfogyasztás számítása
            avg_consumption = None
            if previous_record and self.full_tank.isChecked():
                prev_odometer = previous_record[0]
                distance = new_odometer - prev_odometer
                if distance > 0:  # Csak ha volt távolság
                    avg_consumption = (new_fuel_amount / distance) * 100
        
            # Adatok beszúrása
            cursor.execute('''
                INSERT INTO fuel_consumption (
                    vehicle_id, date, odometer_reading, fuel_amount,
                    fuel_price, total_cost, location, full_tank,
                    avg_consumption
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle_id,
                self.fuel_date.date().toString('yyyy-MM-dd'),
                new_odometer,
                new_fuel_amount,
                self.fuel_price.value(),
                float(self.total_cost.text().replace(' ', '')) if self.total_cost.text() else 0,
                self.location.text(),
                self.full_tank.isChecked(),
                avg_consumption
            ))
        
            self.conn.commit()
            self.loadFuelRecords()
        
            # Ha volt átlagfogyasztás számítás, jelezzük
            if avg_consumption is not None:
                QMessageBox.information(self, "Információ", 
                    f"Átlagfogyasztás: {avg_consumption:.2f} L/100km")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def loadVehiclesForFuel(self):
        try:
            self.fuel_vehicle_combo.clear()
            cursor = self.conn.cursor()
        
            # Lekérjük az aktív járműveket
            cursor.execute("""
                SELECT id, plate_number 
                FROM vehicles 
                ORDER BY plate_number
            """)
        
            vehicles = cursor.fetchall()
        
            # Ha nincsenek járművek, jelezzük
            if not vehicles:
                QMessageBox.warning(self, "Figyelmeztetés", "Nincsenek járművek az adatbázisban!")
                return
            
            # Járművek hozzáadása a legördülő listához
            for vehicle_id, plate_number in vehicles:
                self.fuel_vehicle_combo.addItem(plate_number, vehicle_id)
            
            # Kapcsoljuk a jármű választó változásához az eseménykezelőt
            self.fuel_vehicle_combo.currentIndexChanged.connect(self.onVehicleChanged)
        
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt a járművek betöltése során: {str(e)}")

    def onVehicleChanged(self, index):
        """Jármű váltásakor frissítjük az adatokat"""
        try:
            vehicle_id = self.fuel_vehicle_combo.currentData()
            if vehicle_id is None:
                return
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT date
                FROM fuel_consumption 
                WHERE vehicle_id = ? 
                ORDER BY date DESC
                LIMIT 1
            ''', (vehicle_id,))
        
            previous_record = cursor.fetchone()
            if previous_record:
                # Dátum frissítése
                if previous_record[0]:
                    try:
                        last_date = QDate.fromString(previous_record[0], 'yyyy-MM-dd')
                        self.fuel_date.setDate(last_date)
                    except:
                        self.fuel_date.setDate(QDate.currentDate())
                    
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt a jármű adatainak frissítésekor: {str(e)}")

    def calculateTotalCost(self):
        amount = self.fuel_amount.value()
        price = self.fuel_price.value()
        total = amount * price
        self.total_cost.setText(f"{total:.2f}")

    def addFuelRecord(self):
        try:
            cursor = self.conn.cursor()
            vehicle_id = self.fuel_vehicle_combo.currentData()
        
            # Get current odometer reading and fuel amount
            current_odometer = self.odometer.value()
            current_fuel = self.fuel_amount.value()
            is_full_tank = self.full_tank.isChecked()
        
            # Get the last full tank record for this vehicle
            cursor.execute('''
                SELECT odometer_reading, fuel_amount 
                FROM fuel_consumption 
                WHERE vehicle_id = ? AND full_tank = 1
                ORDER BY date DESC, odometer_reading DESC 
                LIMIT 1
            ''', (vehicle_id,))
        
            last_record = cursor.fetchone()
            avg_consumption = None
        
            # Calculate average consumption only if:
            # 1. This is a full tank fill-up
            # 2. We have a previous full tank record
            # 3. The current odometer reading is higher than the previous one
            if is_full_tank and last_record and current_odometer > last_record[0]:
                distance = current_odometer - last_record[0]  # Distance traveled since last fill
                if distance > 0:
                    # L/100km = (Fuel amount in liters / Distance in km) * 100
                    avg_consumption = (current_fuel / distance) * 100
                    avg_consumption = round(avg_consumption, 2)  # Round to 2 decimal places
        
            # Insert the new record with calculated average consumption
            cursor.execute('''
                INSERT INTO fuel_consumption (
                    vehicle_id, date, odometer_reading, fuel_amount,
                    fuel_price, total_cost, location, full_tank,
                    avg_consumption
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle_id,
                self.fuel_date.date().toString('yyyy-MM-dd'),
                current_odometer,
                current_fuel,
                self.fuel_price.value(),
                float(self.total_cost.text().replace(' ', '')) if self.total_cost.text() else 0,
                self.location.text(),
                is_full_tank,
                avg_consumption
            ))
        
            self.conn.commit()
            self.loadFuelRecords()
        
            # Show the calculated consumption if available
            if avg_consumption is not None:
                QMessageBox.information(self, "Információ", 
                    f"Átlagfogyasztás: {avg_consumption:.2f} L/100km")
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a mentés során: {str(e)}")

    def loadFuelRecords(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT 
                    f.id,
                    v.plate_number,
                    f.date,
                    f.odometer_reading,
                    f.fuel_amount,
                    f.fuel_price,
                    f.total_cost,
                    f.location,
                    f.full_tank,
                    f.avg_consumption
                FROM fuel_consumption f
                JOIN vehicles v ON f.vehicle_id = v.id
                ORDER BY f.date DESC, f.odometer_reading DESC
            ''')
        
            records = cursor.fetchall()
        
            self.fuel_table.setRowCount(len(records))
            for row, record in enumerate(records):
                # Basic fields
                for col, value in enumerate(record):
                    item = QTableWidgetItem()
                
                    if col == 4:  # Fuel amount
                        item.setText(f"{value:.1f}" if value is not None else "")
                    elif col == 5:  # Fuel price
                        item.setText(f"{value:.2f}" if value is not None else "")
                    elif col == 6:  # Total cost
                        item.setText(f"{value:.2f}" if value is not None else "")
                    elif col == 8:  # Full tank
                        item.setText("Igen" if value else "Nem")
                    elif col == 9:  # Average consumption
                        item.setText(f"{value:.2f}" if value is not None else "")
                    else:
                        item.setText(str(value) if value is not None else "")
                
                    item.setTextAlignment(Qt.AlignCenter)
                    self.fuel_table.setItem(row, col, item)
        
            # Resize columns to content
            self.fuel_table.resizeColumnsToContents()
        
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt az adatok betöltése során: {str(e)}")

    def deleteFuelRecord(self):
        try:
            selected_items = self.fuel_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Figyelmeztetés", "Kérem válasszon ki egy rekordot!")
                return
            
            record_id = int(self.fuel_table.item(selected_items[0].row(), 0).text())
        
            reply = QMessageBox.question(self, 'Megerősítés', 
                                       'Biztosan törli a kiválasztott rekordot?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
            if reply == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM fuel_consumption WHERE id = ?", (record_id,))
                self.conn.commit()
                self.loadFuelRecords()
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Hiba", f"Hiba történt a törlés során: {str(e)}")

    def generateFuelReport(self, vehicle_id=None, start_date=None, end_date=None):
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT 
                    v.plate_number,
                    COUNT(*) as tankolas_szam,
                    SUM(f.fuel_amount) as ossz_mennyiseg,
                    SUM(f.total_cost) as ossz_koltseg,
                    MAX(f.odometer_reading) - MIN(f.odometer_reading) as megtett_km,
                    CASE 
                        WHEN MAX(f.odometer_reading) - MIN(f.odometer_reading) > 0 
                        THEN (SUM(f.fuel_amount) / (MAX(f.odometer_reading) - MIN(f.odometer_reading))) * 100
                        ELSE 0 
                    END as atlag_fogyasztas
                FROM fuel_consumption f
                JOIN vehicles v ON f.vehicle_id = v.id
                WHERE 1=1
            '''
        
            params = []
            if vehicle_id:
                query += " AND v.id = ?"
                params.append(vehicle_id)
            if start_date:
                query += " AND f.date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND f.date <= ?"
                params.append(end_date)
            
            query += " GROUP BY v.id, v.plate_number"
        
            cursor.execute(query, params)
            return cursor.fetchall()
        
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba történt a riport generálása során: {str(e)}")
        return []