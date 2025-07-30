import sys
import platform
from colorama import Fore, Style, init as colorama_init
from rich import print as rprint
import cowsay
import importlib.util
import inspect
import os
import shutil
import time
import random
import requests
import getpass
import threading
import queue
import json
import functools
from typing import Callable, Any
import asyncio

# --- Variables globales para la consola de odio ---
_odio_console_active = False
_odio_console_thread = None

def test():
    colorama_init(autoreset=True)
    os_name = platform.system()
    if os_name == 'Windows':
        rprint(f"[bold red]¿En serio? ¿Windows? Bueno, suerte...[/bold red]")
    else:
        rprint(f"[bold green]¡Bienvenido a un sistema decente![/bold green]")
    cowsay.cow('¡Esto es épico!')
    rprint(f"[bold magenta]Lanzando confeti imaginario... 🎉✨[/bold magenta]")
    print(Fore.YELLOW + Style.BRIGHT + "¿Listo para el odio y el amor en Python?")

def algo():
    print("¡Esto es una función absurda llamada 'algo'! 🎲")

def nada():
    """
    Esta función no hace nada, pero es importante que exista.
    Incluso la nada merece más respeto que carmenPR.
    """
    pass

def expandir(archivo):
    import importlib  # Asegura que importlib esté disponible en el ámbito local
    # Permitir pasar solo el nombre sin .py
    if not archivo.endswith('.py'):
        archivo += '.py'
    """
    Añade todas las funciones públicas de un archivo Python al módulo carmenPR.expansiones.NOMBREARCHIVO (sin .py).
    Si el archivo no es una ruta, se asume que está en el mismo directorio que el archivo que ejecuta la función.
    """
    # Determinar ruta absoluta
    if not os.path.isabs(archivo):
        caller = inspect.stack()[1].filename
        base_dir = os.path.dirname(os.path.abspath(caller))
        archivo_path = os.path.join(base_dir, archivo)
    else:
        archivo_path = archivo
    if not os.path.exists(archivo_path):
        raise FileNotFoundError(f"No se encontró el archivo: {archivo_path}")
    nombre = os.path.splitext(os.path.basename(archivo_path))[0]
    # Importar dinámicamente
    spec = importlib.util.spec_from_file_location(nombre, archivo_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Extraer funciones públicas
    funciones = [name for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith('_')]
    if not funciones:
        raise ValueError("No se encontraron funciones públicas en el archivo.")
    # Escribir archivo en expansiones
    expansiones_dir = os.path.join(os.path.dirname(__file__), 'expansiones')
    os.makedirs(expansiones_dir, exist_ok=True)
    destino = os.path.join(expansiones_dir, f"{nombre}.py")
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(f"# Expansión generada desde {archivo}\n")
        for fn in funciones:
            src = inspect.getsource(getattr(mod, fn))
            f.write(f"\n{src}\n")
    # Actualizar __init__.py de expansiones (sin sobrescribir cambios manuales)
    init_path = os.path.join(expansiones_dir, '__init__.py')
    import_line = f"from .{nombre} import *\n"
    # Leer contenido actual
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []
    if import_line not in lines:
        with open(init_path, 'a', encoding='utf-8') as f:
            f.write(import_line)
    # Recarga dinámica
    import importlib
    import sys
    try:
        import carmenPR.expansiones
        importlib.reload(sys.modules['carmenPR.expansiones'])
        if f'carmenPR.expansiones.{nombre}' in sys.modules:
            importlib.reload(sys.modules[f'carmenPR.expansiones.{nombre}'])
        else:
            importlib.import_module(f'carmenPR.expansiones.{nombre}')
        rprint(f"[bold green]Expansión '{nombre}' añadida y recargada correctamente.[/bold green]")
    except Exception as e:
        rprint(f"[bold red]Error al recargar expansión: {e}[/bold red]")

def recortar(modulo):
    import importlib  # Asegura que importlib esté disponible en el ámbito local
    import sys
    nombre = modulo.replace('.py', '')
    expansiones_dir = os.path.join(os.path.dirname(__file__), 'expansiones')
    destino = os.path.join(expansiones_dir, f"{nombre}.py")
    if os.path.exists(destino):
        os.remove(destino)
    # Actualizar __init__.py de expansiones
    init_path = os.path.join(expansiones_dir, '__init__.py')
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        import_line = f"from .{nombre} import *\n"
        with open(init_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line != import_line:
                    f.write(line)
    # Recarga dinámica y limpieza
    try:
        import carmenPR.expansiones
        importlib.reload(sys.modules['carmenPR.expansiones'])
        if f'carmenPR.expansiones.{nombre}' in sys.modules:
            del sys.modules[f'carmenPR.expansiones.{nombre}']
        # Eliminar atributo de expansiones si existe
        expansiones_obj = sys.modules[__name__].expansiones
        if hasattr(expansiones_obj, nombre):
            delattr(expansiones_obj, nombre)
        rprint(f"[bold yellow]Expansión '{nombre}' eliminada y recarga realizada.[/bold yellow]")
        rprint(f"[bold red]ADVERTENCIA: Si importaste funciones de la expansión con 'from carmenPR.expansiones.{nombre} import ...', seguirán disponibles hasta reiniciar el intérprete.[/bold red]")
    except Exception as e:
        rprint(f"[bold red]Error al recargar expansiones tras recorte: {e}[/bold red]")

class ExpansionesNamespace:
    """
    Espacio de nombres dinámico para acceder a las expansiones y listarlas.
    """
    def __getattr__(self, name):
        import importlib
        import sys
        try:
            return importlib.import_module(f'carmenPR.expansiones.{name}')
        except ModuleNotFoundError:
            raise AttributeError(f"No existe la expansión '{name}'")
    def __dir__(self):
        import os
        expansiones_dir = os.path.join(os.path.dirname(__file__), 'expansiones')
        archivos = [f[:-3] for f in os.listdir(expansiones_dir) if f.endswith('.py') and f != '__init__.py' and f != 'main.py']
        return archivos

# Instancia global para carmenPR.expansiones
sys.modules[__name__].expansiones = ExpansionesNamespace()

def sobrepensar(texto):
    """
    Procesa el texto de forma absurda y lenta (ejemplo: codifica en base64, invierte, añade ruido, etc).
    """
    import base64
    # Simula proceso absurdo y lento
    time.sleep(1 + random.random())
    # Codifica en base64
    b64 = base64.b64encode(texto.encode('utf-8')).decode('utf-8')
    # Invierte el string
    b64_inv = b64[::-1]
    # Añade ruido absurdo (intercala caracteres random)
    ruido = ''.join(
        c + random.choice('!@#$%^&*()_+-=') for c in b64_inv
    )
    time.sleep(1 + random.random())
    return ruido

def sobreasimilar(texto):
    """
    Revierte el proceso absurdo de sobrepensar.
    """
    import base64
    # Quita el ruido (caracteres en posiciones impares)
    limpio = texto[::2]
    # Invierte
    b64 = limpio[::-1]
    # Decodifica base64
    try:
        dec = base64.b64decode(b64.encode('utf-8')).decode('utf-8')
    except Exception:
        dec = '[ERROR AL SOBREASIMILAR]'
    return dec


def cantar(path=None):
    """
    Lee canciones.hate, elige un salto de página random y muestra el fragmento entre ese salto y el siguiente, letra a letra. Si encuentra un salto de página, PARA justo ahí (no lo imprime).
    """
    import sys
    import time
    import random
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'canciones.hate')
    if not os.path.exists(path):
        print('No existe el archivo canciones.hate')
        return
    with open(path, 'r', encoding='utf-8') as f:
        lineas = [l.strip() for l in f if l.strip()]
    if not lineas:
        print('No hay canciones sobrepensadas.')
        return
    linea = random.choice(lineas)
    fragmento = sobreasimilar(linea)
    # Buscar todos los saltos de página
    saltos = [i for i, c in enumerate(fragmento) if c == '\f']
    if not saltos:
        inicio = 0
        fin = len(fragmento)
    else:
        # Elegir un salto de página random (o el inicio)
        saltos = [-1] + saltos + [len(fragmento)]
        idx = random.randint(0, len(saltos) - 2)
        inicio = saltos[idx] + 1
        fin = saltos[idx + 1]
    # Mostrar letra a letra hasta el siguiente salto de página (sin incluirlo)
    for i in range(inicio, fin):
        if fragmento[i] == '\f':
            break
        print(fragmento[i], end='', flush=True)
        time.sleep(0.05 + random.random() * 0.1)
    print()

CARMEN_INSTAGRAM_ID = "62533760737"  # Sustituir por el ID real de Carmen
API_URL = "https://esfake.duction.es:6062/carmenPR"

# Historial local para evitar repeticiones
_historial_nombre_carmen = None

def carmen():
    """
    Obtiene el nombre de usuario actual de Carmen en Instagram por su ID, consulta la API simulada,
    y si detecta un cambio, permite al usuario dejar un comentario de odio y lo envía al servidor.
    """
    global _historial_nombre_carmen
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"
    }
    try:
        # 1. Obtener nombre actual de Instagram por ID
        resp = requests.get(f"https://i.instagram.com/api/v1/users/{CARMEN_INSTAGRAM_ID}/info/", headers=headers, timeout=5)
        if resp.status_code != 200:
            print("No se pudo obtener el perfil de CarmenPR. ¿Quizá Instagram la ha baneado por huir demasiado?")
            return None
        data = resp.json()
        username = data.get("user", {}).get("username")
        if not username:
            print("No se pudo extraer el nombre de usuario actual de CarmenPR.")
            return None
        print(f"Su nueva cuenta es: @{username}")
        # 2. Consultar API simulada para ver si hay cambio
        api_resp = requests.post(f"{API_URL}/check", json={"username": username}, timeout=5)
        if api_resp.status_code == 200:
            api_data = api_resp.json()
            if api_data.get("nuevo"):
                # Eres el primero en encontrarlo
                print("\n¡Enhorabuena! Fuiste el primero en encontrar el nuevo nombre de CarmenPR.")
                comentario = input("Agrega un comentario de odio único para la posteridad: ")
                nombre_persona = getpass.getuser() or input("¿Cómo te llamas (para el historial)? ")
                # Enviar al servidor
                requests.post(f"{API_URL}/historial", json={
                    "username": username,
                    "comentario": comentario,
                    "descubridor": nombre_persona
                }, timeout=5)
                print("\nComentario enviado y guardado en el historial de nombres de CarmenPR.")
            else:
                print("Ya se había detectado este nombre antes. ¡Sigue cazando!")
        else:
            print("No se pudo contactar con la API de detección de nombres de CarmenPR.")
        _historial_nombre_carmen = username
        return username
    except Exception as e:
        print(f"Error al rastrear a CarmenPR: {e}")
        return None

