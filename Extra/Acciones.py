import sys

import Extra.MiOBS as MiOBSs

from Extra.Depuracion import Imprimir
from Extra.Delay import Delay
from Extra.MiOS import MiOS
from Extra.EmularTeclado import ComandoTeclas, ComandoEscribir
from Extra.FuncionesProyecto import AbirProyecto
from Extra.News import CambiarNoticia, AsignarNoticia, LinkNoticia
from Extra.Sonidos import Reproducir, PararReproducion


def AgregarStreanDeck(_Deck):
    global Deck
    Deck = _Deck


def AgregarOBS(_MiOBS):
    global MiOBS
    MiOBS = _MiOBS


def Accion(AccionActual):
    global Deck

    # No Saltar extra
    if 'Siquiente' in AccionActual:
        Deck.BotonesSiquiente(True)
        Deck.ActualizarTodasImagenes(True)
    elif 'Anterior' in AccionActual:
        Deck.BotonesSiquiente(False)
        Deck.ActualizarTodasImagenes(True)
    elif 'Regresar' in AccionActual:
        Deck.BotonActuales = Deck.Data['StreamDeck']
        # ComandosRaton = data['teclado']
        Deck.DesfaceBoton = 0
        Deck.Carpeta = "Base"
        Deck.ActualizarTodasImagenes(True)
        Deck.ConfigurandoTeclados("")
    elif 'StreamDeck' in AccionActual:
        Imprimir("Entenado en folder")
        Deck.BotonActuales = AccionActual['StreamDeck']
        Deck.DesfaceBoton = 0
        Deck.Carpeta = AccionActual['Nombre']
        Deck.ConfigurandoTeclados(AccionActual['Nombre'])
        # if 'teclado' in accion:
        #     Imprimir("Cargando Teclado")
        #     ComandosRaton = accion['teclado']
        Deck.ActualizarTodasImagenes(True)
    elif 'Macro' in AccionActual:
        for AccionMacro in AccionActual['Macro']:
            Accion(AccionMacro)
    elif 'OS' in AccionActual:
        MiOS(AccionActual['OS'])
    elif 'tecla' in AccionActual:
        ComandoTeclas(AccionActual['tecla'])
    elif 'texto' in AccionActual:
        ComandoEscribir(AccionActual['texto'])
    elif 'delay' in AccionActual:
        Delay(AccionActual['delay'])
    elif 'Proyecto' in AccionActual:
        AbirProyecto(AccionActual['Proyecto'])
    elif 'OBS' in AccionActual:
        AccionesOBS(AccionActual)
    elif "ConfigDeck" in AccionActual:
        AccionesStreanDeck(AccionActual)
    elif 'MQTT' in AccionActual:
        Imprimir("Cosas de MQTT")
    elif 'News' in AccionActual:
        AccionesNews(AccionActual)
    elif 'Sonido' in AccionActual:
        AccionSonido(AccionActual)
        # MiMQTT.CambiarHost(accion['MQTT'])
        # MiMQTT.Conectar()
    # elif 'mqtt' in accion:
    #     Imprimir(f"Comando MQTT {accion['mqtt']}")
    #     MiMQTT.Enviando(accion['mqtt'])
    elif 'Opcion' in AccionActual:
        if AccionActual['Opcion'] == "Exit":
            # TODO: ver si esta habierto antes de cerrar
            Imprimir("Saliendo ElGatoALSW - Adios :) ")
            CerrarOBS()
            sys.exit()
            # MiMQTT.Cerrar()
            # MiDeck.reset()
            # MiDeck.close()
        else:
            Imprimir(f"Opcion No Encontrada: {AccionActual['Opcion']}")
    else:
        Imprimir("Boton - no definida")


def AccionSonido(AccionActual):
    if AccionActual['Sonido'] == 'Parar':
        PararReproducion()
    else:
        Reproducir(AccionActual['Sonido'])


def AccionesStreanDeck(AccionActual):
    global Deck
    if AccionActual['ConfigDeck'] == "SubirBrillo":
        Deck.CambiarBrillo(5)
    elif AccionActual['ConfigDeck'] == "BajarBrillo":
        Deck.CambiarBrillo(-5)


def AccionesOBS(AccionActual):
    '''Acciones que puede enviarse a OBS_WebSoket'''
    global MiOBS
    global Deck
    if AccionActual['OBS'] == "Server" and 'Server' in AccionActual:
        AgregarOBS(MiOBSs.MiObsWS(Deck.Carpeta))
        MiOBS.CambiarHost(AccionActual['Server'])
        MiOBS.Conectar()
        MiOBS.RegistarEvento(EventoOBS)
        Deck.OBSConectado = True
    elif Deck.OBSConectado:
        if AccionActual['OBS'] == "Cerrar":
            CerrarOBS()
        elif AccionActual['OBS'] == "Grabar":
            MiOBS.CambiarGrabacion()
        elif AccionActual['OBS'] == "Live":
            MiOBS.CambiarStriming()
        elif AccionActual['OBS'] == "Esena":
            MiOBS.CambiarEsena(AccionActual['Esena'])
        elif AccionActual['OBS'] == "Fuente":
            MiOBS.CambiarFuente(AccionActual['Fuente'], not AccionActual['Estado'])
        elif AccionActual['OBS'] == "Filtro":
            MiOBS.CambiarFiltro(AccionActual['Fuente'], AccionActual['Filtro'], not AccionActual['Estado'])
        else:
            Imprimir("No encontramos esta Opcion de OBS")
    else:
        Imprimir("OBS no Conectado")


