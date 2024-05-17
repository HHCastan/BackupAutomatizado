#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Funciones varias y utilidades
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Octubre de 2016   
#######################################################################

import datetime
import sys
import os.path
import glob
import shutil
import tarfile
import ntpath
import smtplib
import mimetypes
import socket
import json
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import os4690

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.utils import COMMASPACE
from subprocess import call
from time import sleep
from ftplib import FTP, error_perm, error_temp, all_errors

ALMACEN_FILE=os4690.resolvepath('adx_idt1:almacen.dat')
HOSTS_FILE=os4690.resolvepath('c:/adx_sdt1/adxhsihf.dat')

#######################################################################
# Function fAyer
#######################################################################
# Devuelve la fecha de ayer en formato AAAAMMDD
#######################################################################
def fAyer():
    hoy    = datetime.date.today()        # Objeto con la fecha actual
    unDia = datetime.timedelta(days=1)
    ayer = hoy - unDia                # Objeto con la fecha de ayer
    return ayer.strftime("%Y%m%d")


#######################################################################
# Function fTienda
#######################################################################
# Devuelve el codigo de la tienda en almacen.dat
#######################################################################
def fTienda():
    f = open(ALMACEN_FILE, 'r')
    tienda = f.readline()
    f.close
    return tienda.strip()
    
   
#######################################################################
# Function fNmbTienda
#######################################################################
# Devuelve el codigo de la tienda en almacen.dat
#######################################################################
def fNmbTienda(id_Tienda, workDir):
    jsonFile    = workDir + 'Tiendas.JSON'              # Contiene list de tiendas y codigos
    JSON_FILE = os4690.resolvepath(jsonFile)
    # Abre archivo con lista de tiendas:
    with open(JSON_FILE) as files_file:
        # Carga el archivo en una estructura json en memoria:
        tiendas = json.load(files_file)

    nombre = tiendas[id_Tienda].replace(" ", "_")
    return nombre
    
   
   
#######################################################################
# Function fGetStoreList
#######################################################################
# Devuelve La lista de tiendas con sus ID - Consulta a InformesPOS
#######################################################################
def fGetStoreList():
    server = '172.16.8.115' 
    database = 'INFORMESPOS' 
    username = 'saldospos' 
    password = 'saldospos' 

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    cursor = cnxn.cursor()

    cursor.execute("SELECT ID, tomcatServer, IPUserData3 FROM TIENDAS_POS ORDER BY ID;")
    lista = cursor.fetchall()

    storeList = [i[0] for i in lista]

    return paternList


#######################################################################
# Function fGetPaternList
#######################################################################
# Devuelve en tuplas los patrones de un nombre de archivo con comodines 
#######################################################################
def fGetPaternList(sPatern):
    longitud = len(sPatern)
    p = 0
    paternList = []
    sAux = ''
    while (p < longitud):                    
        if (sPatern[p] == '[' or sPatern[p] == ']' ):
            if sAux != '':
                paternList.append(sAux)                        
            sAux = ''
            p+=1
            continue
        sAux+= sPatern[p]    
        p+=1
    if sAux != '':    
        paternList.append(sAux)        
    return paternList


#######################################################################
# Function fGetFixedTerminalList
#######################################################################
# Devuelve una lista con DNS de las terminales fijas 
#######################################################################
def fGetFixedTerminalList():
    # Lee host file para extraer lista de terminales fijas
    hostFile = open(HOSTS_FILE, "r")
    fixTrmList = []
    for line in hostFile:
        if line.find('DHCP') != -1:
            hostName = line[17:25]
            fixTrmList.append(hostName)

    hostFile.close
    return fixTrmList
    
    
#######################################################################
# Function fExtractJsonFE
#######################################################################
# extrae los JSON del log indicado en archivos independientes 
#######################################################################
def fExtractJsonFE(fileName, localDir, logFile):
    logFile.write('Inicia extraccion de cadenas Json de ' + fileName + '\n')
    jsonFile = open(fileName, "r")
    jsonFileList = []
    for line in jsonFile:
        if line.find('Request ws: {') != -1:
            try:
                jsonString = line[line.index('{'):]
                jsonTrx = json.loads(''.join(char for char in jsonString if ord(char) < 128))
                invoiceId =  jsonTrx["invoiceId"]
                logFile.write('Encuentra factura con id: ' + invoiceId + '\n')
                outFileName = localDir + '/' + invoiceId + '.json'
                outfile = open(outFileName, "wt")
                outfile.write(jsonString)
                outfile.close
                logFile.write('Archivo creado\n')
                jsonFileList.append(outFileName)
            except (all_errors, Exception) as why:
                logFile.write('Error: Procesando linea\n\t' + str(why) + '\n')

    jsonFile.close
    return jsonFileList
    
    
