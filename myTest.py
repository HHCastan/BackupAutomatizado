'''
Ejecutar: python2 -X4690shell myTest.py

'''
import flFuncts
import os
import ConfigParser
import time
import socket
import ntpath
import json
import shutil
fechaVTA    = flFuncts.getFechaVtaxPLU()            # Fecha interna del archivo VTA
diaVTA      = fechaVTA[6:]                          # Dia interno del archivo VTA
mesVTA      = fechaVTA[4:-2]                        # Mes interno del archivo VTA en letras
anioVTA     = fechaVTA[:4]                          # Anio interno del archivo VTA
print fechaVTA
print diaVTA
print mesVTA
print anioVTA
