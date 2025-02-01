from pathlib import Path
import librosa
import numpy as np
import matplotlib.pyplot as plt
import sys
from PySide6.QtWidgets import (QApplication, QCheckBox, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QProgressBar, QTabWidget, QSpacerItem, QSizePolicy,QGroupBox, QFrame)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QDoubleValidator
import csv
import subprocess

#_______________________________________________INTERFACE____________________________________________________________________________________________
class UIapp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(470, 650)
        self.setWindowTitle("Damien's Peak detector")
        self.waveform_files = ["drums", "bass", "vocals", "other"]

        # Variable bouton importants
        self.button_color = "#7da5ff"
        self.label_color = "#c2c2c2"
        self.black_color = "#000000"
        self.white_color = "#ffffff"

        # Layout principal
        main_layout = QVBoxLayout()
        self.main_tab = QWidget()
        main_layout.addWidget(self.main_tab)
        self.shared_area = QWidget()
        self.create_shared_area()
        main_layout.addWidget(self.shared_area)

        # Configurer le layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_shared_area(self):
            
            #___________zone 1 _______________________
            layout = QVBoxLayout()
            verticalZ1_layout = QVBoxLayout()
            verticalZ2_layout = QVBoxLayout()
            check_layout = QHBoxLayout()
            selection_layout = QHBoxLayout()
            direction_layout = QHBoxLayout()

            # Bouton 1 INPUT
            self.button_input = QPushButton("Entrez un son")
            self.button_input.clicked.connect(self.choose_input)
            verticalZ1_layout.addWidget(self.button_input)
            self.label_input = QLabel("Aucun Input sélectionné")
            verticalZ1_layout.addWidget(self.label_input)

            # Bouton 2 OUTPUT
            self.button_output = QPushButton("Entrez l'emplacement de sauvegarde")
            self.button_output.clicked.connect(self.choose_output)
            verticalZ1_layout.addWidget(self.button_output)
            self.label_output = QLabel("Aucun output sélectionné")
            verticalZ1_layout.addWidget(self.label_output)

            # _______________Conteneur activable_______________
            container_widget = QWidget()
            container_widget.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
            container_widget_layout = QVBoxLayout()
            container_widget.setLayout(container_widget_layout)

            # Activer/désactiver les boutons
            self.checkbox_enable_multipiste = QCheckBox("Multi-piste")
            self.checkbox_enable_multipiste.clicked.connect(self.toggle_secondary_area)
            container_widget_layout.addWidget(self.checkbox_enable_multipiste)

            # Bouton séparer
            self.button_separate = QPushButton("Séparer")
            self.button_separate.setEnabled(False)
            self.button_separate.clicked.connect(self.separate)
            self.button_separate.setStyleSheet(f"background-color: #dbdbdb; color: {self.label_color};")
            container_widget_layout.addWidget(self.button_separate)

            # Barre de progression de l'analyse
            self.progress_bar_separate = QProgressBar()
            self.progress_bar_separate.setValue(0)
            container_widget_layout.addWidget(self.progress_bar_separate)

            # Checkboxes des pistes
            self.track_checkboxes = {}
            for track_name in self.waveform_files:
                checkbox = QCheckBox(track_name) 
                checkbox.clicked.connect(self.track_selected)
                self.track_checkboxes[track_name] = checkbox
                checkbox.setEnabled(False)
                checkbox.setStyleSheet(f"color: {self.label_color};")
                check_layout.addWidget(checkbox, alignment=Qt.AlignCenter)

            self.separated_folder = None
            container_widget_layout.addLayout(check_layout)
            layout.addLayout(verticalZ1_layout)
            layout.addWidget(container_widget)
            self.main_tab.setLayout(layout)

            #___________Zone 2_______________

            container_bas = QWidget()
            container_bas.setStyleSheet("background-color: #c4d6ff; border-radius: 5px;")
            container_bas_layout = QVBoxLayout()
            container_bas.setLayout(container_bas_layout)

            # Champ de saisie marge
            self.label_marge = QLabel("Ajuster le seuil de d'amplitude :")
            container_bas_layout.addWidget(self.label_marge)
            self.edit_marge = QLineEdit()
            self.edit_marge.setStyleSheet(f"background-color: {self.white_color};")
            self.edit_marge.setText("0.05")
            container_bas_layout.addWidget(self.edit_marge)

            # Bouton Analyser
            self.button_analyse = QPushButton("Analyser")
            self.button_analyse.clicked.connect(self.audio_analyse)
            self.button_analyse.setStyleSheet(f"background-color: {self.button_color};")
            container_bas_layout.addWidget(self.button_analyse)

            # Barre de progression de l'analyse
            self.progress_bar_analyse = QProgressBar()
            self.progress_bar_analyse.setValue(0)
            container_bas_layout.addWidget(self.progress_bar_analyse)

            # Champ de saisie nom du graph
            self.label_save = QLabel("Entrez le nom du graph :")
            container_bas_layout.addWidget(self.label_save)
            self.edit_save = QLineEdit()
            self.edit_save.setText(f"{Path(self.label_input.text()).stem}_graph.png")
            self.edit_save.setStyleSheet(f"background-color: {self.white_color};")
            container_bas_layout.addWidget(self.edit_save)

            # Bouton graph
            self.button_graph = QPushButton("Afficher le graph")
            self.button_graph.clicked.connect(self.show_graph)
            self.button_graph.setStyleSheet(f"background-color: {self.button_color};")
            container_bas_layout.addWidget(self.button_graph)

            # Bouton pour créer un fichier csv
            self.button_csv = QPushButton("Créer les metadonnees (.csv)")
            self.button_csv.clicked.connect(self.create_csv_file)
            self.button_csv.setStyleSheet(f"background-color: {self.button_color};")
            container_bas_layout.addWidget(self.button_csv)

            # Résultats de l'analyse
            self.result_label = QLabel("Résultats de l'analyse :")
            container_bas_layout.addWidget(self.result_label)

            # Tableau des résultats de l'analyse
            self.table = QTableWidget()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Selection", "Name", "Time", "Amplitude"])
            container_bas_layout.addWidget(self.table)

            # Bouton pour tout sélectionner
            self.select_all_button = QPushButton("Tout sélectionner")
            self.select_all_button.clicked.connect(self.select_all)
            self.select_all_button.setStyleSheet(f"background-color: {self.white_color};")
            selection_layout.addWidget(self.select_all_button)

            # Bouton pour tout désélectionner
            self.deselect_all_button = QPushButton("Tout désélectionner")
            self.deselect_all_button.clicked.connect(self.deselect_all)
            self.deselect_all_button.setStyleSheet(f"background-color: {self.white_color};")
            selection_layout.addWidget(self.deselect_all_button)

            # Boutons pour modifier les noms des marqueurs
            directions = {
                "Haut": "#ff9970",
                "Bas": "#79f780",
                "Gauche": "#8585ff",
                "Droite": "#ff87c1",
                }
            
            for direction, color in directions.items():
                button_direction = QPushButton(direction)
                button_direction.setStyleSheet(f"background-color: {color};")
                button_direction.clicked.connect(lambda _, dir=direction: self.modify_names(dir))
                direction_layout.addWidget(button_direction)

            container_bas_layout.addLayout(direction_layout)
            container_bas_layout.addLayout(selection_layout)
            verticalZ2_layout.addWidget(container_bas)
            layout.addLayout(verticalZ2_layout)
            self.shared_area.setLayout(layout)