#######################################################################
# Function fReplacePatern
#######################################################################
# Resuelve los patrones de nombres de archivo
#######################################################################
def fReplacePatern(sPatern):
    sFormat = -1
    today = datetime.datetime.today()
    if sPatern == 'AAAA':
        sFormat = '%Y'
    elif sPatern == 'AA':
        sFormat = '%y'
    elif sPatern == 'MM':
        sFormat = '%m'
    elif sPatern == 'DD':
        sFormat = '%d'
    elif sPatern == 'TTT':
        return fTienda()
    else:
        return sPatern
    
    if sFormat != '-1':
        return today.strftime(sFormat)
    else:
        return sPatern
    
    
#######################################################################
# Function fResolveFileName
#######################################################################
# Resuelve el nombre de un archivo con patrones
#######################################################################
def fResolveFileName(sPatern):
    sFileName = ''
    paternList = fGetPaternList(sPatern)
    for patron in paternList:
        sFileName = sFileName + str(fReplacePatern(patron))
    return sFileName


#######################################################################
# Function fFilelist
#######################################################################
# Devuelve una lista de archivos basado en un nombre con metacarcteres
#######################################################################
def fFilelist(sMetaName, sourceDir):
    fileList = ''
    fullFileName = sourceDir + sMetaName
    fileList = glob.glob(fullFileName)
    return fileList


#######################################################################
# Function fCreatePath
#######################################################################
# Devuelve una lista de archivos basado en un nombre con metacarcteres
#######################################################################
def fCreatePath(targetDir):
    l = targetDir.split('/')
    fullPath = l[0]
    print (len(l), fullPath)
    i = 1
    while i < len(l):
        fullPath = fullPath + "/" + l[i]
        print (fullPath)
        if not os.path.exists(fullPath):
            os.mkdir(fullPath)
        i = i + 1


#######################################################################
# Function fCopyFile
#######################################################################
# Copia un archivo haciendo validaciones
#######################################################################
def fCopyFile(origen, targetDir, comprimir, logFile, nodoOrigen, destino):
    # Verifica la existencia el archivo a respaldar:
    if nodoOrigen == 'DD':
        fDownloadFTP_DD(origen, targetDir, logFile)
    else:
        if os.path.exists(origen):
            try:
                if comprimir == "true":  # Comprime archios y directorios
                    logFile.write('Comprimiendo ' + origen + '...\n')
                    with tarfile.open(targetDir + '.tar.gz', 'w:gz') as tf:
                        tf.addfile(origen)
                    tf.close
                else:
                    if os.path.isdir(origen):
                        logFile.write('Copiando Directorio ' + origen + '...\n')
                        shutil.copytree(origen, targetDir, symlinks, ignore)
                    else:
                        logFile.write('copy file ' + origen + ' ' + destino + '\n')
                        shutil.copyfile(origen, destino)
                        
            # Captura posibles errores y continua con los otros archivos
            except (IOError, os.error) as why:
                logFile.write('Error ' + origen + ' => ' + targetDir + '\n')
                logFile.write('    ' + str(why) + '\n')
                # Si llega a este punto es posible que haya fallado el copiado de python
                # se ensaya entonces con un copiado del sistema operativo:
                os.system('copy ' + origen + ' ' + destino)
                logFile.write('Archivo copiado por llamado al sistema. Ignorar error anterior\n')
#        except:
#            logFile.write(origen + ' => ' + targetDir + ' Error inesperado: \n' + sys.exc_info()[0])

#######################################################################
# Function fCopyUtil
#######################################################################
# Copia un archivo haciendo validaciones
#######################################################################
def fCopyUtil(sourceDir, targetDir, fileName, comprimir, logFile, nodoOrigen):
    # Reemplaza comodines de fechas
    if fileName.find('[') != -1:
        fileName = fResolveFileName(fileName)
    
    # Si tiene metacaracteres, halla la correspondiente lista de archivos
    if (fileName.find('*') != -1) or (fileName.find('?') != -1):
        fileList = fFilelist(fileName, sourceDir)
        for fichero in fileList:
            destino = targetDir + ntpath.basename(fichero)
            fCopyFile(fichero, targetDir, comprimir, logFile, nodoOrigen, destino)
    else:
        origen = sourceDir + fileName
        destino = targetDir + fileName
        fCopyFile(origen, targetDir, comprimir, logFile, nodoOrigen, destino)
    

