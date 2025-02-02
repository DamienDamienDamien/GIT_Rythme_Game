from libraries import *

def listen(file_path):
    print(file_path)
    # Charger le fichier audio à l'aide de soundfile
    try:
        # Ouvrir le fichier audio
        data, samplerate = sf.read(file_path)
        
        # Lire le fichier audio avec sounddevice
        print(f"Lecture du fichier audio : {file_path}")
        sd.play(data, samplerate)
        
        # Attendre la fin de la lecture
        sd.wait()  # Attente que la lecture soit terminée
        print("Lecture terminée.")
        
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier audio : {e}")