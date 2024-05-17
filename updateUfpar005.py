import pyodbc
from ftplib import FTP, error_perm, error_temp, all_errors
import ntpath

class Updateufpar005:

    def updateufpar(id, ip):

        # Conexión a la base de datos
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=172.16.8.115;DATABASE=DB_SICAF;UID=consultapos;PWD=nzcs6urC')

        # Cursor para ejecutar consultas SQL
        cursor = conn.cursor()

        # La siguiente linea es temporal mientras se prueba en Windows:
        id_tienda = id #'005' dato anterior
        
        # Luego se reemplaza por esta:
        #id_tienda	= flFuncts.fTienda()					# Identificacion de tienda
        if int(id_tienda) < 100:
            id_tienda = id_tienda[-2:]
        print(id_tienda) #print para ver en que numero de tienda va!

        try:
            # Consulta SQL para obtener los datos de la tabla TALMACENES
            cursor.execute("SELECT DALMACEN, DIRECCION FROM TALMACENES WHERE CALMACEN = " + id_tienda )

            # Obtenemos el primer registro (asumiendo que solo hay uno)
            row = cursor.fetchone()
            if row:
                dalmacen = row[0]
                direccion = row[1]

                # Abrir el archivo UFPAR005.NEW y leer su contenido
                with open('UFPAR005.NEW', 'r') as file:
                    lines = file.readlines()

                # Insertar los valores en las líneas 32 y 33 del archivo
                lines[31] = 'HeaderVoucher                       =4|FLAMINGO ' + dalmacen + '\n'
                lines[32] = 'HeaderVoucher                       =4|' + direccion + '\n'

                # Escribir el contenido modificado en el archivo
                with open('UFPAR005.NEW', 'w') as file:
                    file.writelines(lines)
                #mensaje con el nombre y el numero del almacen, confirmacion de creacion de archivo
                print("Valores insertados correctamente en el archivo de {}/{}.".format(dalmacen,id_tienda))

            else:
                print("No se encontraron registros en la tabla TALMACENES.")

        except Exception as e:
            print("Error:", e)

        finally:
            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()



    def transfer(id, ip):

        FTPServer = ip
        FTPPort = 21
        FTPuser = 'ftpuser'
        FTPPasswd = '4690tcpip'
        myFTP = FTP()
        id_tienda = id
        filename = '' # anterior 'UFPAR005.NEW'
        
        # La carpeta donde se copian los tlogs al servidor FTP:
        targetDir = 'c:/adx_idt1' 
        print('targetDir' + targetDir)
        # Inicia la transferencia
        try:
            print('Estableciendo conexion con ' + FTPServer + '\n')
            myFTP = FTP()
            myFTP.connect(FTPServer, FTPPort)
            myFTP.login(FTPuser, FTPPasswd)
            # Cambia al directorio destno. Si no existe, lo crea
            def cdTree(targertDir):
                if targertDir != "":
                    try:
                        myFTP.cwd(targetDir) #ruta o directoio actual
                    except (all_errors, Exception, IOError):
                        print("Error en directorio destino!!")
            
            cdTree(targetDir)
            ufpar = 'UFPAR005.NEW'
            fh = open(ufpar, 'rb')
            fileName = ntpath.basename(ufpar)
            myFTP.storbinary('STOR ' + ufpar, fh)
            fh.close()

            print("Termina transmision de ufpar!")
        except (all_errors, Exception) as why:
            print("Error: No se puede enviar FTP: " + str(why))
            nroErrores += 1




    #establecemos una conexion con la base de datos
    conninfopos = pyodbc.connect('DRIVER={SQL Server};SERVER=172.16.8.115;DATABASE=INFORMESPOS;UID=saldospos;PWD=saldospos')
    #generamos un cursor
    cursorinfopos=conninfopos.cursor()
    #ejecutamos un select a la tabla tiendas_pos
    cursorinfopos.execute("SELECT id, ip FROM tiendas_pos")
    #recorremos la consulta con los datos id e ip
    for row in cursorinfopos.fetchall():
#        try:
            id=row[0]
            ip=row[1]
            #print("ID: {}, IP: {}".format(id, ip))
            try:
                updateufpar(id, ip)
            except:
                pass
            try:
                transfer(id, ip)
            except:
                pass
#        except (all_errors, Exception) as why:
#	        print("Error: No se puede enviar FTP    " + str(why))

    conninfopos.close()
    cursorinfopos.close()