#######################################################################
# Function fCopyDir
#######################################################################
# Copia los archivos de directorio a otro directorio destino
#######################################################################
def fCopyDir(sourceDir, targetDir, logFile, nodoOrigen):
    # Valida que se trata de un directorio
    if os.path.isdir(sourceDir):
        logFile.write('copy directory ' + sourceDir + ' ' + targetDir + '\n')
        names = os.listdir(sourceDir)
        for name in names:
            origen = os.path.join(sourceDir, name)
            destino = os.path.join(targetDir, name)
            fCopyFile(origen, targetDir, 'false', logFile, nodoOrigen, destino)
    else:
        logFile.write('No es un directorio: ' + sourceDir + '\n')
    

#######################################################################
# Function fCopyFromTrm
#######################################################################
# Copia un archivo desde una ubicacion en la terminal
#######################################################################
def fCopyFromTrm(hostTrm, origen, destino, logFile):
    comando = 'ADXSITQL -get -auth:123/123 ' + hostTrm + ' ' + origen + ' ' + destino
    #logFile.write('Comando de copiado: ' + comando + '\n')
    os.system(comando)
    

#######################################################################
# Function fRemoveFile
#######################################################################
# Elimina el archivo envido como parametro con su full path name
#######################################################################
def fRemoveFile(fullName):
    # verifica que exista el archivo para evitar una excepcion:
    if os.path.exists(fullName):
        os.system('del ' + fullName)
        


#######################################################################
# Function fEmptyFolder
#######################################################################
# Elimina el archivo envido como parametro con su full path name
#######################################################################
def fEmptyFolder(folderName):
    files = glob.glob(folderName + '*')
    print folderName + '*'
    for f in files:
        os.remove(f)
        


#######################################################################
# Function fTarBackup
#######################################################################
# genera un empaquetado tipo tar con los archivos de la ruta especificada
#######################################################################
def fTarBackup(tgzFile, workDir, logFile):
    logFile.write("Inicia empaquetado de archivos respaldados...\n")
    with tarfile.open(tgzFile, 'w:gz') as tf:
        os.chdir(workDir)
        tf.add(name='out')
    tf.close
    logFile.write("Termina empaquetado de archivos respaldados...\n")

    
#######################################################################
# Function fUnTarBackup
#######################################################################
# genera un empaquetado tipo tar con los archivos de la ruta especificada
#######################################################################
def fUnTarBackup(tgzFile, workDir, logFile):
    logFile.write("Inicia desempaquetado de archivos respaldados...\n")
    tf = tarfile.open(tgzFile)
    os.chdir(workDir)
    tf.extractall()
    tf.close
    logFile.write("Termina desempaquetado de archivos respaldados...\n")

    
#######################################################################
# Function fUploadFileFTP
#######################################################################
# Hace FTP del backup al destino especificado
#######################################################################
def fUploadFileFTP(sourceFilePath, destinationDirectory, server, port, username, password, logFile):
    logFile.write("Inicia transmision de archivo empaquetado...\n")
    logFile.write('Server: '+ server + '\n')
    logFile.write('File: '+ sourceFilePath + '\n')
    
    try:
        myFTP = FTP()
        myFTP.connect(server, port)
        myFTP.login(username, password)
        # Changing Working Directory
        myFTP.cwd(destinationDirectory)
        if os.path.isfile(sourceFilePath):
            fh = open(sourceFilePath, 'rb')
            fileName = ntpath.basename(sourceFilePath)
            myFTP.storbinary('STOR ' + fileName, fh)
            fh.close()
        else:
            logFile.write('No existe archivo a enviar\n')

        logFile.write("Termina transmision de archivo empaquetado...\n")
    except (all_errors, Exception) as why:
        logFile.write("Error: No se puede enviar FTP\n\t" + str(why))

        
