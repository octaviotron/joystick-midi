#!/usr/bin/env python3
"""
Script para leer pulsaciones de un dispositivo USB HID (joystick) en Linux.
Usa solo módulos estándar de Python.
"""

import os
import struct
import select
from fcntl import ioctl

# Constantes para ioctl
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRMASK = (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK = (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IOC(dir_, type_, nr, size):
    return (dir_ << _IOC_DIRSHIFT) | (type_ << _IOC_TYPESHIFT) | (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT)

def _IOR(type_, nr, size):
    return _IOC(_IOC_READ, type_, nr, size)

def _IOW(type_, nr, size):
    return _IOC(_IOC_WRITE, type_, nr, size)

def _IOWR(type_, nr, size):
    return _IOC(_IOC_READ | _IOC_WRITE, type_, nr, size)

# Constantes específicas de HID/evdev
HID_MAX_DESCRIPTOR_SIZE = 4096
HIDIOCGRDESCSIZE = _IOR(ord('H'), 0x01, 4)  # get descriptor size
HIDIOCGRDESC = _IOR(ord('H'), 0x02, 4 + HID_MAX_DESCRIPTOR_SIZE)  # get descriptor

EV_KEY = 0x01
EV_ABS = 0x03
ABS_X = 0x00
ABS_Y = 0x01
BTN_JOYSTICK = 0x120
BTN_TRIGGER = 0x120

# Diccionario de nombres personalizados para botones
BUTTON_NAMES = {
    288: "BUTTON 1",  # Trigger
    289: "BUTTON 2",  # Thumb
    290: "BUTTON 3",
    291: "BUTTON 4",
    292: "BUTTON 5",
    293: "BUTTON 6",
    294: "BUTTON 7",
    295: "BUTTON 8",
}

# Buscar el dispositivo por vendor y product ID
def encontrar_dispositivo(vendor_id=0x0583, product_id=0xa000):
    """Busca el dispositivo HID por vendor y product ID"""
    base_path = "/sys/class/hidraw"
    
    if not os.path.exists(base_path):
        return None
    
    for hidraw in os.listdir(base_path):
        uevent_path = os.path.join(base_path, hidraw, "device", "uevent")
        
        if os.path.exists(uevent_path):
            with open(uevent_path, 'r') as f:
                content = f.read()
            
            # Buscar los IDs en el contenido
            if f"HID_ID={vendor_id:04x}:{product_id:04x}" in content:
                dev_path = os.path.join("/dev", hidraw)
                return dev_path
    
    # Alternativa: buscar en /dev/input/by-id o /dev/input/by-path
    input_by_id = "/dev/input/by-id"
    if os.path.exists(input_by_id):
        for entry in os.listdir(input_by_id):
            if "Joystick" in entry or "joystick" in entry:
                return os.path.join(input_by_id, entry)
    
    return None

# Leer descriptor HID
def leer_descriptor_hid(dev_path):
    """Lee el descriptor HID del dispositivo"""
    try:
        with open(dev_path, 'rb') as f:
            # Obtener tamaño del descriptor
            desc_size = struct.pack('I', 0)
            result = ioctl(f, HIDIOCGRDESCSIZE, desc_size)
            desc_size = struct.unpack('I', desc_size)[0]
            
            # Obtener descriptor completo
            desc = struct.pack('I', desc_size) + b'\x00' * HID_MAX_DESCRIPTOR_SIZE
            result = ioctl(f, HIDIOCGRDESC, desc)
            
            # Los primeros 4 bytes son el tamaño
            actual_size = struct.unpack('I', desc[:4])[0]
            descriptor_data = desc[4:4+actual_size]
            
            return descriptor_data
    except Exception as e:
        print(f"Error leyendo descriptor: {e}")
        return None

# Función principal para leer eventos
def leer_eventos_joystick():
    """Lee eventos del joystick"""
    
    # Primero intentar encontrar el dispositivo
    dev_path = encontrar_dispositivo()
    
    if not dev_path:
        # Si no lo encontramos por ID, buscar en /dev/input
        input_devices = []
        for i in range(32):  # Comprobar los primeros 32 dispositivos de entrada
            path = f"/dev/input/event{i}"
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        # Intentar leer un evento para ver si es accesible
                        pass
                    input_devices.append(path)
                except:
                    continue
        
        if not input_devices:
            print("No se encontraron dispositivos de entrada")
            return
        
        print("Dispositivos de entrada disponibles:")
        for i, dev in enumerate(input_devices):
            print(f"{i}: {dev}")
        
        try:
            choice = int(input("Selecciona el número del dispositivo: "))
            dev_path = input_devices[choice]
        except:
            print("Selección inválida")
            return
    else:
        print(f"Dispositivo encontrado: {dev_path}")
    
    # Abrir dispositivo de entrada para leer eventos
    event_path = dev_path
    if 'hidraw' in dev_path:
        # Convertir hidraw a event device
        hidraw_name = os.path.basename(dev_path)
        event_num = hidraw_name.replace('hidraw', '')
        event_path = f"/dev/input/event{event_num}"
    
    if not os.path.exists(event_path):
        # Buscar el event device correspondiente
        for i in range(32):
            test_path = f"/dev/input/event{i}"
            if os.path.exists(test_path):
                try:
                    # Verificar si es nuestro dispositivo
                    with open(test_path, 'rb') as f:
                        pass
                    event_path = test_path
                    break
                except:
                    continue
    
    print(f"Leyendo eventos de: {event_path}")
    
    try:
        with open(event_path, 'rb', buffering=0) as f:
            # Estructura del evento: ver linux/input.h
            # struct input_event {
            #     struct timeval time;
            #     unsigned short type;
            #     unsigned short code;
            #     unsigned int value;
            # }
            event_format = 'llHHI'  # timeval (2 longs), type, code, value
            event_size = struct.calcsize(event_format)
            
            print("Leyendo eventos del joystick. Presiona Ctrl+C para salir.")
            
            # Configurar poll/select para lectura no bloqueante
            poller = select.poll()
            poller.register(f, select.POLLIN)
            
            while True:
                # Esperar evento con timeout
                events = poller.poll(1000)  # Timeout de 1 segundo
                
                if events:
                    data = f.read(event_size)
                    if len(data) == event_size:
                        tv_sec, tv_usec, ev_type, ev_code, ev_value = struct.unpack(event_format, data)
                        
                        # Interpretar eventos
                        # Interpretar eventos (solo botones y ejes)
                        if ev_type == EV_KEY:
                            btn_name = BUTTON_NAMES.get(ev_code, f"BTN_{ev_code}")
                            state = "PRESIONADO" if ev_value == 1 else "LIBERADO"
                            print(f"Botón {btn_name} - {ev_code} {state}", flush=True)
                        elif ev_type == EV_ABS:
                            if ev_code == ABS_X: axis = "X"
                            elif ev_code == ABS_Y: axis = "Y"
                            else: axis = f"AXIS_{ev_code}"
                            print(f"Eje {axis} Valor: {ev_value}", flush=True)
                
                else:
                    # Timeout - ningún evento
                    pass
                    
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except PermissionError:
        print(f"Error de permisos: Necesitas ejecutar como root o tener permisos para leer {event_path}")
        print("Intenta con: sudo python3 script.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Lector de joystick USB HID (Método Nativo)")
    print("=" * 50)
    
    try:
        leer_eventos_joystick()
    except KeyboardInterrupt:
        print("\nSaliendo...")