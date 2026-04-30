############################################################
# Programa Proyecto Final
#
# El siguiente programa escrito con micropython simula lo siguiente:
# Los leds prenden de acuerdo a un patrón y duración definidos
# durante ese tiempo el usuario debe presionar el botón correspondiente
# de ese led, para poder sumar puntos, en caso contrario perdera una vida
# de las 3 que tiene inicialmente, el juego corre dentro de un bucle
# donde se detiene cuando ya no le quede ninguna vida y por consiguiente
# se muestra su puntuación
#
############################################################

# Librerias de micropython 
from machine import Pin, PWM
import time
from time import sleep_ms, ticks_ms, ticks_diff
import _thread




# SEMAFORO(también llamado bloqueo)
baton = _thread.allocate_lock()

# SPEAKER
speaker = machine.PWM(machine.Pin(5))

# PUNTUACIÓN
puntuacion = 0

# VIDAS
vidas = 3

# NOTAS
ab = 415
a = 440
g = 392
c_especial = 520
b_especial = 500

c4 = 261 # Nota C4 con 261 de frecuencia en hz
g4 = 391
a4 = 440
f4 = 349
e4 = 329
d4 = 293
do_reb = 277
si4 = 246

# VARIABLE PULSAR
last_press_time = 0

# LEDS
led_rojo = Pin(16, Pin.OUT)
led_azul = Pin(17, Pin.OUT)
led_verde = Pin(18, Pin.OUT)
led_amarillo = Pin(19, Pin.OUT)

led_rojo.value(0)
led_azul.value(0)
led_verde.value(0)
led_amarillo.value(0)

#PUSH BUTTONS
push_rojo = Pin(6, Pin.IN, Pin.PULL_UP)
push_azul = Pin(13, Pin.IN, Pin.PULL_UP)
push_verde = Pin(14, Pin.IN, Pin.PULL_UP)
push_amarillo = Pin(15, Pin.IN, Pin.PULL_UP)

# Display 7 segmentos para vidas

segmentos = [
    Pin(28, Pin.OUT), # g
    Pin(27, Pin.OUT), # f
    Pin(2, Pin.OUT),  # e
    Pin(3, Pin.OUT),  # d
    Pin(4, Pin.OUT),  # c
    Pin(22, Pin.OUT), # b
    Pin(26, Pin.OUT), # a
    ]

#Funciones LEDS de vidas

def cero():
    cero_leds = [1,0,0,0,0,0,0] #Anodo comun VCC
    for i in range(len(cero_leds)):
            segmentos[i].value(cero_leds[i])
            
def uno():
    uno_leds = [1,1,1,1,0,0,1]
    for i in range(len(uno_leds)):
            segmentos[i].value(uno_leds[i])

def dos():
    dos_leds = [0,1,0,0,1,0,0]
    for i in range(len(dos_leds)):
            segmentos[i].value(dos_leds[i])

def tres():
    tres_leds = [0,1,1,0,0,0,0]
    for i in range(len(tres_leds)):
            segmentos[i].value(tres_leds[i])
            
# Funciones para reproducir notas
def play_note_alone(nota, duracion_seg, tiempo_de_espera):
    speaker.duty_u16(int(65535/2))
    speaker.freq(nota)
    start_time = ticks_ms()
    duracion_ms = duracion_seg * 1000
    while ticks_diff(ticks_ms(), start_time) < duracion_ms:
        pass
    speaker.duty_u16(int(0))
    time.sleep(tiempo_de_espera)
    
def play_note(nota, duracion, tiempo_de_espera):
    speaker.duty_u16(int(65535/2))
    speaker.freq(nota)
    time.sleep(duracion)
    speaker.duty_u16(int(0))
    time.sleep(tiempo_de_espera)
    
# Funcion principal del juego para prender led   
def play_led(led, duracion_seg, tiempo_de_espera, push, vidas):
    global puntuacion
    led.value(1)
    start_time = ticks_ms()
    duracion_ms = duracion_seg * 1000
    boton_presionado = False # Declaración de variable bool en falso indicando que el botón no está presionado
# Mientras que el tiempo transcurrido desde que se prendió el led(duración)
    while ticks_diff(ticks_ms(), start_time) < duracion_ms:
        if push.value() == 0:  # Botón presionado
            boton_presionado = True # Se cambia el estado del botón indicando que se presionó
            break  # Salimos del bucle una vez que se presiona el botón
        time.sleep(0.01)  # Dormir por un corto periodo para liberar CPU

    led.value(0)#Se apaga el Led para indicar que se ha presionado