#######################################################################
# Function fWalkDir
#######################################################################
# Hace FTP del backup al destino especificado
#######################################################################
def fWalkDir(f, dirpath, target, logFile):
    original_dir = f.pwd()
    try:
        f.cwd(dirpath)
    except error_perm:
        return  # ignora lo que no es directorio
    try:
        names = []
        lineas = []
        f.retrlines('LIST', lineas.append)
        for linea in lineas:
            nombre = linea.split()[-1]
            if (nombre not in ('.', '..')):
                names.append(nombre)
        # Si llega a este punto es por que es una carpeta y se crea local
        try:
            os.mkdir(target + dirpath[3:])
        except OSError:
            # La carpeta ya existia
            pass
    except error_perm:
        return  # ignora lo que no es directorio
    except error_temp:
        pass

    for name in names:
        fWalkDir(f, dirpath + '/' + name, target, logFile)
        origen = dirpath + '/' + name
        destino = target + dirpath[3:] + '/' + name
        try:
            logFile.write("FTP desde DD: " + origen + "\n")
            f.retrbinary("RETR "+origen, open(destino,"wb").write)
        except IOError:
            pass
        except error_temp:
            # error temporal en conexion, reintentando...
            sleep(1)
            try:
                f.retrbinary("RETR "+origen, open(destino,"wb").write)
            except error_temp:
                logFile.write('No se pudo traer: ' + origen + '\n')
    f.cwd(original_dir)  # Retorna a la posicion cuando lo llamaron
    
    
#######################################################################
# Function fDownloadFTP_DD
#######################################################################
# Hace FTP del backup al destino especificado
#######################################################################
def fDownloadFTP_DD(sourceDir, targetDir, logFile):
    logFile.write("Inicia transmision desde nodo DD ")
    logFile.write(sourceDir + "=>" + targetDir + "\n")
    
    ftpDD = FTP('DD', 'ftpuser', '4690tcpip', timeout=3600)
    ftpDD.set_pasv(False)

    # Configura el socket:
    # El KEEPALIVE se activa cada 1 segundo de osio del puerto (KEEPIDLE), 
    # Entonces envia el KEEPALIVE una vez cada 2 segundos (KEEPINTVL),
    # Finalmente, cierra la conexion despues de 5 pings fallidos (KEEPCNT)
    ftpDD.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    ftpDD.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
    ftpDD.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
    ftpDD.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

    fCreatePath(targetDir + 'derby')

    fWalkDir(ftpDD, sourceDir, targetDir, logFile)
    ftpDD.quit()

    
#######################################################################
# Function: fSendEmail
# Autor: Hugo Castaneda
# Fecha: Octubre 2016
#######################################################################
# Hace envio del archivo de log
#######################################################################    
def fSendEmail(eMailFrom, eMailTo, eMailSMTP, eMailPort, eMailSubjct, eMailBody, attachFile):
    eMailMsg = MIMEMultipart()
    eMailMsg['From'] = eMailFrom
    eMailMsg['To'] = ",".join(eMailTo.split(','))
    eMailMsg['Subject '] = eMailSubjct
    
    fp = open(attachFile)
    attachment = MIMEText(fp.read(), _subtype="text")
    sleep(5)
    fp.close
    fileName = ntpath.basename(attachFile)

    attachment.add_header("Content-Disposition", "attachment", filename=fileName)
    newBody = MIMEText(eMailBody, 'plain')
    eMailMsg.attach(newBody)
    eMailMsg.attach(attachment)
    try:
        server = smtplib.SMTP(eMailSMTP, eMailPort)
        text = eMailMsg.as_string()
        server.sendmail(eMailFrom, eMailTo.split(','), text)
        server.quit()
    except (Exception, smtplib.SMTPException) as why:
        print ("Error: No se puede enviar correo")
        print ('    ' + str(why))

#######################################################################
# Function getFechaVtaxPLU
#######################################################################
# Devuelve la fecha del VTAXPLU en ADX_UDT1
#######################################################################
def getFechaVtaxPLU():
    fileName = 'c:/adx_udt1/VTAXPLU.DAT'
    f = open(fileName, 'r')
    mensaje = f.readline()
    mensaje = f.readline()
    campos = mensaje.split(",")
    fechaHoraAlmacen = campos[13]
    return '20' + fechaHoraAlmacen[:6]
    

#######################################################################
# Function ping
#######################################################################
# Returns True if host (str) responds to a ping request.
# Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
#######################################################################
def ping(host):
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0
    
    