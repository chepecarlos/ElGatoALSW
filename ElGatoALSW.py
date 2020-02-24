#!/usr/bin/env python3

# Librerias
import os
import threading
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from pynput.keyboard import Key, Controller
import time
import json

# Cargar Teclado
keyboard = Controller()

teclas = "nada"
folder = ""
fuente = "."

# Recusos para sistema
FolderRecursos = os.path.join(os.path.dirname(__file__), "Recusos")

Estado = -1

with open('Comandos.json') as f:
    data = json.load(f)

Comandos = [["Arduino", [["Verificar", [Key.ctrl, "r"]], ["Salvar", [Key.ctrl, "s"]]]]]



def ObtenerImagen(deck, key, state):

    if Estado == -1:
        name = "{}".format(data['Comando'][key]['Nombre'])
        icon = "{}{}.png".format(Comandos[key][0],"P" if state else "R")
        font = "Roboto-Regular.ttf"
        label = "{}".format(Comandos[key][0])
    else:
        if key == deck.key_count() -1:
            name = "Salir"
            icon = "Salir.png"
            font = "Roboto-Regular.ttf"
            label = "Salir"
        else:
            name = "{}".format(Comandos[Estado][1][key][0])
            icon = "{}/{}{}.png".format(Comandos[Estado][0], Comandos[Estado][1][key][0], "P" if state else "R")
            font = "Roboto-Regular.ttf"
            label = "{}".format(Comandos[Estado][1][key][0])

    return {
        "name": name,
        "icon": os.path.join(FolderRecursos, icon),
        "font": os.path.join(FolderRecursos, font),
        "label": label
    }

#
def CargarImagen(deck, icon_filename, font_filename, label_text, titulo = False):
    # Create new key image of the correct dimensions, black background.
    image = PILHelper.create_image(deck)
    # Resize the source image asset to best-fit the dimensions of a single key,
    # and paste it onto our bCargarImagenlank frame centered as closely as possible.
    icon = Image.open(icon_filename).convert("RGBA")
    if titulo:
        icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
    else:
        icon.thumbnail((image.width, image.height), Image.LANCZOS)
    icon_pos = ((image.width - icon.width) // 2, 0)
    image.paste(icon, icon_pos, icon)

    # Load a custom TrueType font and Comandosuse it to overlay the key index, draw key
    # label onto the image.
    if titulo:
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")
    return PILHelper.to_native_format(deck, image)


# Actualizar
def CambiarImagen(deck, key, state, titulo = False):

    # Obtener Imagen
    ImagenEstilo = ObtenerImagen(deck, key, state)
    #
    Imagen = CargarImagen(deck, ImagenEstilo["icon"], ImagenEstilo["font"], ImagenEstilo["label"],titulo)

    deck.set_key_image(key, Imagen)

# Funciones de Teclado

def PrecionarTecla(deck, key, state):
    global Estado
    if Estado == -1:
        if key < len(Comandos):
            print("Boton {} = {}".format(Comandos[key][0], state), flush=True)
            CambiarImagen(deck, key, state)
            Estado = key
            for key in range(len(Comandos[key][1])):
                CambiarImagen(deck, key, False)
            CambiarImagen(deck, deck.key_count() - 1  , False, False)
        else:
            print("Teclado no programada")
    else:
        if key == deck.key_count() -1:
            deck.reset()
            Estado = -1;
            for key in range(len(Comandos)):
                CambiarImagen(deck, key, False)
            print("Regresar")
        elif key < len(Comandos[Estado][1]):
            print("Boton {} = {}".format(Comandos[Estado][1][key][0], state), flush=True)
            CambiarImagen(deck, key, state)
            if state:
                ComandoTeclas(Comandos[Estado][1][key][1])
        else:
            print("Teclado no programada")
    if state:
        time.sleep(0.25)



def ComandoTeclas(Teclas):
    for tecla in Teclas:
        keyboard.press(tecla)

    for tecla in Teclas:
        keyboard.release(tecla)

def ActualizarImagen(deck, teclas, tecla):
    global folder
    image = PILHelper.create_image(deck)

    nombre = "{}".format(teclas[tecla]['Nombre'])

    try:
        print("Cambiando folder")
        folder = "{}".format(teclas[tecla]['Folder'])
    except KeyError:
        print("No cambiar folder")

    try:
        NombreIcon = "{}/{}".format(folder,teclas[tecla]['ico'])
        deck.set_brightness(data['Brillo'])
    except KeyError:
        NombreIcon = "IconoDefecto.png"

    icon = Image.open(NombreIcon).convert("RGBA")
    icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
    icon_posicion = ((image.width - icon.width) // 2, 0)
    image.paste(icon, icon_posicion, icon)

    try:
        titulo = "{}".format(teclas[tecla]['Titulo'])
    except KeyError:
        print(" ")

    deck.set_key_image(tecla, PILHelper.to_native_format(deck, image))

def ActualizarTeclas(deck, tecla, estado):
    global teclas
    if estado:
        try:
            print("Boton {} {} = {}".format(tecla, teclas[tecla]['Nombre'], estado), flush=True)
            try:
                print("comando {}".format(teclas[tecla]['tecla']))

                for tecla in teclas[tecla]['tecla']:
                    keyboard.press(tecla)

                for tecla in teclas[tecla]['tecla']:
                    keyboard.release(tecla)
            except KeyError:
                print("no comando")
                try:
                    #print(teclas[tecla]['key'])
                    teclas = teclas[tecla]['key']
                    #print(teclas)
                    # for indice in range(len(teclas)):
                    #     print(indice)
                    #     ActualizarImagen(deck, teclas, indice)
                except KeyError:
                    print("no key")
        except IndexError:
            print("Boton {} No Asignada = {}".format(tecla, estado), flush=True)



# Principal
if __name__ == "__main__":

    # Buscando Dispisitovos
    streamdecks = DeviceManager().enumerate()

    print("Programa El Gato ALSW - {}".format("Encontrado" if len(streamdecks) > 0 else "No Conectado"));

    for index, deck in enumerate(streamdecks):

        # Abriendo puerto
        deck.open()
        deck.reset()

        print("Abriendo '{}' dispositivo (Numero Serial: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Cambiar Brillo
        try:
            deck.set_brightness(data['Brillo'])
        except KeyError:
            deck.set_brightness(50)

        try:
            fuente = "{}".format(data['Fuente'])
        except KeyError:
            print("Error faltar")

        # Activando Imagen Defecto
        #for key in range(len(data['Comando'])):
        #    CambiarImagen(deck, key, False)

        teclas = data['Comando']
        for tecla in range(len(teclas)):
            ActualizarImagen(deck, teclas, tecla)

        # Sistema de Coalbask
        # deck.set_key_callback(PrecionarTecla)
        deck.set_key_callback(ActualizarTeclas)

        for t in threading.enumerate():
            if t is threading.currentThread():
                continue

            if t.is_alive():
                t.join()
