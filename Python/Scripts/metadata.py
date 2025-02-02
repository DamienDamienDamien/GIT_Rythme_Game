from libraries import *

def modify_names(self, direction):
    for row in range(self.table.rowCount()):
        checkbox = self.table.cellWidget(row, 0)

        if checkbox.isChecked():
            current_name_item = self.table.item(row, 1)
            current_name = current_name_item.text()
            
            # Séparer la ligne a l'endroit ou le "_" se trouve
            parts = current_name.split("_")
            # Verifier si la deuxieme partie est un chiffre
            if len(parts) > 1 and parts[-1].isdigit():
                marker_number = parts[-1]
            else:
                # Utiliser le numéro de la ligne par défault
                marker_number = str(row + 1)
            
            new_name = f"{direction}_{marker_number}"
            current_name_item.setText(new_name)


def shuffle(self):
    directions = ["Haut", "Bas", "Gauche", "Droite"]
    for row in range(self.table.rowCount()):
        checkbox = self.table.cellWidget(row, 0)

        if checkbox.isChecked():
            current_name_item = self.table.item(row, 1)
            current_name = current_name_item.text()
            
            parts = current_name.split("_")
            
            if len(parts) > 1 and parts[-1].isdigit():
                marker_number = parts[-1]
            else:
                marker_number = str(row + 1)

            new_name = f"{random.choice(directions)}_{marker_number}"
            current_name_item.setText(new_name)


def update_table_new(self):
    if self.peak_times is None or self.peak_amps is None:
        return
    self.table.setRowCount(0)
    for i, (t, a) in enumerate(zip(self.peak_times, self.peak_amps)):

        checkbox = QCheckBox()
        checkbox.setChecked(True)
        formatted_time = self.format_time(t)
        m_name = f"marqueur_{str(i+1).zfill(4)}"
        self.table.insertRow(i)
        name_item = QTableWidgetItem(m_name)
        self.table.setCellWidget(i, 0, checkbox)
        self.table.setItem(i, 1, name_item)
        self.table.setItem(i, 2, QTableWidgetItem(formatted_time))
        self.table.setItem(i, 3, QTableWidgetItem(f"{a:.2f}"))