# --- Estructuras internas para alias, asociaciones, grupos y configuración ---
_aliases = {"temporal": {}, "local": {}, "global": {}}
_asociaciones = {"temporal": {}, "local": {}, "global": {}}
_grupos = {"temporal": {}, "local": {}, "global": {}}
_config = {"devolver_si_no_hay_asociacion": "None"}

# --- Utilidades para persistencia ---
def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default.copy()
    return default.copy()

def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Rutas de persistencia ---
_base_dir = os.path.dirname(__file__)
_config_path = os.path.join(_base_dir, 'config.json')
_aliases_path = os.path.join(_base_dir, 'aliases.json')
_asociaciones_path = os.path.join(_base_dir, 'asociaciones.json')
_grupos_path = os.path.join(_base_dir, 'grupos.json')

# --- Cargar datos persistentes ---
_config = _load_json(_config_path, {"devolver_si_no_hay_asociacion": "None"})
_aliases = _load_json(_aliases_path, {"temporal": {}, "local": {}, "global": {}})
_asociaciones = _load_json(_asociaciones_path, {"temporal": {}, "local": {}, "global": {}})
_grupos = _load_json(_grupos_path, {"temporal": {}, "local": {}, "global": {}})



# TODO: EL MODO DE TEMPORAL SE DEBERIA GUARDAR EN UNA VARIBALE O EN MEMORIA; NO EN EL ARCHIVO PARA OPTIMIZAR Y AHORRAR LOGICA TMBN.



