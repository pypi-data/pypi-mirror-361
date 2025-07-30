from .PR import *
from . import expansiones
import threading
import requests
import json
import hashlib
import os

def _mostrar_mensaje_carmenPR():
    try:
        resp = requests.get('https://esfake.duction.es:6062/carmenPR/mensaje', timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data and 'mensaje' in data and 'color' in data and 'tipo' in data:
                from rich import print as rprint
                color = data['color']
                mensaje = data['mensaje']
                tipo = data['tipo']
                # Identificador único del mensaje
                msg_id = hashlib.sha256((mensaje + color + tipo).encode('utf-8')).hexdigest()
                state_file = os.path.join(os.path.expanduser('~'), '.carmenpr_mensaje')
                mostrado = None
                if os.path.exists(state_file):
                    with open(state_file, 'r', encoding='utf-8') as f:
                        mostrado = f.read().strip()
                if tipo == 'momentaneo':
                    if mostrado == msg_id:
                        return  # Ya se mostró este mensaje momentáneo
                    with open(state_file, 'w', encoding='utf-8') as f:
                        f.write(msg_id)
                rprint(f"[bold {color}]{mensaje}[/bold {color}]")
    except Exception:
        pass  # Silencioso ante cualquier error

def _solicitar_mensaje_al_iniciar():
    hilo = threading.Thread(target=_mostrar_mensaje_carmenPR, daemon=True)
    hilo.start()

_solicitar_mensaje_al_iniciar()
