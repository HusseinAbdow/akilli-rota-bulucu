from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox, 
                             QComboBox, QFormLayout, QTextEdit, QScrollArea, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt

class ControlPanel(QWidget):
    # Signals
    generate_signal = pyqtSignal()
    calculate_signal = pyqtSignal()
    source_changed_signal = pyqtSignal(int)
    target_changed_signal = pyqtSignal(int)
    request_random_cases_signal = pyqtSignal()
    run_custom_experiment_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.experiment_cases = []

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. Network Generation Group
        group_gen = QGroupBox("1. Ağ Oluşturma")
        layout_gen = QVBoxLayout()
        self.btn_generate = QPushButton("🔄 Rastgele Ağ Oluştur")
        self.btn_generate.clicked.connect(self.generate_signal.emit)
        layout_gen.addWidget(self.btn_generate)
        
        self.lbl_stats = QLabel("Düğümler: 0 | Bağlantılar: 0")
        layout_gen.addWidget(self.lbl_stats)
        group_gen.setLayout(layout_gen)
        layout.addWidget(group_gen)
        
        # 2. Path Finding Selection Group
        group_sel = QGroupBox("2. Yol Bulma Ayarları")
        layout_sel = QFormLayout()
        
        # Source/Target Spinboxes
        # Source/Target Spinboxes
        self.spin_source = QSpinBox()
        self.spin_source.setRange(0, 250)
        self.spin_source.setValue(0)
        # self.spin_source.setSpecialValueText("Seçiniz") # Removed as requested
        self.spin_source.valueChanged.connect(self.source_changed_signal.emit)
        
        self.spin_target = QSpinBox()
        self.spin_target.setRange(0, 250)
        self.spin_target.setValue(0)
        # self.spin_target.setSpecialValueText("Seçiniz") # Removed as requested
        self.spin_target.valueChanged.connect(self.target_changed_signal.emit)
        
        layout_sel.addRow("Kaynak (S):", self.spin_source)
        layout_sel.addRow("Hedef (D):", self.spin_target)
        
        # Algorithm Selection
        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["Algoritma Seçiniz...", "ACO Algoritma", "Genetik Algoritma", "Q-Learning Algoritma"])
        layout_sel.addRow("Algoritma:", self.combo_algo)
        
        # Weights
        self.spin_w_delay = QDoubleSpinBox()
        self.spin_w_delay.setRange(0, 1)
        self.spin_w_delay.setSingleStep(0.1)
        self.spin_w_delay.setValue(0.0)
        
        self.spin_w_rel = QDoubleSpinBox()
        self.spin_w_rel.setRange(0, 1)
        self.spin_w_rel.setSingleStep(0.1)
        self.spin_w_rel.setValue(0.0)
        
        self.spin_w_bw = QDoubleSpinBox()
        self.spin_w_bw.setRange(0, 1)
        self.spin_w_bw.setSingleStep(0.1)
        self.spin_w_bw.setValue(0.0)
        
        layout_sel.addRow("Gecikme (w1):", self.spin_w_delay)
        layout_sel.addRow("Güvenilirlik (w2):", self.spin_w_rel)
        layout_sel.addRow("Bant Genişliği (w3):", self.spin_w_bw)
        
        self.btn_calculate = QPushButton("🚀 En İyi Yolu Bul")
        self.btn_calculate.clicked.connect(self.calculate_signal.emit)
        layout_sel.addRow(self.btn_calculate)
        
        group_sel.setLayout(layout_sel)
        layout.addWidget(group_sel)
        
        # 3. Results Area
        group_res = QGroupBox("Sonuçlar")
        layout_res = QVBoxLayout()
        self.lbl_result_summary = QLabel("Sonuç bekleniyor...")
        self.lbl_result_summary.setWordWrap(True)
        layout_res.addWidget(self.lbl_result_summary)
        group_res.setLayout(layout_res)
        layout.addWidget(group_res)
        
        # 4. Experiment Mode
        group_exp = QGroupBox("3. Deneysel Karşılaştırma")
        layout_exp = QVBoxLayout()
        
        self.btn_add_random_cases = QPushButton("🎲 Rastgele Senaryolar Ekle (20 adet)")
        self.btn_add_random_cases.clicked.connect(self.request_random_cases_signal.emit)
        layout_exp.addWidget(self.btn_add_random_cases)
        
        self.txt_cases = QTextEdit()
        self.txt_cases.setPlaceholderText("Yüklenen senaryolar burada görünecek...")
        self.txt_cases.setMaximumHeight(100)
        self.txt_cases.setReadOnly(True)
        layout_exp.addWidget(self.txt_cases)
        
        self.btn_run_experiment = QPushButton("🧪 Karşılaştırmayı Başlat")
        self.btn_run_experiment.clicked.connect(self.run_custom_experiment_signal.emit)
        layout_exp.addWidget(self.btn_run_experiment)
        
        group_exp.setLayout(layout_exp)
        layout.addWidget(group_exp)
        
        # Connect signals for auto-balancing
        self.spin_w_delay.valueChanged.connect(lambda: self.normalize_weights(self.spin_w_delay))
        self.spin_w_rel.valueChanged.connect(lambda: self.normalize_weights(self.spin_w_rel))
        self.spin_w_bw.valueChanged.connect(lambda: self.normalize_weights(self.spin_w_bw))
        
        layout.addStretch()

    def normalize_weights(self, changed_spinbox):
        """
        Relaxed balancing: Only adjust others if total > 1.0.
        Allows users to enter values sequentially (e.g. 0.4, 0.4, 0.2) without
        premature adjustment.
        """
        spinners = [self.spin_w_delay, self.spin_w_rel, self.spin_w_bw]
        
        # Block signals to prevent recursive calls
        for s in spinners:
            s.blockSignals(True)
            
        try:
            current_val = changed_spinbox.value()
            
            # 1. Check if we exceeded 1.0
            others = [s for s in spinners if s != changed_spinbox]
            sum_others = sum(s.value() for s in others)
            
            if (current_val + sum_others) > 1.00001:
                # We exceeded 1.0.
                # Priority: Keep the value the user just typed (current_val).
                # Reduce the *others* proportionally to fit the remaining space.
                
                remaining_budget = max(0.0, 1.0 - current_val)
                
                if sum_others > 0:
                    scale_factor = remaining_budget / sum_others
                    for s in others:
                        s.setValue(s.value() * scale_factor)
                else:
                    # Special case: Others were 0, but current > 1? 
                    # Spinbox max is likely 1.0, so this rarely happens unless max > 1.
                    # Just ensure current doesn't exceed 1.
                    if current_val > 1.0:
                        changed_spinbox.setValue(1.0)
                        
        finally:
            # Unblock signals
            for s in spinners:
                s.blockSignals(False)

    def set_stats(self, nodes, links):
        self.lbl_stats.setText(f"Düğümler: {nodes} | Bağlantılar: {links}")

    def get_selected_algorithm(self):
        return self.combo_algo.currentText()

    def get_weights(self):
        return (self.spin_w_delay.value(), self.spin_w_rel.value(), self.spin_w_bw.value())

    def set_selection_values(self, source_id, target_id):
        self.spin_source.blockSignals(True)
        self.spin_target.blockSignals(True)
        
        if source_id is None:
            self.spin_source.setValue(-1)
        else:
            self.spin_source.setValue(source_id)
            
        if target_id is None:
            self.spin_target.setValue(-1)
        else:
            self.spin_target.setValue(target_id)
            
        self.spin_source.blockSignals(False)
        self.spin_target.blockSignals(False)

    def show_results(self, result_obj):
        if result_obj is None:
            self.lbl_result_summary.setText("Yol bulunamadı veya seçim yapılmadı.")
            self.lbl_result_summary.setStyleSheet("color: gray;")
            return
            
        text = (f"<b>Algoritma Başarılı!</b><br>"
                f"Yol: {result_obj.path_nodes}<br>"
                f"Toplam Maliyet: {result_obj.total_cost:.4f}<br>"
                f"Gecikme: {result_obj.total_delay:.2f} ms<br>"
                f"Güvenilirlik Maliyeti: {result_obj.total_reliability:.4f}<br>"
                f"Bant Genişliği Maliyeti: {result_obj.resource_cost:.4f}<br>"
                f"Süre: {result_obj.execution_time:.4f} sn")
        
        self.lbl_result_summary.setText(text)
        self.lbl_result_summary.setStyleSheet("color: #2ecc71; font-size: 11px;")

    def add_cases_batch(self, cases):
        self.experiment_cases.extend(cases)
        self.update_cases_text()

    def update_cases_text(self):
        txt = f"Toplam Senaryo: {len(self.experiment_cases)}\n"
        for i, (s, d, b) in enumerate(self.experiment_cases[-5:]): # Show last 5
            txt += f"{i+1}. {s} -> {d} ({b:.1f} Mbps)\n"
        if len(self.experiment_cases) > 5:
            txt += "... (+ daha fazla)"
        self.txt_cases.setText(txt)

    def get_experiment_config(self):
        # Return currently loaded configuration
        return {
            'cases': self.experiment_cases,
            'algorithms': ["ACO Algoritma", "Genetik Algoritma", "Q-Learning Algoritma"],
            'repetitions': 1 # Default to 1 to save time, or make configurable
        }
