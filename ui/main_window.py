from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QLabel, QPushButton, QComboBox, QGroupBox,
    QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QFileDialog
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Sorter Dashboard")
        self.setMinimumSize(900, 760)

        # Estado
        self.connected = False
        self.red_count = 0
        self.blue_count = 0

        self.history = []  

        self.cbPorts = QComboBox()
        self.btnRefresh = QPushButton("Refresh Ports")
        self.btnConnect = QPushButton("Connect")
        self.lblStatus = QLabel("Status: Disconnected")
        self.badge = QLabel("OFF"); self.badge.setObjectName("BadgeOff")

        top = QHBoxLayout()
        top.addWidget(self.cbPorts, 0)
        top.addWidget(self.btnRefresh, 0)
        top.addWidget(self.btnConnect, 0)
        top.addSpacing(12)
        top.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignVCenter)
        top.addSpacing(6)
        top.addWidget(self.lblStatus, 0, Qt.AlignmentFlag.AlignVCenter)
        top.addStretch(1)

        
        self.colorContainer = QWidget(); self.colorContainer.setObjectName("ColorCard")
        self.lblColorTitle = QLabel("Color Detection"); self.lblColorTitle.setObjectName("ColorTitle")
        self.lblColor = QLabel("—"); self.lblColor.setObjectName("ColorValue")
        self.lblColor.setStyleSheet("color:#aab1c3;")

        rowColor = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(self.lblColorTitle)
        left.addWidget(self.lblColor)
        rowColor.addLayout(left)
        rowColor.addStretch(1)
        self.colorContainer.setLayout(rowColor)

 
        grpCounts = QGroupBox("Counters")
        layCounts = QHBoxLayout()

        colR = QVBoxLayout()
        self.lblRedTitle = QLabel("Red Objects"); self.lblRedTitle.setObjectName("RedTitle")
        self.lblRed = QLabel("0"); self.lblRed.setObjectName("CountNumber")
        colR.addWidget(self.lblRedTitle); colR.addWidget(self.lblRed)

        colB = QVBoxLayout()
        self.lblBlueTitle = QLabel("Blue Objects"); self.lblBlueTitle.setObjectName("BlueTitle")
        self.lblBlue = QLabel("0"); self.lblBlue.setObjectName("CountNumber")
        colB.addWidget(self.lblBlueTitle); colB.addWidget(self.lblBlue)

        layCounts.addLayout(colR)
        layCounts.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layCounts.addLayout(colB)
        grpCounts.setLayout(layCounts)

        self.btnReset = QPushButton("Reset Counters")
        self.btnExport = QPushButton("Export Data")

        self.btnSimRed = QPushButton("+ Red")
        self.btnSimRed.setShortcut("R")
        self.btnSimBlue = QPushButton("+ Blue")
        self.btnSimBlue.setShortcut("B")

        self.btnFullScreen = QPushButton("Full Screen")

        bottom = QHBoxLayout()
        bottom.addWidget(self.btnReset)
        bottom.addWidget(self.btnExport)
        bottom.addSpacing(10)
        bottom.addWidget(self.btnSimRed)
        bottom.addWidget(self.btnSimBlue)
        bottom.addStretch(1)
        bottom.addWidget(self.btnFullScreen)

        self.chartGroup = QGroupBox("Live Chart")
        chartHeader = QHBoxLayout()
        self.chartType = QComboBox()
        self.chartType.addItems(["Pie", "Bar", "XY"])
        chartHeader.addWidget(QLabel("Chart type:"))
        chartHeader.addWidget(self.chartType)
        chartHeader.addStretch(1)

        chartLayout = QVBoxLayout()
        chartLayout.addLayout(chartHeader)
        self.canvas = self._create_chart_canvas()
        chartLayout.addWidget(self.canvas)
        self.chartGroup.setLayout(chartLayout)

        root = QVBoxLayout()
        root.addLayout(top)
        root.addSpacing(12)
        root.addWidget(self.colorContainer)
        root.addSpacing(12)
        root.addWidget(grpCounts)
        root.addSpacing(12)
        root.addLayout(bottom)
        root.addSpacing(12)
        root.addWidget(self.chartGroup)
        root.addStretch(1)

        container = QWidget(); container.setLayout(root)
        self.setCentralWidget(container)

        self.applyStyles()

        # Conexiones
        self.btnRefresh.clicked.connect(self.refreshPorts)
        self.btnConnect.clicked.connect(self.toggleConnection)
        self.btnReset.clicked.connect(self.mockReset)
        self.btnExport.clicked.connect(self.mockExport)
        self.btnFullScreen.clicked.connect(self.toggleFullScreen)
        self.chartType.currentIndexChanged.connect(self.update_chart)

        self.btnSimRed.clicked.connect(lambda: self.setColor("RED"))
        self.btnSimBlue.clicked.connect(lambda: self.setColor("BLUE"))

        # Carga inicial
        self.refreshPorts()
        self._push_history()
        self.update_chart()

    # ---------- Estilos ----------
    def applyStyles(self):
        try:
            with open("ui/styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass
        self.lblColorTitle.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lblColor.setFont(QFont("Segoe UI", 30, QFont.Weight.Black))

    # ---------- DEMO ----------
    def refreshPorts(self):
        self.cbPorts.clear()
        self.cbPorts.addItems(["COM3", "COM4", "COM5"])
        self.cbPorts.setCurrentIndex(0)

    def toggleConnection(self):
        self.connected = not self.connected
        if self.connected:
            self.btnConnect.setText("Disconnect")
            self.lblStatus.setText(f"Status: Connected ({self.cbPorts.currentText()})")
            self.badge.setObjectName("BadgeOk"); self.badge.setText("OK")
            self.badge.style().unpolish(self.badge); self.badge.style().polish(self.badge)
            # demo: evento inicial
            self.setColor("BLUE")
        else:
            self.btnConnect.setText("Connect")
            self.lblStatus.setText("Status: Disconnected")
            self.badge.setObjectName("BadgeOff"); self.badge.setText("OFF")
            self.badge.style().unpolish(self.badge); self.badge.style().polish(self.badge)
            self.setColor("-")

    def mockReset(self):
        self.red_count = 0
        self.blue_count = 0
        self.lblRed.setText("0")
        self.lblBlue.setText("0")
        self.setColor("-")
        self._push_history()
        self.update_chart()

    def mockExport(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "counts.csv", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("Color,Count\n")
            f.write(f"Red,{self.red_count}\n")
            f.write(f"Blue,{self.blue_count}\n")

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def setColor(self, color: str):
        color = color.upper()
        if color == "RED":
            self.lblColor.setText("Red")
            self.lblColor.setStyleSheet("color:#ff4d4d;")
            self.red_count += 1
            self.lblRed.setText(str(self.red_count))
            self._push_history()
            self.update_chart()
        elif color == "BLUE":
            self.lblColor.setText("Blue")
            self.lblColor.setStyleSheet("color:#4d79ff;")
            self.blue_count += 1
            self.lblBlue.setText(str(self.blue_count))
            self._push_history()
            self.update_chart()
        else:
            self.lblColor.setText("—")
            self.lblColor.setStyleSheet("color:#aab1c3;")

    def _push_history(self):
        idx = len(self.history)
        self.history.append((idx, self.red_count, self.blue_count))
        if len(self.history) > 500:
            self.history = self.history[-500:]

    def _create_chart_canvas(self) -> FigureCanvas:
        plt.rcParams["axes.facecolor"] = "#0f1830"
        plt.rcParams["figure.facecolor"] = "#0f1830"
        plt.rcParams["axes.edgecolor"] = "#1f2a44"
        plt.rcParams["xtick.color"] = "#e5e7eb"
        plt.rcParams["ytick.color"] = "#e5e7eb"
        plt.rcParams["text.color"] = "#e5e7eb"

        fig, self.ax = plt.subplots(figsize=(6.5, 3.2), dpi=100)
        canvas = FigureCanvas(fig)
        return canvas

    def update_chart(self):
        chart_mode = self.chartType.currentText().upper()
        self.ax.clear()

        red = self.red_count
        blue = self.blue_count

        if chart_mode == "PIE":
            total = red + blue
            if total == 0:
                self.ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                             color="#aab1c3", fontsize=12)
            else:
                self.ax.pie(
                    [red, blue],
                    labels=["Red", "Blue"],
                    autopct="%1.0f%%",
                    startangle=90,
                    colors=["#ff6b6b", "#7aa2ff"],
                    textprops={"color": "#e5e7eb"},
                )
                self.ax.axis("equal")
            self.ax.set_title("Live Proportion", color="#aab1c3", fontsize=11)

        elif chart_mode == "BAR":
            labels = ["Red", "Blue"]
            values = [red, blue]
            colors = ["#ff6b6b", "#7aa2ff"]
            bars = self.ax.bar(labels, values, color=colors)
            for b in bars:
                b.set_linewidth(0.6)
                b.set_edgecolor("#1f2a44")
            for rect, val in zip(bars, values):
                self.ax.text(rect.get_x() + rect.get_width()/2, rect.get_height() + 0.05,
                             str(val), ha="center", va="bottom", fontsize=10)
            self.ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.6, color="#aab1c333")
            self.ax.set_ylim(0, max(1, max(values) * 1.2))
            self.ax.set_title("Counts (Live)", color="#aab1c3", fontsize=11)

        else:  
            if len(self.history) < 2:
                self.ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                             color="#aab1c3", fontsize=12)
            else:
                xs = [t for (t, r, b) in self.history]
                ys_r = [r for (t, r, b) in self.history]
                ys_b = [b for (t, r, b) in self.history]
                self.ax.plot(xs, ys_r, marker="o", linewidth=1.8, markersize=4, label="Red", color="#ff6b6b")
                self.ax.plot(xs, ys_b, marker="o", linewidth=1.8, markersize=4, label="Blue", color="#7aa2ff")
                self.ax.fill_between(xs, ys_r, step="pre", alpha=0.05, color="#ff6b6b")
                self.ax.fill_between(xs, ys_b, step="pre", alpha=0.05, color="#7aa2ff")
                self.ax.legend(loc="upper left")
                self.ax.grid(alpha=0.25, linestyle="--", linewidth=0.6, color="#aab1c333")
                self.ax.set_xlabel("Event #")
                self.ax.set_ylabel("Count")
                self.ax.set_xlim(left=0, right=max(xs) if xs else 1)
                self.ax.set_ylim(0, max(1, red, blue) * 1.2)
                self.ax.set_title("Counts over time", color="#aab1c3", fontsize=11)

        self.canvas.draw_idle()
