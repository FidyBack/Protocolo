
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Carareto
# 17/02/2018
# Aplicação 
####################################################

print("Inicializado")

from enlace import *
import time
from tkinter import filedialog, Tk
from pacote import *

# Serial Com Port
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "COM6"                  # Windows(variacao de)

def main():
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    
    # Ativa comunicacao e limpa a porta
    com.enable()
    time.sleep(0.1)
    com.fisica.flush()

    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega dados
    print ("Gerando dados para transmissao :")
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    print("Arquivo selecionado: {}".format(str(filename)))

    with open(str(filename), "rb") as foto:
        txBuffer = foto.read()

    # Empacota o arquivo de acordo com o protocolo
    pac = pacote()
    send = pac.empacotar(txBuffer)
    lenSend = len(send)
    LenSendByte = lenSend.to_bytes(8,"big")

    # Transmite dados
    start = time.time()
    com.sendData(LenSendByte)
    time.sleep(0.01)
    com.sendData(send)

    # Comparação visual entre as imagens
    print("-------------------------")
    print("Imagem Original")
    print("-------------------------\n")
    print(txBuffer)
    print("\n-------------------------")
    print("Imagem Empacotada")
    print("-------------------------\n")
    print(send)
    print("-------------------------")

    # Recebe confirmacao do tamanho da imagem e converte 
    lenData, len1 = com.getData(8)
    size = int.from_bytes(lenData, "big")

    print("Tamanho Recebido: {}".format(size))
    if lenData == LenSendByte:
        print("Dados coerentes")
    else:
        print("Dados incoerentes, tente novamente")
        com.disable()

    # Encerra e passa dados de comunicação
    final = time.time() - start
    print("Tempo de comunicação: {}".format(final))
    print("Taxa de Tranferência: {}".format(size/final))
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

# So roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