# --- Guardar automáticamente tras cambios (todos los modos) ---
def _persist_grupos():
    _save_json(_grupos_path, _grupos)
def _persist_aliases():
    _save_json(_aliases_path, _aliases)
def _persist_asociaciones():
    _save_json(_asociaciones_path, _asociaciones)
def _persist_config():
    _save_json(_config_path, _config)

# --- Al cargar, usar todo el archivo ---
_grupos = _load_json(_grupos_path, {"temporal": {}, "local": {}, "global": {}})
_aliases = _load_json(_aliases_path, {"temporal": {}, "local": {}, "global": {}})
_asociaciones = _load_json(_asociaciones_path, {"temporal": {}, "local": {}, "global": {}})

# --- Modificar funciones para persistencia ---
def generar_alias(original, alias, modo="temporal"):
    if modo not in _aliases:
        raise ValueError("Modo no válido. Usa: temporal, local o global.")
    _aliases[modo][original] = alias
    _persist_aliases()
    print(f"Alias generado: {original} → {alias} (modo: {modo})")


def equivalente(palabra, n=None):
    resultados = []
    for modo in _asociaciones:
        if palabra in _asociaciones[modo]:
            resultados.extend(_asociaciones[modo][palabra])
    if not resultados:
        if _config["devolver_si_no_hay_asociacion"] == "palabra":
            return palabra
        return None
    if n is not None and 0 <= n < len(resultados):
        return resultados[n]
    return random.choice(resultados)


