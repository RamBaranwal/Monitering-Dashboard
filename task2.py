import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QTabWidget, QLineEdit, QPushButton
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Monitor")
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.cpu_mem_tab = QWidget()
        self.process_tab = QWidget()

        self.tabs.addTab(self.cpu_mem_tab, "📊 CPU & Memory")
        self.tabs.addTab(self.process_tab, "🖥 Running Processes")

        self.init_cpu_mem_tab()
        self.init_process_tab()

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(5000)  # Refresh every 5 seconds

    def init_cpu_mem_tab(self):
        layout = QVBoxLayout()

        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setTitle("🔵 CPU Usage (%)", color='w', size='12pt')
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.showGrid(x=True, y=True, alpha=0.3)
        self.cpu_curve = self.cpu_graph.plot(pen=pg.mkPen(color="cyan", width=2))

        self.mem_graph = pg.PlotWidget()
        self.mem_graph.setTitle("🟢 Memory Usage (%)", color='w', size='12pt')
        self.mem_graph.setYRange(0, 100)
        self.mem_graph.showGrid(x=True, y=True, alpha=0.3)
        self.mem_curve = self.mem_graph.plot(pen=pg.mkPen(color="magenta", width=2))

        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("font-size: 14px; color: red; font-weight: bold;")
        
        self.mem_label = QLabel("Memory: 0%")
        self.mem_label.setStyleSheet("font-size: 14px; color: red; font-weight: bold;")

        layout.addWidget(self.cpu_graph)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.mem_graph)
        layout.addWidget(self.mem_label)

        self.cpu_mem_tab.setLayout(layout)

        self.cpu_data = []
        self.mem_data = []

    def init_process_tab(self):
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search process...")
        self.search_input.textChanged.connect(self.search_process)
        self.terminate_button = QPushButton("❌ Terminate")
        self.terminate_button.clicked.connect(self.terminate_process)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.terminate_button)

        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["PID", "Name", "CPU (%)", "Memory (MB)"])
        self.process_table.setSelectionBehavior(self.process_table.SelectRows)  

        self.countdown_label = QLabel("🔄 Refreshing in: 5s")
        self.countdown_label.setStyleSheet("font-size: 14px; color: red; font-weight: bold;")

        layout.addLayout(search_layout)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.process_table)

        self.process_tab.setLayout(layout)

        self.refresh_time = 5
        self.timer_countdown = QTimer()
        self.timer_countdown.timeout.connect(self.update_timer)
        self.timer_countdown.start(1000)

    def update_timer(self):
        self.refresh_time -= 1
        if self.refresh_time < 0:
            self.refresh_time = 5
        self.countdown_label.setText(f"🔄 Refreshing in: {self.refresh_time}s")

    def update_stats(self):
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent

        self.cpu_label.setText(f"CPU: {cpu_usage}%")
        self.mem_label.setText(f"Memory: {mem_usage}%")

        if len(self.cpu_data) > 50:
            self.cpu_data.pop(0)
            self.mem_data.pop(0)

        self.cpu_data.append(cpu_usage)
        self.mem_data.append(mem_usage)

        self.cpu_curve.setData(self.cpu_data)
        self.mem_curve.setData(self.mem_data)

        self.process_table.setRowCount(0)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            row = self.process_table.rowCount()
            self.process_table.insertRow(row)
            self.process_table.setItem(row, 0, QTableWidgetItem(str(proc.info['pid'])))
            self.process_table.setItem(row, 1, QTableWidgetItem(proc.info['name']))
            self.process_table.setItem(row, 2, QTableWidgetItem(str(proc.info['cpu_percent'])))
            mem_mb = round(proc.info['memory_info'].rss / (1024 * 1024), 2)
            self.process_table.setItem(row, 3, QTableWidgetItem(str(mem_mb)))

        self.refresh_time = 5  

    def search_process(self):
        query = self.search_input.text().lower()
        for row in range(self.process_table.rowCount()):
            process_name = self.process_table.item(row, 1).text().lower()
            self.process_table.setRowHidden(row, query not in process_name)

    def terminate_process(self):
        selected = self.process_table.selectedItems()
        if selected:
            pid = int(self.process_table.item(selected[0].row(), 0).text())
            try:
                p = psutil.Process(pid)
                p.terminate()
                self.update_stats()  
            except psutil.NoSuchProcess:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())
