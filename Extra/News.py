import json
import os
import sys
import yaml

from Extra.Depuracion import Imprimir

ArchivoNoticias = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")) + '/Data/News.json'
ArchivoID = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")) + '/Data/IdNews.json'
ArchivoTituloNoticias = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")) + '/Data/News/TituloNoticia.txt'


def SalvarArchivoNoticia(Directorio):
    global Archivo
    data = {}
    data['Noticia'] = str(Directorio)
    Imprimir(f"El Archivo de Noticas es {data['Noticia']}")
    with open(ArchivoNoticias, 'w') as file:
        json.dump(data, file, indent=4)


def SalvarIdNoticia(ID):
    global Archivo
    data = {}
    data['ID'] = str(ID)
    with open(ArchivoID, 'w') as file:
        json.dump(data, file, indent=4)


def SalvarTexto(Archivo, Texto):
    with open(ArchivoTituloNoticias, 'w') as file:
        file.write(Texto)


def CargarArchivoNoticia():
    global ArchivoNoticias
    if os.path.exists(ArchivoNoticias):
        with open(ArchivoNoticias) as f:
            data = json.load(f)
            if 'Noticia' in data:
                return data['Noticia']
    else:
        Imprimir(f"No se Encontro el Archivo {ArchivoNoticias}")
        sys.exit()


def CargarIDNoticia():
    global ArchivoID
    if os.path.exists(ArchivoID):
        with open(ArchivoID) as f:
            data = json.load(f)
            if 'ID' in data:
                return int(data['ID'])
    else:
        Imprimir(f"No se Encontro el Archivo {ArchivoID}")
        sys.exit()


def CargarNoticias():
    Archivo = CargarArchivoNoticia()
    with open(Archivo) as f:
        try:
            data = list(yaml.load_all(f, Loader=yaml.SafeLoader))[
                0]['custom_sections']
            for i in range(len(data)):
                if 'title' in data[i]:
                    if data[i]['title'] == "Noticias":
                        return data[i]['items']
        except yaml.YAMLError as exc:
            print("error con yaml")
            return exc


def CambiarNoticia(Cambiar=True):
    Noticias = CargarNoticias()
    ID = CargarIDNoticia()
    if Cambiar:
        ID += 1
    else:
        ID -= 1

    if ID < 0:
        ID = 0
    elif ID >= len(Noticias):
        ID = len(Noticias) - 1
    SalvarNoticia(ID, Noticias[ID])


def AsignarNoticia(ID):
    Noticias = CargarNoticias()
    SalvarIdNoticia(ID)
    SalvarNoticia(ID, Noticias[ID])


def SalvarNoticia(ID, Noticia):
    global ArchivoTituloNoticias
    SalvarIdNoticia(ID)
    Imprimir(f"{ID} - {Noticia}")
    SalvarTexto(ArchivoTituloNoticias, Noticia['title'])
