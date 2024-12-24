import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QComboBox, QInputDialog
)
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtCore import Qt

# Constants for the Golden Ratio
PHI = (1 + math.sqrt(5)) / 2

# RPM Speed Thresholds
SPEED_THRESHOLDS = [5, 10, 20, 30, 40]  # in km/h

class GearCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Bicycle Gear Ratio Calculator")
        self.setFixedSize(900, int(900 / PHI))  # Increased width to accommodate wheel size selector
        self.init_ui()

    def init_ui(self):
        # Define colors
        BACKGROUND_COLOR = "#2C3E50"  # Dark blue-gray
        BUTTON_COLOR = "#27AE60"      # Nice shade of green
        TEXT_COLOR = "#ECF0F1"        # Light gray

        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)

        # Input Label and Field for Front Gear Teeth
        front_gear_label = QLabel("Front Gear Teeth:")
        front_gear_label.setStyleSheet("font-size: 14px;")
        self.front_gear_input = QLineEdit()
        self.front_gear_input.setFixedWidth(100)
        self.front_gear_input.setStyleSheet("padding: 5px; font-size: 14px;")
        input_layout.addWidget(front_gear_label)
        input_layout.addWidget(self.front_gear_input)

        # Wheel Size Label and ComboBox
        wheel_size_label = QLabel("Wheel Size:")
        wheel_size_label.setStyleSheet("font-size: 14px; margin-left: 20px;")
        self.wheel_size_combo = QComboBox()
        self.wheel_size_combo.setFixedWidth(150)
        self.wheel_size_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        # Define common wheel sizes in inches
        common_wheel_sizes = [
            "20 inches",
            "24 inches",
            "26 inches",
            "27.5 inches",
            "700C (~29 inches)",  # Default
            "Other"
        ]
        self.wheel_size_combo.addItems(common_wheel_sizes)
        self.wheel_size_combo.setCurrentText("700C (~29 inches)")  # Set default to "700C (~29 inches)"
        input_layout.addWidget(wheel_size_label)
        input_layout.addWidget(self.wheel_size_combo)
        input_layout.addStretch()

        # Calculate Button
        calculate_button = QPushButton("Calculate")
        calculate_button.setStyleSheet(f"background-color: {BUTTON_COLOR}; padding: 10px; font-size: 14px;")
        calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(calculate_button)

        # Clear Button
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("background-color: #95A5A6; padding: 10px; font-size: 14px;")
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Rear Gear", "Gear Inch", "Gear Ratio",
            "RPM @ 5 km/h", "RPM @ 10 km/h",
            "RPM @ 20 km/h", "RPM @ 30 km/h", "RPM @ 40 km/h"
        ])
        
        # Adjust column widths
        for i in range(self.table.columnCount()):
            if i >= 3:  # RPM columns
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 120)
            else:
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #34495E;
                color: #ECF0F1;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2980B9;
                padding: 4px;
                border: 1px solid #2C3E50;
            }
            QTableWidget::item:selected {
                background-color: #1ABC9C;
            }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table non-editable
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def calculate_rpm(self, gear_ratio, speed_kmh, wheel_circumference_m):
        """
        Calculates RPM based on gear ratio, speed, and wheel circumference.
        """
        # Convert speed from km/h to m/s
        speed_ms = speed_kmh * 1000 / 3600
        # RPM = (speed / circumference) * 60 / gear_ratio
        rpm = (speed_ms / wheel_circumference_m) * 60 / gear_ratio
        return f"{rpm:.2f}"

    def calculate(self):
        """
        Handles the calculation and populates the table with results.
        """
        try:
            front_teeth_text = self.front_gear_input.text()
            front_teeth = int(front_teeth_text)
            if front_teeth < 1:
                raise ValueError
        except ValueError:
            QMessageBox.critical(
                self, "Invalid Input",
                "Please enter a valid positive integer for front gear teeth."
            )
            return

        # Get selected wheel size
        selected_wheel_size = self.wheel_size_combo.currentText()
        # Map wheel sizes to their diameters in inches
        wheel_size_mapping = {
            "20 inches": 20,
            "24 inches": 24,
            "26 inches": 26,
            "27.5 inches": 27.5,
            "700C (~29 inches)": 29,  # Approximation
            "Other": None  # Placeholder for custom sizes
        }

        wheel_diameter_in = wheel_size_mapping.get(selected_wheel_size, None)

        # If "Other" is selected, prompt user to enter custom wheel size
        if wheel_diameter_in is None:
            custom_wheel_size, ok = QInputDialog.getDouble(
                self, "Custom Wheel Size",
                "Enter wheel diameter in inches:",
                decimals=2, min=10, max=60  # Reasonable range for wheel sizes
            )
            if ok:
                wheel_diameter_in = custom_wheel_size
            else:
                # User canceled; abort calculation
                return

        # Convert wheel diameter to meters for RPM calculation
        wheel_diameter_m = wheel_diameter_in * 0.0254  # 1 inch = 0.0254 meters
        wheel_circumference_m = wheel_diameter_m * math.pi

        # Clear previous results
        self.table.setRowCount(0)

        # Populate table with rear gears from 9T to 60T
        for rear_teeth in range(9, 61):
            gear_ratio = front_teeth / rear_teeth
            gear_inch = wheel_diameter_in * gear_ratio  # Gear Inch = Wheel Diameter (in) * (Front Teeth / Rear Teeth)
            rpms = [self.calculate_rpm(gear_ratio, speed, wheel_circumference_m) for speed in SPEED_THRESHOLDS]

            # Insert row
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Rear Gear (as text, e.g., "15T")
            rear_gear_item = QTableWidgetItem(f"{rear_teeth}T")
            rear_gear_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_position, 0, rear_gear_item)

            # Gear Inch
            gear_inch_item = QTableWidgetItem(f"{gear_inch:.2f}")
            gear_inch_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_position, 1, gear_inch_item)

            # Gear Ratio
            gear_ratio_item = QTableWidgetItem(f"{gear_ratio:.2f}")
            gear_ratio_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_position, 2, gear_ratio_item)

            # RPMs at different speeds
            for idx, rpm in enumerate(rpms):
                rpm_item = QTableWidgetItem(rpm)
                rpm_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_position, 3 + idx, rpm_item)

    def clear(self):
        """
        Clears the input field and the results table.
        """
        self.front_gear_input.clear()
        self.table.setRowCount(0)

    def keyPressEvent(self, event):
        """
        Overrides the keyPressEvent to handle copying.
        """
        if (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_C:
            self.copy_selection()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        """
        Copies the selected table data to the clipboard.
        """
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        clipboard = QApplication.clipboard()
        copy_text = ""

        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                row_data = []
                for column in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    item = self.table.item(row, column)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                copy_text += "\t".join(row_data) + "\n"

        clipboard.setText(copy_text)

def main():
    app = QApplication(sys.argv)
    calculator = GearCalculator()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