# En caso de que nunca se presionó dentro del tiempo
    if not boton_presionado:
        print("menos una vida")
        #Restar una vida a las vidas que se tenían
        vidas -= 1
        calc_vidas(vidas) # Devolver en el display la cantidad de vidas actualizada
    else:
        print("bien")
        # Sumarle 126 de puntuación
        puntuacion += 126
        calc_vidas(vidas) # Devolver en el display la cantidad de vidas actualizada

    time.sleep(tiempo_de_espera)
    return vidas  # Devolver el valor actualizado de vidas
    calc_vidas() # Devolver en el display la cantidad de vidas actualizada
    
# Función para mostrar las vidas en el display según las vidas que queden
def calc_vidas(vidas):
    if vidas == 3:
        tres()
    elif vidas == 2:
        dos()
    elif vidas == 1:
        uno()
    elif vidas == 0:
        cero()

def play_fail_sound():
    play_note(d4, 0.5, 0)
    play_note(do_reb, 0.4,0)
    play_note(c4, 0.3,0)
    play_note(si4, 0.2, 0.001)
    play_note(si4, 0.2, 0.001)
    play_note(si4, 0.2, 0.001)
    play_note(si4, 0.2, 0.001)
    
def led_wait_time(duracion):
    start_time = ticks_ms()
    elapsed_time = ticks_diff(ticks_ms(), start_time)
    if elapsed_time < duracion:  # Si no han pasado segundos completos desde que se apagó el LED
        time.sleep_ms(duracion - elapsed_time)  # Esperar el tiempo restante antes de iniciar el LED
    
# Segundo hilo
        
def second_thread():
    global vidas
    while vidas > 0:
        if not push_rojo.value():
            play_note_alone(c_especial, 0.1, 0)
        if not push_azul.value():
            play_note_alone(c4, 0.1, 0)
        if not push_verde.value():
            play_note_alone(e4, 0.1, 0)
        if not push_amarillo.value():
            play_note_alone(a, 0.1, 0)
        

_thread.start_new_thread(second_thread, ())


calc_vidas(vidas)
time.sleep(1)
# Llama a las funciones de play_led en el bucle principal
while True:
    # Adquirimos el bloqueo del semáforo
    baton.acquire()
    vidas = play_led(led_azul, 0.5, 0, push_azul, vidas)
    if vidas <= 0:
        break
    led_wait_time(500)
    
    vidas = play_led(led_amarillo, 0.3, 0, push_amarillo, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    
    vidas = play_led(led_verde, 0.4, 0, push_verde, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_amarillo, 0.3, 0, push_amarillo, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    
    vidas = play_led(led_rojo, 0.4, 0, push_rojo, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_amarillo, 0.4, 0, push_amarillo, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_verde, 0.5, 0, push_verde, vidas)
    if vidas <= 0:
        break
    led_wait_time(500)
    
    vidas = play_led(led_azul, 0.3, 0, push_azul, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    
    vidas = play_led(led_amarillo, 0.3, 0, push_amarillo, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    
    vidas = play_led(led_rojo, 0.4, 0, push_rojo, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_verde, 0.3, 0, push_verde, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    
    vidas = play_led(led_amarillo, 0.3, 0, push_amarillo, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    
    vidas = play_led(led_azul, 0.4, 0, push_azul, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_rojo, 0.2, 0, push_rojo, vidas)
    if vidas <= 0:
        break
    led_wait_time(200)
    
    vidas = play_led(led_azul, 0.4, 0, push_azul, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_amarillo, 0.2, 0, push_amarillo, vidas)
    if vidas <= 0:
        break
    led_wait_time(200)
    
    vidas = play_led(led_verde, 0.4, 0, push_verde, vidas)
    if vidas <= 0:
        break
    led_wait_time(400)
    
    vidas = play_led(led_verde, 0.3, 0, push_verde, vidas)
    if vidas <= 0:
        break
    led_wait_time(300)
    # Liberamos el bloqueo del semáforo
    baton.release()

if vidas == 0:
    play_fail_sound()
    print("Puntuación final:", puntuacion)


