import json
from MiLibrerias import EnviarMensajeMQTT
def MensajeMQTT(Opciones):
    """
        Envia un mensaje por mqtt

        mensaje -> stl
            mensaje a enviar
        topic -> stl
            tema a publicar el mensaje
    """
    Mensaje = None
    Topic = None
    if 'mensaje' in Opciones:
        Mensaje = Opciones['mensaje']
    elif 'opciones' in Opciones:
        Mensaje = Opciones['opciones']
        Mensaje = json.dumps(Mensaje)
    
    if 'topic' in Opciones:
        Topic = Opciones['topic']
    
    if Mensaje is not None and Topic is not None:
        EnviarMensajeMQTT(Topic, Mensaje)