#_______________________________FONCTIONS_________________________________

    # activation/désactivation des boutons
    def toggle_secondary_area(self):
        is_checked = self.checkbox_enable_multipiste.isChecked()
        state_color = self.black_color if is_checked else self.label_color
        button_style = f"background-color: {self.button_color if is_checked else '#dbdbdb'}; color: {state_color};"
        
        self.button_separate.setEnabled(is_checked)
        self.button_separate.setStyleSheet(button_style)
        self.checkbox_enable_multipiste.setStyleSheet(f"color: {state_color};")
        
        for checkbox in self.track_checkboxes.values():
            checkbox.setEnabled(is_checked)
            checkbox.setStyleSheet(f"color: {state_color};")
    
        if not is_checked:
            self.selected_track = None
            for checkbox in self.track_checkboxes.values():
                checkbox.setChecked(False)

    #Récuperer l'input
    def choose_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier")
        if file_path:
            self.label_input.setText(f"{file_path}")
             # Extraire le nom du fichier sans l'extension
        file_name = Path(file_path).stem
        # Mettre à jour le champ de saisie pour le nom du graphe
        self.edit_save.setText(f"{file_name}_graph.png")

    #Récuperer l'output
    def choose_output(self):
        file_path = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if file_path:
            self.label_output.setText(f"{file_path}")

    #Formater les secondes en HH:MM:SS
    def format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        
    def audio_analyse(self):
        # Verifier si le mode multipiste est activé
        if self.checkbox_enable_multipiste.isChecked():
            if not hasattr(self, 'selected_track') or self.selected_track is None:
                return
            track_path = Path(self.separated_folder) / f"{self.selected_track}.wav"
        else:
            track_path = Path(self.label_input.text())

        # Récupérer les infos depuis l'interface
        input_file = str(track_path)
        output_dir = self.label_output.text()
        threshold_margin = float(self.edit_marge.text())
        self.progress_bar_analyse.setValue(10)
        signal, sample_rate = librosa.load(input_file, sr=None)
        print(f"Signal shape: {signal.shape}, Sample rate: {sample_rate}")

        # Calculer la STFT et identifier les pics
        self.progress_bar_analyse.setValue(30)
        amplitude = np.abs(librosa.stft(signal))
        self.times = librosa.frames_to_time(range(amplitude.shape[1]), sr=sample_rate, hop_length=512)
        self.amplitudes = np.max(amplitude, axis=0)
        
        # Identifier le seuil
        self.progress_bar_analyse.setValue(60)
        max_amp = np.max(self.amplitudes)
        threshold = max_amp * (1 - threshold_margin)
        
        # Identifier les pics
        self.progress_bar_analyse.setValue(80)
        self.peak_times = self.times[self.amplitudes >= threshold]
        self.peak_amps = self.amplitudes[self.amplitudes >= threshold]
        
        print(f"Amplitude maximale : {max_amp:.2f} dB")
        print(f"Nombre de pics trouvés : {len(self.peak_times)}")
        self.progress_bar_analyse.setValue(100)
        
        self.result_label.setText(f"Amplitude maximale : {max_amp:.2f} dB\nNombre de pics trouvés : {len(self.peak_times)}")
        self.update_table()

    def show_graph(self):
        if self.peak_times is None or self.peak_amps is None:
            print("Erreur : veuillez d'abord analyser l'audio.")
            return
        
        # Affichage des résultats
        plt.figure(figsize=(20, 4))
        plt.plot(self.times, self.amplitudes, label="Amplitude", color="blue")
        plt.scatter(self.peak_times, self.peak_amps, color='red', zorder=5, label="Max Amplitude Points")
        
        # Ajouter des lignes verticales pour chaque pic
        for t in self.peak_times:
            plt.axvline(t, color='red', linestyle='--', alpha=0.6)
        
        plt.xlabel('Temps [s]')
        plt.ylabel('Amplitude')
        plt.title('Amplitude en fonction du temps avec détection des pics')
        plt.legend(loc='upper right')
        plt.grid()

        # Vérifier si un dossier de sortie est spécifié et qu'il existe
        output_dir = self.label_output.text()
        if output_dir:
            output_path = Path(output_dir) / self.edit_save.text()
            if Path(output_dir).exists():
                plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
                print(f"Graphique enregistré dans : {output_path}")
        plt.show()

    def update_table(self):
        if self.peak_times is None or self.peak_amps is None:
            return
        self.table.setRowCount(0)
        for i, (t, a) in enumerate(zip(self.peak_times, self.peak_amps)):

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            formatted_time = self.format_time(t)
            m_name = f"marqueur_{i+1}"
            self.table.insertRow(i)
            name_item = QTableWidgetItem(m_name)
            self.table.setCellWidget(i, 0, checkbox)
            self.table.setItem(i, 1, name_item)
            self.table.setItem(i, 2, QTableWidgetItem(formatted_time))
            self.table.setItem(i, 3, QTableWidgetItem(f"{a:.2f}"))

    def select_all(self):
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            checkbox.setChecked(True)

    def deselect_all(self):
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            checkbox.setChecked(False)

    def modify_names_up(self):
        self.modify_names("Haut")

    def modify_names_down(self):
        self.modify_names("Bas")

    def modify_names_left(self):
        self.modify_names("Gauche")

    def modify_names_right(self):
        self.modify_names("Droite")

    def modify_names(self, direction):
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox.isChecked():
                current_name_item = self.table.item(row, 1)
                current_name = current_name_item.text()
                new_name = f"{direction}"
                current_name_item.setText(new_name)

    def create_csv_file(self):
        if self.peak_times is None or self.peak_amps is None:
            print("Erreur : veuillez d'abord analyser l'audio.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer un fichier CSV", "", "CSV Files (*.csv)")
        
        if file_path:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file, delimiter='\t')
                    writer.writerow(["Name", "Start", "Duration Time", "Format", "Type", "Description"])
                    total_duration = self.format_time(self.times[-1]) if self.times is not None else "00:00:00"  # Durée totale de l'audio
                    
                    for row in range(self.table.rowCount()):
                        custom_name = self.table.item(row, 1).text()
                        peak_time = self.peak_times[row] if row < len(self.peak_times) else 0
                        formatted_time = self.format_time(peak_time)
                        description = ""
                        m_type = "Cue"
                        format = "decimal"
                        duration = "00:00:00"
                        writer.writerow([custom_name, formatted_time, duration, format, m_type, description])
                    print(f"Fichier texte créé : {file_path}")

    def track_selected(self, checked):
        checkbox = self.sender()
        track_name = checkbox.text()
        
        if checked:
            self.selected_track = track_name
        else:
            if self.selected_track == track_name:
                self.selected_track = None

    def separate(self):
        self.progress_bar_separate.setValue(0)
        input_file = self.label_input.text()
        output_dir = self.label_output.text()

        if self.separated_folder and Path(self.separated_folder).exists():
            print(f"Les pistes ont déjà été séparées : {self.separated_folder}")
            return self.separated_folder

        self.progress_bar_separate.setValue(99)
        subprocess.run(["demucs", "-o", output_dir, input_file])
        base_name = Path(input_file).stem
        separated_folder = Path(output_dir) / "htdemucs" / base_name
        self.progress_bar_separate.setValue(100)
        self.separated_folder = separated_folder
        print(f"Pistes séparées dans : {self.separated_folder}")
        return separated_folder
    
    def plot_waveforms(self, file_path):
        audio, sr = librosa.load(file_path, sr=None)
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(audio, sr=sr, alpha=0.8)
        plt.title(f"Amplitude de la piste : {Path(file_path).stem}")
        plt.xlabel("Temps (s)")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()

    def plot_waveform_by_track(self, track_name):
        if not self.separated_folder:
            print("Erreur : Veuillez séparer les pistes d'abord.")
            return
        
        track_path = Path(self.separated_folder) / f"{track_name}.wav"
        if not track_path.exists():
            print(f"Erreur : Le fichier {track_path} n'existe pas.")
            return
        
        self.plot_waveforms(track_path)
        
#__________________EXECUTE_________________

if __name__ == "__main__":
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    window = UIapp()
    window.show()
    sys.exit(app.exec())