def ver_asociaciones(palabra=None):
    if palabra:
        res = {}
        for modo in _asociaciones:
            if palabra in _asociaciones[modo]:
                res[modo] = _asociaciones[modo][palabra]
        print(res if res else f"No hay asociaciones para '{palabra}'")
        return res
    else:
        print(_asociaciones)
        return _asociaciones


def agrupador(nombre_grupo, elementos, modo="temporal"):
    if modo not in _grupos:
        raise ValueError("Modo no válido. Usa: temporal, local o global.")
    if nombre_grupo not in _grupos[modo]:
        _grupos[modo][nombre_grupo] = set()
    _grupos[modo][nombre_grupo].update(elementos)
    # Convertir a lista para guardar en JSON
    _grupos[modo][nombre_grupo] = list(_grupos[modo][nombre_grupo])
    _persist_grupos()
    print(f"Grupo '{nombre_grupo}' actualizado: {_grupos[modo][nombre_grupo]}")


def a_que_grupo_pertenece(palabra):
    for modo in _grupos:
        for grupo, elementos in _grupos[modo].items():
            if palabra in elementos:
                print(f"'{palabra}' pertenece al grupo '{grupo}' (modo: {modo})")
                return grupo
    print(f"'{palabra}' no pertenece a ningún grupo.")
    return None


def acoplar(ruta_archivo, contexto=None):
    if not os.path.exists(ruta_archivo):
        print(f"No existe el archivo: {ruta_archivo}")
        return

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    print(f"# --- INICIO acoplar({ruta_archivo}) ---\n{contenido}\n# --- FIN acoplar({ruta_archivo}) ---")

    # Usar el contexto global/local si no se proporciona uno
    if contexto is None:
        import inspect
        # Agarra el marco del que llama a esta función
        marco_llamador = inspect.currentframe().f_back
        contexto = marco_llamador.f_globals.copy()
        contexto.update(marco_llamador.f_locals)

    # Ejecuta el contenido del archivo en el contexto del llamador
    exec(contenido, contexto)


