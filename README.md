# Joystick MIDI Reader

Un script simple y eficiente en Python para leer eventos de joystick USB HID en Linux sin depender de librerías externas pesadas. Diseñado para ser rápido, ligero y fácil de hackear.

## Descripción

Esta herramienta permite leer e interpretar las pulsaciones de botones y movimientos de ejes de cualquier dispositivo Joystick/Gamepad USB conectado a un sistema Linux. Utiliza métodos nativos del sistema (`struct`, `fcntl`, `select`) para interactuar directamente con los dispositivos de entrada (`/dev/input/event*`), eliminando la necesidad de instalar módulos adicionales como `evdev`.

## Características

*   **Cero Dependencias**: Funciona con la librería estándar de Python 3. No requiere `pip install`.
*   **Baja Latencia**: Lectura de eventos sin búfer (`buffering=0`) para una respuesta inmediata.
*   **Auto-detección**: Busca automáticamente dispositivos HID compatibles.
*   **Salida Limpia**: Formato de log claro y consolidado para eventos de botones y ejes.
*   **Personalizable**: Diccionario de nombres de botones editable para mapear códigos de eventos a nombres humanos (e.g., "TRIGGER", "JUMP").

## Uso

1.  Conecta tu Joystick USB.
2.  Ejecuta el script:

```bash
python3 joystickmidi.py
```

3.  El script intentará detectar tu dispositivo automáticamente. Si encuentra el dispositivo, comenzará a mostrar los eventos en pantalla.

### Ejemplo de Salida

```text
Lector de joystick USB HID (Método Nativo)
==================================================
Dispositivo encontrado: /dev/input/event19
Leyendo eventos de: /dev/input/event19
Leyendo eventos del joystick. Presiona Ctrl+C para salir.

Botón BUTTON 1 - 288 PRESIONADO
Botón BUTTON 1 - 288 LIBERADO
Eje X Valor: 128
Eje Y Valor: 255
```

### Ejecución sin permisos
Si tienes problemas de permisos para leer `/dev/input/event*`, puedes ejecutarlo con sudo:

```bash
sudo python3 joystickmidi.py
```

## Contribuir

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar la detección de dispositivos, soportar más protocolos o añadir salida MIDI real, siéntete libre de hacer un fork y enviar un Pull Request.

## Créditos

Desarrollado por **Octavio Rossell**
*   Email: <octavio.rossell@gmail.com>
*   GitHub: [https://github.com/octaviotron/joystick-midi](https://github.com/octaviotron/joystick-midi)
