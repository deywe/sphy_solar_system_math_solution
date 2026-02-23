import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QSlider, QLabel, QPushButton, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph.opengl as gl

class HarpiaPlayer(QMainWindow):
    def __init__(self, parquet_path):
        super().__init__()
        self.setWindowTitle("Harpia Player - SPHY Engine (Corrected Axial Tilts)")
        self.resize(1200, 800)

        # 1. Carregar Dados
        self.df = pd.read_parquet(parquet_path)
        self.total_frames = self.df['frame'].max()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor('k')
        self.view.setCameraPosition(distance=300, elevation=30, azimuth=45)
        self.main_layout.addWidget(self.view, stretch=97)

        # 2. Controles
        self.ctrl_frame = QFrame()
        self.ctrl_frame.setStyleSheet("""
            QFrame { background-color: #111; border-top: 1px solid #333; }
            QLabel { color: #AAA; font-family: Monospace; }
        """)
        self.ctrl_layout = QHBoxLayout(self.ctrl_frame)
        self.ctrl_layout.setContentsMargins(15, 0, 15, 0)
        
        self.btn = QPushButton("▶ PLAY")
        self.btn.setFixedWidth(80)
        self.btn.setStyleSheet("background-color: #222; color: white; border: 1px solid #444;")
        self.btn.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(self.total_frames)
        self.slider.valueChanged.connect(self.update_frame)
        
        self.lbl = QLabel("FRAME: 0")
        self.lbl.setFixedWidth(100)
        
        self.ctrl_layout.addWidget(self.btn)
        self.ctrl_layout.addWidget(self.slider)
        self.ctrl_layout.addWidget(self.lbl)
        self.main_layout.addWidget(self.ctrl_frame, stretch=3)

        self.render_objects = {'rings': []}
        self.meshes = {}
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(lambda: self.slider.setValue(
            self.slider.value() + 1 if self.slider.value() < self.total_frames else 0))
        
        self._init_scene()
        self.update_frame(0)

    def _init_scene(self):
        def create_sphere(radius, color):
            md = gl.MeshData.sphere(rows=15, cols=30, radius=radius)
            mesh = gl.GLMeshItem(meshdata=md, smooth=True, color=color, shader='shaded')
            self.view.addItem(mesh)
            return mesh

        self.sun = create_sphere(4.0, (1, 0.9, 0, 1))
        
        n_asteroids = 2000
        radii = np.random.uniform(18, 33, n_asteroids)
        angles = np.random.uniform(0, 2*np.pi, n_asteroids)
        ast_pos = np.zeros((n_asteroids, 3))
        ast_pos[:,0] = radii * np.cos(angles)
        ast_pos[:,1] = radii * np.sin(angles)
        ast_pos[:,2] = np.random.normal(0, 1.0, n_asteroids)
        self.belt = gl.GLScatterPlotItem(pos=ast_pos, size=1.2, color=(0.5, 0.5, 0.5, 0.6), pxMode=True)
        self.view.addItem(self.belt)

        config = {
            'Mercury': (0.4, (0.7, 0.7, 0.7, 1)), 'Venus': (0.9, (0.9, 0.8, 0.5, 1)),
            'Earth': (1.0, (0.2, 0.4, 1.0, 1)), 'Moon': (0.3, (0.7, 0.7, 0.7, 1)),
            'Mars': (0.8, (0.8, 0.3, 0.1, 1)), 'Jupiter': (2.2, (0.8, 0.7, 0.5, 1)),
            'Saturn': (1.8, (0.8, 0.6, 0.4, 1)), 'Uranus': (1.5, (0.6, 0.9, 0.9, 1)),
            'Neptune': (1.4, (0.1, 0.2, 0.8, 1)), 'Pluto': (0.3, (0.5, 0.4, 0.3, 1)),
            'Ceres': (0.35, (0.6, 0.6, 0.5, 1))
        }

        for nome in self.df['corpo'].unique():
            if nome == 'Sun': continue
            r, c = config.get(nome, (0.2, (0.6, 0.6, 0.6, 1)))
            self.meshes[nome] = create_sphere(r, c)

    def _draw_rings(self, center, planet_name):
        if planet_name not in ["Saturn", "Uranus"]: return
        
        r_min, r_max = (2.5, 4.5) if planet_name == "Saturn" else (2.0, 3.0)
        color = (0.7, 0.6, 0.4, 0.3) if planet_name == "Saturn" else (0.5, 0.7, 1.0, 0.4)
        theta = np.linspace(0, 2*np.pi, 50)
        
        for r in np.linspace(r_min, r_max, 4):
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = np.zeros_like(theta)
            
            # --- CORREÇÃO DE INCLINAÇÃO ---
            if planet_name == "Uranus":
                # Rotaciona 90 graus no eixo X para ficar vertical/diagonal
                pts = np.vstack([x + center[0], z + center[1], y + center[2]]).transpose()
            else:
                # Saturno permanece horizontal
                pts = np.vstack([x + center[0], y + center[1], z + center[2]]).transpose()
                
            line = gl.GLLinePlotItem(pos=pts, color=color, width=1, antialias=True)
            self.view.addItem(line)
            self.render_objects['rings'].append(line)

    def update_frame(self, val):
        self.lbl.setText(f"FRAME: {val}")
        for r in self.render_objects['rings']: self.view.removeItem(r)
        self.render_objects['rings'] = []
        data = self.df[self.df['frame'] == val]
        for _, row in data.iterrows():
            nome = row['corpo']
            if nome in self.meshes:
                m = self.meshes[nome]
                m.resetTransform()
                m.translate(row['pos_x'], row['pos_y'], row['pos_z'])
                if nome in ["Saturn", "Uranus"]:
                    self._draw_rings([row['pos_x'], row['pos_y'], row['pos_z']], nome)
        self.belt.rotate(0.05, 0, 0, 1)

    def toggle_play(self):
        if self.play_timer.isActive(): 
            self.play_timer.stop()
            self.btn.setText("▶ PLAY")
        else: 
            self.play_timer.start(30)
            self.btn.setText("⏸ PAUSE")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = HarpiaPlayer("telemetria_solar_sphy.parquet")
    player.show()
    sys.exit(app.exec_())