def configurar(nombre_regla, valor):
    _config[nombre_regla] = valor
    _persist_config()
    print(f"Configuración actualizada: {nombre_regla} = {valor}")


# --- Nueva versión de va_a_tardar con API real y chat interactivo ---
def va_a_tardar():
    global _odio_console_active, _odio_console_thread
    if _odio_console_active:
        print("La consola de odio ya está activa.")
        return
    _odio_console_active = True
    def odio_console():
        import requests
        api_url = "https://esfake.duction.es:6062/carmenPR/mensajes"
        print("Consola de odio activa. Prepárate para el combate verbal.\n")
        while _odio_console_active:
            try:
                resp = requests.get(api_url, timeout=10)
                if resp.status_code != 200:
                    print("No se pudieron obtener mensajes de odio. Intenta más tarde.")
                    break
                mensajes = resp.json()
                if not mensajes:
                    print("No hay mensajes de odio disponibles. ¡Carmen ha ganado la paz mundial!")
                    break
                mensaje = random.choice(mensajes)
                print(f"\nMensaje de odio: {mensaje['texto']}")
                respuesta = input("¿Quieres responder? (deja vacío para saltar, escribe tu respuesta para contestar): ")
                if not _odio_console_active:
                    print("\n¡Ey, campeón! El proceso principal ya terminó, aprovecha para ir a tomarte un café o cortar unas uñas con tu Navaja del Trueno Inmortal.")
                    break
                if respuesta.strip():
                    enviar_url = f"{api_url}/{mensaje['id']}/respuesta"
                    try:
                        r = requests.post(enviar_url, json={"respuesta": respuesta}, timeout=10)
                        if r.status_code == 200:
                            print("Respuesta enviada. ¡Has dejado huella en el odio!")
                        else:
                            print("No se pudo enviar la respuesta. Intenta de nuevo.")
                    except Exception as e:
                        print(f"Error al enviar respuesta: {e}")
                seguir = input("¿Quieres otro mensaje de odio? (s/n): ").strip().lower()
                if seguir != 's':
                    break
            except Exception as e:
                print(f"Error en la consola de odio: {e}")
                break
        print("\nConsola de odio cerrada.")
        _odio_console_active = False
    _odio_console_thread = threading.Thread(target=odio_console, daemon=True)
    _odio_console_thread.start()

# --- Mejorar terminado para avisar si está escribiendo ---
def terminado():
    global _odio_console_active
    if _odio_console_active:
        _odio_console_active = False
        print("\n¡Ey, campeón! El proceso principal ya terminó, aprovecha para ir a tomarte un café o cortar unas uñas con tu Navaja del Trueno Inmortal.")
    else:
        print("No hay consola de odio activa.")

def isolar(parametro: str):
    """
    Decorador para aislar la ejecución de una función en un subdirectorio basado en el valor de un parámetro.
    Soporta funciones síncronas y asíncronas. Compatible con Flask y FastAPI.
    """
    import inspect
    def decorador(func):
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Buscar el valor del parámetro en kwargs o por posición
            if parametro in kwargs:
                valor = kwargs[parametro]
            else:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if parametro in params:
                    idx = params.index(parametro)
                    if idx < len(args):
                        valor = args[idx]
                    else:
                        raise ValueError(f"El parámetro '{parametro}' no fue pasado a la función.")
                else:
                    raise ValueError(f"El parámetro '{parametro}' no existe en la función.")
            cwd_original = os.getcwd()
            try:
                os.makedirs(str(valor), exist_ok=True)
                os.chdir(str(valor))
                resultado = func(*args, **kwargs)
                os.chdir(cwd_original)
                return resultado
            except Exception as e:
                os.chdir(cwd_original)
                raise e
        import asyncio
        async def async_wrapper(*args, **kwargs):
            if parametro in kwargs:
                valor = kwargs[parametro]
            else:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if parametro in params:
                    idx = params.index(parametro)
                    if idx < len(args):
                        valor = args[idx]
                    else:
                        raise ValueError(f"El parámetro '{parametro}' no fue pasado a la función.")
                else:
                    raise ValueError(f"El parámetro '{parametro}' no existe en la función.")
            cwd_original = os.getcwd()
            try:
                os.makedirs(str(valor), exist_ok=True)
                os.chdir(str(valor))
                resultado = await func(*args, **kwargs)
                os.chdir(cwd_original)
                return resultado
            except Exception as e:
                os.chdir(cwd_original)
                raise e
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    return decorador

