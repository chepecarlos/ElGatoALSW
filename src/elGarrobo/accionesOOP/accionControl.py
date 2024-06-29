import json
import time

from elGarrobo.miLibrerias import ConfigurarLogging, EnviarMensajeMQTT, ObtenerArchivo

from .accionBase import accionBase

Logger = ConfigurarLogging(__name__)


class accionControl(accionBase):
    def __init__(self) -> None:
        nombre = "Control MQTT"
        comando = "control"
        descripcion = "Controla la PC a distancia"
        super().__init__(nombre, comando, descripcion)

        propiedadHost = {
            "nombre": "host",
            "tipo": str,
            "obligatorio": True,
            "atributo": "host",
            "descripcion": "Compradora a controlar por MQTT",
            "ejemplo": "umaru",
        }

        propiedadAccion = {
            "nombre": "accion",
            "tipo": str,
            "obligatorio": True,
            "atributo": "accion",
            "descripcion": "accion a realizar en la pc",
            "ejemplo": "delay",
        }

        propiedadOpciones = {
            "nombre": "opciones",
            "tipo": dict,
            "obligatorio": False,
            "atributo": "opciones",
            "descripcion": "opciones para accion a realizar en la pc",
            "ejemplo": "time: 1",
        }

        self.agregarPropiedad(propiedadHost)
        self.agregarPropiedad(propiedadAccion)
        self.agregarPropiedad(propiedadOpciones)

        # TODO: usar configuraciones globales
        data = ObtenerArchivo("modulos/control/mqtt.md")

        if data is None:
            Logger.warning("No se encontro informacion mqtt modulos/control/mqtt.md")
            return

        self.topicControl = data.get("topic", "control")

        self.funcion = self.controlDistancia

    def controlDistancia(self):
        """espera un tiempo"""
        host = self.obtenerValor("host")
        accionHost = self.obtenerValor("accion")
        opcionesHost = self.obtenerValor("opciones")
        if host is not None and accionHost is not None:
            mensaje = {"host": host, "accion": accionHost}
            if opcionesHost:
                mensaje = {"host": host, "accion": accionHost, "opciones": opcionesHost}
                Logger.info(f"Control[{mensaje['host']}] - {mensaje['accion']}")
                Logger.info(f"Opciones: {opcionesHost}")
            else:
                mensaje = {"host": host, "accion": accionHost}
                Logger.info(f"Control[{mensaje['host']}] - {mensaje['accion']}")
            EnviarMensajeMQTT(self.topicControl, json.dumps(mensaje))
