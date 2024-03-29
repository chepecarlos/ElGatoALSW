# Atributos Basicos de cada Accion

| nombre          | tipo          | descripcion                     | obligatorio | ejemplo     |
| --------------- | ------------- | ------------------------------- | ----------- | ----------- |
| nombre          | string        | nombre para la depuracion       | true        | MQTT        |
| titulo          | string        | Titulo para StreamDeck          | false       | MQTT        |
| titulo_opciones | list          | Atributos extrar para titulo    | false       |             |
| cargar_titulo   | list          | Carga un texto desde un archivo | fase        |
| ket             | int or string | id Boton o nombre Tecla         | true        | 15 o KEY_Z  |
| imagen          | string        | direccion de la imagen o gif    | false       | ./pollo.png |
| imagen_opciones | list          | Atributos extrar para imagen    | false       |             |
| accion          | string        | accion a realizar               | true        | reproducion |
| opciones        | list          | atributos extra para accion     | false       |             |
| macro_opciones  | list          | atributos extra macros          | false       |             |

# Opciones extras para Titulos

Configuraciones extrar para el texto que aparece e la imagen o gif para el **StreamDeck**

**Ningunos** de los atributos extas son obligatorios

| nombre       | tipo    | descripcion                             | defecto | ejemplo |
| ------------ | ------- | --------------------------------------- | ------- | ------- |
| tamanno      | int     | Tamaño maximo del texto                 | 40      | 20      |
| ajustar      | boolean | Disminulle el tamaño que se lea cmpleto | true    | false   |
| alinear      | string  | Posicion texto (centro, ariba, abajo)   | abajo   | ariba   |
| color        | string  | Color en nombre ingles o hexa           | white   | #008080 |
| borde_color  | string  | Color de borde de texto                 | black   | #ff0000 |
| borde_grosor | int     | Tamaño del borde                        | 5       | 20      |

# Opciones Extrar para Imagenes 

| nombre | tipo  | descripcion                   | defecto | ejemplo |
| ------ | ----- | ----------------------------- | ------- | ------- |
| fondo  | color | Color en nombre ingles o hexa | black   | #ff00f0 |

# Opciones Extrar para Macros

Atributos para opciones macros

**Ningunos** de los atributos extas son obligatorios

| nombre    | tipo           | descripcion                             | ejemplo |
| --------- | -------------- | --------------------------------------- | ------- |
| solisita  | string o list  | atributo                                | tiempo  |
| respuesta | string or list | atributo para siqueinte accion en macro | tiempo  |