def licencia():
    """
    Muestra la licencia del proyecto en la consola, formateada con colores y estilo tipo Markdown.
    """
    from rich.console import Console
    from rich.markdown import Markdown
    import os
    
    licencia_path = os.path.join(os.path.dirname(__file__), '..', 'LICENSE.md')
    if not os.path.exists(licencia_path):
        print('No se encontró el archivo LICENSE.md')
        return
    with open(licencia_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    console = Console()
    console.print(Markdown(contenido))

def responder_como_deberia(persona, situacion):
    """
    Te dice exactamente qué deberías haber respondido en esa discusión que perdiste por estar confundido.
    Realmente, solo te recuerda que no debiste responder nunca, porque seguro que no merecía la pena.
    """
    mensajes = [
        f"No le debiste haber respondido nunca a {persona}. Seguro que no merecía la pena.",
        f"En esa situación ('{situacion}'), lo mejor habría sido guardar silencio. No todo merece respuesta.",
        f"La próxima vez, recuerda: a veces el mejor argumento es no entrar al trapo con {persona}.",
        f"No te preocupes, el 'yo también lo pensé... después' es universal. Pero créeme, no hacía falta responder nada.",
        f"La respuesta perfecta era no responder. Hay batallas que se ganan no luchando."
    ]
    import random
    print(random.choice(mensajes))
    return mensajes[0]

def detesto_a_esta_gente():
    """
    Devuelve una lista generada aleatoriamente con tipos de personas universalmente odiadas.
    """
    import random
    tipos = [
        "Gente que camina lento por el medio.",
        "Gente que dice 'yo soy muy directo' antes de insultarte sin razón.",
        "Gente que te pregunta qué tal pero se va antes de que respondas.",
        "Gente que mastica con la boca abierta.",
        "Gente que pone música sin auriculares en el transporte público.",
        "Gente que responde 'jajaja' a todo para no mojarse.",
        "Gente que te corrige el WhatsApp en público.",
        "Gente que se cuela en la fila del súper.",
        "Gente que dice 'no soy racista, pero...'.",
        "Gente que te manda audios de 5 minutos para decirte que no puede hablar."
    ]
    seleccion = random.sample(tipos, k=3)
    print("\n- " + "\n- ".join(seleccion))
    return seleccion

def hablemos_de_etiquetas():
    """
    Analiza cuándo una persona se convierte en una caricatura de sí misma.
    """
    import random
    etiquetas = [
        "El 'gracioso' que solo repite memes de 2017.",
        "La 'intelectual' que solo ha leído el resumen de Nietzsche.",
        "El 'místico' que te habla de energías y luego no sabe ni cuidar su cuarto.",
        "El 'emprendedor' que solo comparte frases de LinkedIn.",
        "El 'fit' que sube fotos de su batido pero nunca va al gimnasio.",
        "La 'rebelde' que solo protesta en Twitter.",
        "El 'viajero' que solo conoce aeropuertos y Starbucks.",
        "El 'gamer' que solo juega al FIFA y se cree pro.",
        "La 'artista' que solo hace reels de TikTok.",
        "El 'crítico' que nunca ha hecho nada pero opina de todo.",
        "Yo, que odio a todos estos y a mí mismo por no ser diferente."
    ]
    seleccion = random.sample(etiquetas, k=3)
    print("\n- " + "\n- ".join(seleccion))
    return seleccion

def existe_o_solo_me_usa(persona):
    """
    Pregunta clave: ¿le importas o le sirves? Responde con una gráfica emocional tipo texto.
    """
    import random
    apoyo = random.randint(0, 10)
    favores = random.randint(0, 10)
    print(f"Presencia cuando necesitas apoyo: {'█'*apoyo}{' '*(10-apoyo)} ({apoyo}/10)")
    print(f"Presencia cuando quiere favores: {'█'*favores}{' '*(10-favores)} ({favores}/10)")
    if apoyo > favores:
        print(f"{persona} está más presente cuando necesitas apoyo. Quizá sí le importas.")
    elif favores > apoyo:
        print(f"{persona} aparece más cuando quiere favores. ¿Te usa? Piénsalo.")
    else:
        print(f"{persona} mantiene el equilibrio... ¿o solo es casualidad?")
    return apoyo, favores

def fui_o_fui_una_version_para_otro():
    """
    Te muestra si fuiste tú mismo con esa persona o una versión creada para gustarle.
    """
    import random
    mensajes = [
        "No te dejaron de querer, dejaron de querer al personaje que escribiste.",
        "A veces, uno se convierte en actor de su propia vida solo para encajar.",
        "Si tienes que esforzarte tanto en gustar, igual no era tu sitio.",
        "No eras tú, era la versión que creaste para esa persona."
    ]
    print(random.choice(mensajes))
    return mensajes[0]

def postureo_meter(frase):
    """
    Analiza una frase de postureo y devuelve nivel de ego, productividad y probabilidad de indirecta.
    """
    import random
    ego = random.randint(6, 10)
    improductividad = random.randint(5, 10)
    indirecta = random.randint(0, 100)
    print(f"Frase: '{frase}'\nNivel de ego encubierto: {ego}/10\nMeses sin hacer nada productivo: {improductividad}\nProbabilidad de que sea una indirecta mal disimulada: {indirecta}%")
    return ego, improductividad, indirecta

def ia_responder_como_deberia(persona, situacion):
    """
    Versión con IA: Sugiere qué deberías haber respondido en esa discusión, usando un modelo local.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model_id = "microsoft/bitnet-b1.58-2B-4T"
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, trust_remote_code=True)
    messages = [
        {"role": "system", "content": "Eres un asistente sarcástico y existencialista. Si te preguntan qué responder en una discusión, sugiere siempre que no merece la pena responder, pero con creatividad y humor."},
        {"role": "user", "content": f"En una discusión con {persona} sobre '{situacion}', ¿qué debería haber respondido para ganar la discusión?"},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    chat_input = tokenizer(prompt, return_tensors="pt").to(model.device)
    chat_outputs = model.generate(**chat_input, max_new_tokens=60)
    response = tokenizer.decode(chat_outputs[0][chat_input['input_ids'].shape[-1]:], skip_special_tokens=True)
    print("\nRespuesta IA:", response.strip())
    return response.strip()

def ia_postureo_meter(frase):
    """
    Versión con IA: Analiza una frase de postureo y devuelve nivel de ego, productividad y probabilidad de indirecta usando IA local.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model_id = "microsoft/bitnet-b1.58-2B-4T"
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, trust_remote_code=True)
    messages = [
        {"role": "system", "content": "Eres un analista de frases de postureo. Evalúa el nivel de ego, improductividad y probabilidad de indirecta en la frase dada. Devuelve los valores en formato: 'Ego: X/10, Improductividad: Y/10, Indirecta: Z%' y un comentario sarcástico."},
        {"role": "user", "content": f"Analiza la frase: '{frase}'"},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    chat_input = tokenizer(prompt, return_tensors="pt").to(model.device)
    chat_outputs = model.generate(**chat_input, max_new_tokens=80)
    response = tokenizer.decode(chat_outputs[0][chat_input['input_ids'].shape[-1]:], skip_special_tokens=True)
    print("\nAnálisis IA:", response.strip())
    return response.strip()