def CerrarOBS():
    global MiOBS
    global Deck
    if Deck.OBSConectado:
        Deck.OBSConectado = False
        MiOBS.DesregistarEvento(EventoOBS)
        MiOBS.Cerrar()


def EventoOBS(Mensaje):
    '''Escucha y Reaciona a eventos de OBS'''
    Imprimir(Mensaje.name)
    global MiOBS
    global Deck
    IdOBS = Deck.BuscarCarpeta(MiOBS.Carpeta)
    if Mensaje.name == "Exiting":
        try:
            print("Cerrando OBS - Evento")
            CerrarOBS()
        except Exception as e:
            print(f"No se pudo conectar a OBS - {e}")
            MiOBS.OBSConectado = False
    elif Mensaje.name == 'RecordingStopped':
        Imprimir(f'Parado la grabacion - {MiOBS.Carpeta}')
        IdGrabar = Deck.BuscarBoton(IdOBS, 'Rec')
        if IdGrabar != -1:
            Deck.CambiarEstadoBoton(IdOBS, IdGrabar, False)
            Deck.ActualizarTodasImagenes()
    elif Mensaje.name == 'RecordingStarted':
        Imprimir(f'Iniciado la grabacion - {MiOBS.Carpeta}')
        IdGrabar = Deck.BuscarBoton(IdOBS, 'Rec')
        if IdGrabar != -1:
            Deck.CambiarEstadoBoton(IdOBS, IdGrabar, True)
            Deck.ActualizarTodasImagenes()
    elif(Mensaje.name == 'StreamStopped'):
        Imprimir("Parando la trasmicion")
        IdLive = Deck.BuscarBoton(IdOBS, 'Live')
        if IdLive != -1:
            Deck.CambiarEstadoBoton(IdOBS, IdLive, False)
            Deck.ActualizarTodasImagenes()
    elif(Mensaje.name == 'StreamStarted'):
        Imprimir("Empezando la trasmicion")
        IdLive = Deck.BuscarBoton(IdOBS, 'Live')
        if IdLive != -1:
            Deck.CambiarEstadoBoton(IdOBS, IdLive, True)
            Deck.ActualizarTodasImagenes()
    elif(Mensaje.name == 'SwitchScenes'):
        Imprimir(f"Cambia a Esena - {Mensaje.datain['scene-name']}")
        IdEsena = Deck.BuscarBoton(IdOBS, Mensaje.datain['scene-name'])
        for Boton in range(len(Deck.Data['StreamDeck'][IdOBS]['StreamDeck'])):
            if Deck.EsEsena(IdOBS, Boton):
                if IdEsena == Boton:
                    Deck.CambiarEstadoBoton(IdOBS, Boton, True)
                else:
                    Deck.CambiarEstadoBoton(IdOBS, Boton, False)
        Deck.ActualizarTodasImagenes()
    elif(Mensaje.name == 'SceneItemVisibilityChanged'):
        NombreIten = Mensaje.datain['item-name']
        EstadoItem = Mensaje.datain['item-visible']
        IdItem = Deck.BuscarBoton(IdOBS, NombreIten)
        Imprimir(f"Se cambio fuente {NombreIten} - {EstadoItem}")
        Deck.CambiarEstadoBoton(IdOBS, IdItem, EstadoItem)
        Deck.ActualizarTodasImagenes()
    elif(Mensaje.name == 'SourceFilterVisibilityChanged'):
        NombreFiltro = Mensaje.datain['filterName']
        NombreFuente = Mensaje.datain['sourceName']
        EstadoFiltro = Mensaje.datain['filterEnabled']
        Imprimir(f"Se cambio el filtro {NombreFiltro} de {NombreFuente} a {EstadoFiltro}")
        IdItem = Deck.BuscarBoton(IdOBS, NombreFiltro)
        Deck.CambiarEstadoBoton(IdOBS, IdItem, EstadoFiltro)
        Deck.ActualizarTodasImagenes()
    else:
        Imprimir(f"Evento no procesado de OBS: {Mensaje.name}")


def AccionesNews(AccionActual):
    if AccionActual['News'] == "Siquiente":
        Imprimir("Siquiente Noticia")
        CambiarNoticia()
    elif AccionActual['News'] == "Anterior":
        Imprimir("Anterior Noticia")
        CambiarNoticia(False)
    elif AccionActual['News'] == "Reiniciar":
        Imprimir("Reiniciar Noticia")
        AsignarNoticia(0)
    elif AccionActual['News'] == "Link":
        Imprimir("Pegar Link de Noticia")
        Link = LinkNoticia()
        ComandoEscribir(Link)
    else:
        Imprimir("No accion de News")
