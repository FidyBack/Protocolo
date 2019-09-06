#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################
# Arquivo baseado no código da matéria de Camada Física da Computação
# Lecionado no Insper, pelo professor Carareto
# Abel Cavalcante e Rodrigo de Jesus
# 05/09/2019
#######################################################################

print("Inicializado")

import time
from enlace import *
from pacote import *
from tkinter import filedialog, Tk

# Serial Com Port
#   python -m serial.tools.list_ports

serialName = "COM6"

def main():
    com = enlace(serialName)

# Ativa comunicacao e limpa a porta
    com.enable()
    time.sleep(0.1)
    com.fisica.flush()

# Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("porta : {}".format(com.fisica.name))
    print("-------------------------")

# Carrega dados
    print ("Gerando dados para transmissao :")
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    print("Arquivo selecionado: {}".format(str(filename)))

    with open(str(filename), "rb") as foto:
        txBuffer = foto.read()

# Empacota a mensagem e envia uma mensagem tipo 1
    pac = pacote()
    t1, t3 = pac.full_empacotacao(txBuffer)
    inicia = False

    while not inicia:
        com.sendData(t1)
        time.sleep(5)
        t2 = pac.recebedor(com)
        t2_info, t2_pac_tot, t2_indice = pac.ler_pacotes(t2)
        if t2_info.pack_type == 2 and t2_info.right == True:
            inicia = True

# Inicia a contagem dos pacotes e envia mensagens tipo 3
    contador = 1
    numPack = len(t3)

    while contador <= numPack:
        com.sendData(t3[contador-1])
        timer1 = time.time()
        timer2 = time.time()

# Desativa a porta
    com.disable()

# So roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
