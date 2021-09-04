# https://pyautogui.readthedocs.io/en/latest/install.html

import pyautogui
import pyperclip

from .delay import Delay
# Implementar press y onrelles
# TODO: Añadir ñ en las funciones
# TODO: Agregar funcionMover Raton a posicion


def ComandoTeclas(Opciones):
    """
        Preciona una combinacion de tecla.

        teclas -> list
            combinaciones de teclas
    """
    if 'teclas' in Opciones:
        Teclas = Opciones['teclas']

        for tecla in Teclas:
            pyautogui.keyDown(tecla)
        for tecla in reversed(Teclas):
            pyautogui.keyUp(tecla)


def ComandoPegar(Opciones):
    """
        Guarda texto en papelera.

        texto -> stl
            texto a guardas
        intervalo -> float
            tiempo de espera
    """
    if 'texto' in Opciones:
        Texto = Opciones['texto']

        intervalo = 0.15
        if 'intervalo' in Opciones:
            intervalo = Opciones['intervalo']

        pyperclip.copy(Texto)
        pyautogui.hotkey('ctrl', 'v', interval=intervalo)


def ComandoEscribir(Opciones):
    """
        Escribe un texto letra por letra.
        
        texto -> stl
            texto a guardas
        intervalo -> float
            tiempo de espera
    """
    if 'texto' in Opciones:
        Texto = Opciones['texto']

        intervalo = 0.01
        if 'intervalo' in Opciones:
            intervalo = Opciones['intervalo']

        pyautogui.write(Texto, interval=intervalo)


def ComandoPrecionar(Opciones):
    """
        Preciona una combinacion de teclas con estado.

        tecla -> list
            combinaciones de teclas
        precionado -> bool
            estado de la tecla
        
    """
    if 'teclas' in Opciones:
        Teclas = Opciones['teclas']
    if 'precionado' in Opciones:
        Estado = Opciones['presionado']

    if Estado:
        for tecla in Teclas:
            pyautogui.keyDown(tecla)
    else:
        for tecla in reversed(Teclas):
            pyautogui.keyUp(tecla)


def CopiarTexto():
    """
        Copia texto de papelera.
    """
    pyautogui.hotkey('ctrl', 'c')
    Delay({"tiempo": 0.1})
    return pyperclip.paste()