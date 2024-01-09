# Librería: https://github.com/Elektordi/obs-websocket-py
# librería temporal: https://github.com/Elektordi/obs-websocket-py
import threading

from MiLibrerias import ConfigurarLogging, ObtenerArchivo, ObtenerValor, SalvarArchivo, SalvarValor
from obswebsocket import events, obsws, requests
from acciones import mensajeMQTT
from math import log

logger = ConfigurarLogging(__name__)


class MiOBS:
    """Concepción con OBS."""

    def __init__(self):
        """Crea confección básica con OBS Websocket."""
        logger.info("OBS[Iniciando]")
        self.archivoEstado = "data/obs.json"
        self.audioMonitoriar = list()
        self.dibujar = None
        self.notificaciones = None
        self.Reiniciar()

    def Reiniciar(self):
        """Reiniciar todo los estado"""
        logger.info("OBS[Reiniciando]")
        self.host = "localhost"
        self.port = 4455
        self.password = None
        self.conectado = False
        SalvarValor(self.archivoEstado, "obs_conectar", False)
        self.LimpiarTemporales()

    def CambiarHost(self, host: int) :
        """Cambia el host a conectarse."""
        self.host = host

    def IniciarAcciones(self, listaAcciones):
        """Acciones para controlar OBS"""
        listaAcciones["obs_conectar"] = self.Conectar
        listaAcciones["obs_desconectar"] = self.Desconectar
        listaAcciones["obs_grabar"] = self.CambiarGrabacion
        listaAcciones["obs_envivo"] = self.CambiarEnVivo
        listaAcciones["obs_camara_virtual"] = self.CambiarCamaraVirtual
        listaAcciones["obs_escena"] = self.CambiarEscena
        listaAcciones["obs_fuente"] = self.CambiarFuente
        listaAcciones["obs_filtro"] = self.CambiarFiltro
        listaAcciones["obs_estado"] = self.EstadoOBS
        listaAcciones["obs_tiempo_grabando"] = self.TiempoGrabando
        listaAcciones["obs_tiempo_envivo"] = self.TiempoEnVivo

        listaAcciones["obs_grabar_vertical"] = self.cambiarGrabacionVertical
        listaAcciones["obs_envivo_vertical"] = self.cambiarEnVivoVertical
        listaAcciones["obs_escena_vertical"] = self.cambiarEscenaVertical
        
        # listaAcciones['obs_host'] = self.OBS.Conectar
        # listaAcciones['obs_server'] = self.OBS.Conectar

    def DibujarDeck(self, funcion):
        """Guarda Funcion para refrescar iconos StringDeck."""
        self.dibujar = funcion

    def actualizarDeck(self):
        """Dibuja en StreanDeck si es posible"""
        if self.dibujar is not None:
            self.dibujar()

    def AgregarNotificacion(self, funcion):
        """Agrega función para notificación."""
        self.alertaOBS = ObtenerArchivo("modulos/alerta_obs/mqtt.json")
        self.notificaciones = funcion
    def Conectar(self, opciones):
        """Se conecta a OBS Websocket y inicializa los eventos."""
        if "servidor" in opciones:
            self.host = opciones["servidor"]
        if "puerto" in opciones:
            self.port = opciones["puerto"]
        if "contrasenna" in opciones:
            self.password = opciones["contrasenna"]

        if self.conectado:
            logger.info("OBS Ya Conectado")
            self.Notificar("OBS-Ya-Conectado")
            return
        
        modulos = ObtenerArchivo("modulos/modulos.json")
        monitorAudio = modulos.get("obs_monitor_audio", False)

        if monitorAudio:
            self.audioMonitoriar = ObtenerArchivo("modulos/audio_obs/audio.json")
            self.audioTopico = ObtenerArchivo("modulos/audio_obs/mqtt.json")["topic"]

        try:
            if self.password is None:
                self.OBS = obsws(self.host, self.port, authreconnect=1, on_connect=self.conectarOBS, on_disconnect=self.desconectarOBS)
            else:
                self.OBS = obsws(self.host, self.port, self.password, authreconnect=1, on_connect=self.conectarOBS, on_disconnect=self.desconectarOBS)
            self.OBS.connect(input_volume_meters=monitorAudio)
        except Exception as error:
            logger.warning(f"OBS[Error] {error}")
            self.LimpiarTemporales()
            self.conectado = False
            SalvarValor(self.archivoEstado, "obs_conectar", False)
            self.Notificar("OBS-No-Encontrado")
            return
        self.SalvarEstadoActual()
        # self.AgregarEvento()
        # self.OBS.call(requests.SetHeartbeat(True))
        self.AgregarEvento(self.EventoEscena, events.CurrentProgramSceneChanged)
        self.AgregarEvento(self.EventoGrabando, events.RecordStateChanged)
        self.AgregarEvento(self.EventoEnVivo, events.StreamStateChanged)
        self.AgregarEvento(self.EventoWebCamara, events.VirtualcamStateChanged)
        self.AgregarEvento(self.EventoVisibilidadFuente, events.SceneItemEnableStateChanged)
        self.AgregarEvento(self.EventoVisibilidadFiltro, events.SourceFilterEnableStateChanged)
        self.AgregarEvento(self.eventoVendendor, events.VendorEvent)
        self.AgregarEvento(self.EventoSalir, events.ExitStarted)
        self.AgregarEvento(self.eventoVolumen, events.InputVolumeMeters)

        # self.AgregarEvento(self.EventoPulsoCorazon, events.Heartbeat)
        self.actualizarDeck()

    def conectarOBS(self, mensaje):
        self.conectado = True
        logger.info(f"OBS[Conectado] {self.host}")
        self.Notificar("OBS-Conectado")

    def desconectarOBS(self, mensaje):
        self.conectado = False
        logger.info("OBS[Desconectado]")
        self.Notificar("OBS-No-Conectado")
        self.LimpiarTemporales()
        self.actualizarDeck()

    def SalvarEstadoActual(self):
        """Salta estado inicial de OBS para StreamDeck."""
        escenaActual = self.OBS.call(requests.GetSceneList()).datain["currentProgramSceneName"]
        estadoGrabando = self.OBS.call(requests.GetRecordStatus()).datain["outputActive"]
        estadoEnVivo = self.OBS.call(requests.GetStreamStatus()).datain["outputActive"]
        SalvarValor(self.archivoEstado, "obs_conectar", self.conectado)
        SalvarValor(self.archivoEstado, "obs_escena", escenaActual)
        SalvarValor(self.archivoEstado, "obs_grabar", estadoGrabando)
        SalvarValor(self.archivoEstado, "obs_envivo", estadoEnVivo)

        self.SalvarFuente()

    def SalvarFuente(self):
        HiloFuentes = threading.Thread(target=self.HiloFuenteArchivo)
        HiloFuentes.start()

    def HiloFuenteArchivo(self):
        refrescar = False
        escenaActual = self.OBS.call(requests.GetSceneList()).datain["currentProgramSceneName"]
        data = self.OBS.call(requests.GetSceneItemList(sceneName=escenaActual)).datain
        for fuente in data["sceneItems"]:
            nombreFuente = fuente["sourceName"]
            estadoFuente = fuente["sceneItemEnabled"]
            idFuente = fuente["sceneItemId"]
            estadoFuenteViejo = ObtenerValor("data/obs_fuente.json", nombreFuente, Depurar=False)

            if estadoFuente != estadoFuenteViejo:
                SalvarValor("data/obs_fuente.json", nombreFuente, estadoFuente)
                refrescar = True

            SalvarValor("data/obs_fuente_id.json", [escenaActual, idFuente], nombreFuente)
            self.SalvarFiltroFuente(nombreFuente)

        if refrescar:
            self.actualizarDeck()

    def AgregarEvento(self, Funcion, Evento):
        """Registra evento de OBS a una funcion."""
        self.OBS.register(Funcion, Evento)

    def EventoEscena(self, mensaje):
        """Recibe nueva escena actual."""
        escenaActual = mensaje.datain["sceneName"]
        SalvarValor(self.archivoEstado, "obs_escena", escenaActual)
        logger.info(f"OBS[Escena] {escenaActual}")
        self.SalvarFuente()
        self.actualizarDeck()

    def EventoGrabando(self, mensaje):
        """Recibe estado de grabación."""
        estado =  mensaje.datain["outputActive"]
        SalvarValor(self.archivoEstado, "obs_grabar", estado)
        logger.info(f"OBS[Grabado] {estado}")
        if estado:
            self.Notificar("OBS-Grabando")
        else:
            self.Notificar("OBS-No-Grabando")
        self.actualizarDeck()

    def EventoEnVivo(self, mensaje):
        """Recibe estado del Striming."""
        estado = mensaje.datain["outputActive"]
        SalvarValor(self.archivoEstado, "obs_envivo", estado)
        logger.info(f"OBS[EnVivo] - {estado}")
        if estado:
            self.Notificar("OBS-EnVivo")
        else:
            self.Notificar("OBS-No-EnVivo")
        self.actualizarDeck()

    def EventoWebCamara(self, mensaje):
        """Recibe estado del WebCamara"""
        estado = mensaje.datain["outputActive"]
        SalvarValor(self.archivoEstado, "obs_webcamara", estado)
        logger.info(f"OBS[WebCamara] - {estado}")
        if estado:
            self.Notificar("OBS-WebCamara")
        else:
            self.Notificar("OBS-No-WebCamara")
        self.actualizarDeck()

    def EventoSalir(self, mensaje):
        """Recibe desconeccion de OBS websocket."""
        logger.info("OBS[Desconectado]")
        self.Notificar("OBS-No-Conectado")
        try:
            self.Desconectar()
        except Exception as error:
            logger.warning(f"OBS[Error] {error}")
            self.conectado = False
        self.LimpiarTemporales()
        self.actualizarDeck()

    def EventoPulsoCorazon(self, mensaje):
        if mensaje.name == "Heartbeat":
            logger.info("Pulso de OBS")

    def EventoVisibilidadFuente(self, mensaje):
        """Recive estado de fuente."""
        escenaActual = mensaje.datain["sceneName"]
        idFuente = mensaje.datain["sceneItemId"]
        visibilidad = mensaje.datain["sceneItemEnabled"]
        nombreFuente = ObtenerValor("data/obs_fuente_id.json", [escenaActual, str(idFuente)])
        SalvarValor("data/obs_fuente.json", nombreFuente, visibilidad)
        self.actualizarDeck()

    def EventoVisibilidadFiltro(self, mensaje):
        """Recive estado del filtro."""
        nombreFiltro = mensaje.datain["filterName"]
        nombreFuente = mensaje.datain["sourceName"]
        visibilidad = mensaje.datain["filterEnabled"]
        logger.info(f"OBS[{nombreFiltro}] {visibilidad}")
        SalvarValor("data/obs_filtro.json", [nombreFuente, nombreFiltro], visibilidad)
        self.actualizarDeck()

    def SalvarFiltroFuente(self, fuente):
        """Salva el estado de los filtros de una fuente."""
        filtros = self.OBS.call(requests.GetSourceFilterList(sourceName=fuente)).datain["filters"]
        if filtros is None:
            return

        for filtro in filtros:
            nombreFiltro = filtro["filterName"]
            estadoFiltro = filtro["filterEnabled"]
            SalvarValor("data/obs_filtro.json", [fuente, nombreFiltro], estadoFiltro)

    def SalvarFiltroConfiguraciones(self, Filtro, lista):
        for elemento in lista:
            Data = Filtro.copy()
            Data.append(elemento)
            SalvarValor("data/obs_filtro_opciones.json", Data, lista[elemento])

    def eventoVendendor(self, mensaje):
        """Recive mensajes de plugins extras"""
        vendedor = mensaje.datain["vendorName"]
        if vendedor == "aitum-vertical-canvas":
            self.eventoVertical(mensaje)

    def eventoVertical(self, mensaje):
        """Recive mensajes para el plugin de Vertical"""
        tipo = mensaje.datain["eventType"]
        if tipo == "switch_scene":
            escenaActual = mensaje.datain["eventData"]["new_scene"]
            SalvarValor(self.archivoEstado, "obs_escena_vertical", escenaActual)
            logger.info(f"OBS[Escena-Vertical] {escenaActual}")

    def eventoVolumen(self, mensaje):
        """Recive mensaje de entradas de Audio"""
        def convertir(nivel):
            return round(20 * log(nivel, 10), 1) if nivel > 0 else -200.0
            
        canales = mensaje.datain["inputs"]
        for canal in canales:
            for nombres in self.audioMonitoriar:
                if nombres == canal["inputName"]:
                    if len(canal["inputLevelsMul"]) > 0:
                        nivel = canal["inputLevelsMul"][0][1]
                        opciones = {
                         "mensaje" : convertir(nivel),
                         "topic" : f"{self.audioTopico}/{nombres}"
                        }
                        mensajeMQTT(opciones)

    def CambiarEscena(self, opciones):
        """Envía solicitud de cambiar de Escena."""
        escena = opciones.get("escena")

        if escena is None:
            logger.info("OBS[Escena no definida]")
            return
       
        if self.conectado:
            self.OBS.call(requests.SetCurrentProgramScene(sceneName=escena))## problema 
            logger.info(f"OBS[Cambiando] {escena}")
        else:
            logger.warning("OBS[No conectado]")
            self.Notificar("OBS-No-Encontrado")

    def CambiarFuente(self, opciones=False, fuente=None):
        """Envia solisitud de Cambia el estado de una fuente."""

        esenaActual = ObtenerValor(self.archivoEstado, "obs_escena")
        if fuente is None:
            if "fuente" in opciones:
                fuente = opciones["fuente"]

        if self.conectado:
            estadoFuente = ObtenerValor("data/obs_fuente.json", fuente)
            idFuente =  self.OBS.call(requests.GetSceneItemId(sceneName=esenaActual, sourceName=fuente)).datain["sceneItemId"]
            if estadoFuente is not None:
                estadoFuente = not estadoFuente
                logger.info(f"OBS[Fuente] {esenaActual}-{fuente}={estadoFuente}")
                self.OBS.call(requests.SetSceneItemEnabled(sceneName=esenaActual, sceneItemId=idFuente, sceneItemEnabled=estadoFuente))
            else:
                logger.warning(f"No se encontro {fuente[0]} o {fuente[1]} en OBS")

        else:
            logger.info("OBS[no Conectado]")
            self.Notificar("OBS No Conectado")

    def CambiarFiltro(self, opciones):
        """Envia solisitud de cambiar estado de filtro."""
        filtro = opciones.get("filtro")
        fuente = opciones.get("fuente")
        estado = opciones.get("estado")

        if fuente is None or filtro is None:
            logger.info("OBS[Falta Atributo]")
            return

        if self.conectado:
            if estado is None:
                estado = ObtenerValor("data/obs_filtro.json", [fuente, filtro])
                if estado is not None:
                    estado = not estado

            if estado is not None:
                logger.info(f"OBS[Filtro] {fuente}[{filtro}]={estado}")
                self.OBS.call(requests.SetSourceFilterEnabled(sourceName=fuente, filterName=filtro, filterEnabled=estado))
        else:
            logger.info("OBS[no Conectado]")
            self.Notificar("OBS No Conectado")

    def CambiarGrabacion(self, opciones=None):
        """Envia solisitud de cambiar estado de Grabacion."""
        if self.conectado:
            logger.info("Cambiando[Grabacion]")
            self.OBS.call(requests.ToggleRecord())
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS No Conectado")

    def CambiarEnVivo(self, opciones=None):
        """Envia solisitud de cambiar estado del Streaming ."""
        if self.conectado:
            logger.info("Cambiando[EnVivo]")
            self.OBS.call(requests.ToggleStream())
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS No Conectado")

    def CambiarCamaraVirtual(self, opciones=None):
        """Envia solisitud de cambio estado Camara Virtual"""
        if self.conectado:
            self.OBS.call(requests.ToggleVirtualCam())
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS-No-Conectado")

    def cambiarGrabacionVertical(self, opciones=None):
        """Envia solisitud de cambiar estado de Grabacion en plugin Vertical."""
        if self.conectado:
            logger.info("Cambiando[Grabacion-Vertical]")
            self.OBS.call(requests.CallVendorRequest(vendorName="aitum-vertical-canvas",requestType="toggle_recording"))
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS No Conectado")

    def cambiarEnVivoVertical(self, opciones=None):
        """Envia solisitud de cambiar estado del Streaming ."""
        if self.conectado:
            logger.info("Cambiando[EnVivo-Vertical]")
            self.OBS.call(requests.CallVendorRequest(vendorName="aitum-vertical-canvas",requestType="toggle_streaming"))
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS No Conectado")



    def cambiarEscenaVertical(self, opciones=None):
        """Enviá solicitud de cambiar de Escena en plugin Vertical."""
        escena = opciones.get("escena")

        if escena is None:
            logger.info("OBS[Escena no definida]")
            return
       
        if self.conectado:
            mensaje = {"scene":escena}
            self.OBS.call(requests.CallVendorRequest(vendorName="aitum-vertical-canvas",requestType="switch_scene", requestData=mensaje))
            logger.info(f"OBS[Cambiando-Vertical] {escena}")
        else:
            logger.warning("OBS[No conectado]")
            self.Notificar("OBS-No-Encontrado")

    def TiempoGrabando(self, opciones=None):
        if self.conectado:
            consulta = self.OBS.call(requests.GetStreamingStatus())
            if consulta.getRecording():
                tiempo = consulta.getRecTimecode().split(".")[0]
                logger.info(f"Tiempo Grabando: {tiempo}")
                return tiempo
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS-No-Conectado")
        return "No-Grabando"

    def TiempoEnVivo(self, opciones=None):
        if self.conectado:
            consulta = self.OBS.call(requests.GetStreamingStatus())
            if consulta.getStreaming():
                tiempo = consulta.getStreamTimecode().split(".")[0]
                logger.info(f"Tiempo Envivo: {tiempo}")
                return tiempo
        else:
            logger.info("OBS no Conectado")
            self.Notificar("OBS-No-EnVivo")
        return "No-EnVivo"

    def LimpiarTemporales(self):
        """Limpia los archivos con información temporal de OBS."""
        SalvarArchivo(self.archivoEstado, dict())
        SalvarArchivo("data/obs_fuente.json", dict())
        SalvarArchivo("data/obs_filtro.json", dict())
        SalvarArchivo("data/obs_filtro_opciones.json", dict())
        SalvarArchivo("data/obs_fuente_id.json", dict())

    def Desconectar(self, opciones=False):
        """Deconectar de OBS websocket."""
        logger.info(f"OBS[Desconectar] - {self.host}")
        if self.conectado:
            self.OBS.disconnect()
            self.LimpiarTemporales()
        self.conectado = False
        SalvarValor(self.archivoEstado, "obs_conectar", False)
        self.actualizarDeck()
        logger.info("Desconeccion correcta")

    def __del__(self):
        """Borrar objeto de Websocket ."""
        self.Desconectar()

    def EventoPrueva(self, Mensaje):
        print(Mensaje)

    def Notificar(self, Mensaje):
        if self.notificaciones is not None:
            self.notificaciones(Mensaje, self.alertaOBS)

    def EstadoOBS(self, opciones):
        conectado = ObtenerValor(self.archivoEstado, "obs_conectar")
        if conectado is None or not conectado:
            self.Notificar("OBS-No-Conectado")
        else:
            self.Notificar("OBS-Conectado")

        grabando = ObtenerValor(self.archivoEstado, "obs_grabar")
        if grabando is None or not grabando:
            self.Notificar("OBS-No-Grabando")
        else:
            self.Notificar("OBS-Grabando")

        enVivo = ObtenerValor(self.archivoEstado, "obs_envivo")
        if enVivo is None or not enVivo:
            self.Notificar("OBS-No-EnVivo")
        else:
            self.Notificar("OBS-EnVivo")

        webCamara = ObtenerValor(self.archivoEstado, "obs_webcamara")
        if webCamara is None or not webCamara:
            self.Notificar("OBS-No-WebCamara")
        else:
            self.Notificar("OBS-WebCamara")

    def Consultas(self):
        # print(dir(requests))
        print()
        print(dir(events))
        print()
        # Solisitud = requests.Baserequests()
        # Solisitud.name = "StartStopVirtualCam"
        # self.OBS.call(Solisitud)
