from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLabel
from PyQt6.QtCore import Qt

class ResultsDialog(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Deney Sonuçları")
        self.resize(800, 600)
        self.results = results
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Karşılaştırmalı Analiz Sonuçları")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Algoritma", "Ortalama Maliyet", "Ortalama Süre (s)", "Toplam Deneme"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Populate Table
        self.load_data()

        # Close Button
        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def load_data(self):
        # results structure: {algo: {'costs': [], 'times': []}}
        if not self.results:
            return

        row_count = len(self.results)
        self.table.setRowCount(row_count)
        
        for i, (algo_name, data) in enumerate(self.results.items()):
            costs = data.get('costs', [])
            times = data.get('times', [])
            
            avg_cost = sum(costs) / len(costs) if costs else 0
            avg_time = sum(times) / len(times) if times else 0
            count = len(costs)
            
            self.table.setItem(i, 0, QTableWidgetItem(algo_name))
            self.table.setItem(i, 1, QTableWidgetItem(f"{avg_cost:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{avg_time:.4f}"))
            self.table.setItem(i, 3, QTableWidgetItem(str(count)))
