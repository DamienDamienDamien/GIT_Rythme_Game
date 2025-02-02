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
import soundfile as sf
import sounddevice as sd
import random
