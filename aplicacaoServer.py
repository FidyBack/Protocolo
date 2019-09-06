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

# Recebe dados da mensagem tipo 1 e envia a mensagem tipo 2
    pac = pacote()
    ocioso = True

    while ocioso:
        t1 = pac.recebedor(com)
        t1_info, t1_pac_tot, t1_indice = pac.ler_pacotes(t1)
        if t1_info.pack_type == 1 and t1_info.right == True:
            if t1_info.recive == pac.identif:
                ocioso = False
        time.sleep(1)

    t2 = pac.empacotar(tipo = 2)
    com.sendData(t2)

# Inicia a contagem dos pacotes e recebe mensagens tipoo 3
    contador = 1
    numPack = t1_pac_tot
    despacotamento = info_all_packs()

    while contador <= numPack:
        timer1 = time.time()
        timer2 = time.time()
        t3 = pac.recebedor(com)
        t3_info, t3_pac_tot, t3_indice = pac.ler_pacotes(t3)
        despacotamento.insert_pack(t3)

# Desativa a porta
    com.disable()

# So roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
