import os
from flask import Flask, jsonify, request, Response, render_template, send_from_directory, abort
from datetime import datetime
import cv2
import numpy as np

app = Flask(__name__, static_folder="upload", static_url_path="/upload")

UPLOAD_FOLDER = '/home/mihe3492/testDjango/upload'
SAVE_FOLDER = 'saved_images'
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    
    
content1 = """#EXT-X-DISCONTINUITY
#EXTINF:8.00
segment_000.ts"""



content2 = """#EXT-X-DISCONTINUITY
#EXTINF:8.00
segment_00.ts"""



# Compteur pour les images reçues
image_counter = 0

moves_data = [
        {"move_number": 1, "player": "Nord", "action": "Enchère 1 Cœur", "result": "Acceptée"},
        {"move_number": 2, "player": "Est", "action": "Passe", "result": "Acceptée"},
        {"move_number": 3, "player": "Sud", "action": "Enchère 2 Cœurs", "result": "Acceptée"},
        {"move_number": 4, "player": "Ouest", "action": "Passe", "result": "Acceptée"},
        # Add more moves as needed
    ]
table_streams = {
    '1': {
        'url': 'https://fastmedia-yu-gi-oh-4-fr.rakuten.wurl.tv/playlist.m3u8',
        'description': 'Plongez dans une partie captivante, où chaque coup est un défi stratégique.'
    },
    '2': {
        'url': 'https://devstreaming-cdn.apple.com/videos/streaming/examples/adv_dv_atmos/main.m3u8',
        'description': 'Suivez les mouvements serrés de joueurs expérimentés dans cette partie palpitante.'
    },
    '3': {
        'url': '/upload/playlist.m3u8',
        'description': "Assistez à un duel d'experts où chaque carte jouée peut faire basculer la victoire."
    }
}



# Créer un endpoint pour recevoir le flux vidéo
@app.route('/', methods=['GET'])
def main_():
    return render_template('index.html',moves_data=moves_data,table_streams=table_streams)

@app.route('/comment-jouer', methods=['GET'])
def jouer():
    return render_template('comment_jouer.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/confidentialite', methods=['GET'])
def confidentialite():
    return render_template('politique_confidentialite.html')

@app.route('/utilisation', methods=['GET'])
def utilisation():
    return render_template('conditions_utilisation.html')

@app.route('/recent', methods=['GET'])
def recent():
    return render_template('videos_recents.html',moves_data=moves_data)

@app.route('/direct', methods=['GET'])
def direct():
    return render_template('diffusions_en_direct.html',table_streams=table_streams)

# Dictionnaire pour les URLs des flux vidéo par table

@app.route('/table/<table_id>/summary')
def table_summary(table_id):
    # Fetch or generate game moves data based on the table ID
    # For demonstration purposes, let's assume this is a list of dictionaries
    
    return render_template('table_summary.html', table_id=table_id, moves_data=moves_data)


@app.route('/table/<table_id>')
def table(table_id):
    stream_url, desc = getInfo(table_id)
    
    return render_template('table.html', stream_url=stream_url, table_id=table_id,desc=desc)

def getInfo(table_id):
    table_info = table_streams.get(table_id)
    stream_url = table_info['url']
    desc = table_info['description']
    if not stream_url:
        return "Table non disponible", 404
    return stream_url, desc

    
@app.route('/download/apk', methods=['GET'])
def download_apk():
    filename = 'app-debug.apk'
    try:
        # Vérifiez si le fichier existe
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.isfile(file_path):
            return abort(404)  # Renvoie une erreur 404 si le fichier n'existe pas

        # Envoie le fichier pour téléchargement
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True, mimetype='application/vnd.android.package-archive')
    except Exception as e:
        # Gère les erreurs possibles
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Lire le contenu actuel de `playlist1.m3u8` ou créer le fichier s'il n'existe pas
        playlist_path = "upload/playlist1.m3u8"
        if os.path.exists(playlist_path):
            with open(playlist_path, "r") as file2:
                lines = file2.readlines()
        else:
            lines = ["#EXTM3U\n", "#EXT-X-VERSION:3\n", "#EXT-X-TARGETDURATION:8\n"]

        # Sélectionner le contenu à insérer en fonction du fichier reçu
        new_content = content1 if file.filename == "segment_000.ts" else content2

        # Trouver l'index où insérer les nouvelles lignes
        insert_index = None
        for i, line in enumerate(lines):
            if "#EXT-X-PLAYLIST-TYPE:EVENT" in line:
                insert_index = i
                break

        # Ajouter le nouveau contenu au bon emplacement
        if insert_index is not None:
            lines.insert(insert_index, new_content + "\n")
        else:
            lines.append(new_content + "\n")

        # Réécrire le contenu mis à jour dans `playlist1.m3u8`
        with open(playlist_path, "w") as file2:
            file2.writelines(lines)

        return jsonify({"success": "File uploaded and playlist updated"}), 200

if __name__ == '__main__':
    app.run(debug=True)
