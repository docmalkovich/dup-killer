# prog principal, pas de GUI
# python 3.7

import sys, os
import configparser     # pour fichier de config
import hashlib          # pour calculer le hash MD5
import time
from collections import defaultdict # pour DBdups
import pickle           # pour sauvegarder la BDD 
import csv              # pour générer un csv
import argparse

# variables globales
InputDirectory=[]
PreserveDir=[]
PreserveDirExcept=[]
DatabaseFile=''
OutputFile=''
DBFiles={}                  # bdd/dict sur les fichiers
                            #   clé = path + filename
                            #   val = [path,file,size,dtmodif,md5,preserve]
DBdups=defaultdict(list)    # bdd/dict sur les fichiers
                            #   clé = clé de hash / groupe de doublons
                            #   val = liste des fichiers en doublons (list comme DBfiles + delete)
#FileCount=0
chkFilename=False
chkSize=False
chkDtmodif=False
chkMD5=False
calculMD5=False
verboseMode=False
writeDeleteOnly=False

def readConfigFile(ConfigFileName):
    global InputDirectory, PreserveDir, DatabaseFile, OutputFile
    global chkFilename, chkSize, chkDtmodif, chkMD5, calculMD5, writeDeleteOnly

    if not os.path.exists(ConfigFileName) :
        printLog('Error: Config File not found : '+ConfigFileName)
        sys.exit(-1)
    printLog("lecture de "+ConfigFileName)
    config = configparser.ConfigParser()
    config.read(ConfigFileName)

    # Loop through the params and add them to the list.
    if config.has_section('InputDirectories'):
        for x in config['InputDirectories']:
            InputDirectory.append(config['InputDirectories'][x])
    if config.has_section('PreserveDirectories'):
        for x in config['PreserveDirectories']:
            PreserveDir.append(config['PreserveDirectories'][x])
    if config.has_section('PreserveDirectoriesExceptions'):
        for x in config['PreserveDirectoriesExceptions']:
            PreserveDirExcept.append(config['PreserveDirectoriesExceptions'][x])
    if config.has_section('Params'):
        DatabaseFile=config['Params']['DatabaseFile']
        OutputFile=config['Params']['OutputFile']
        f=lambda x: True if config['Params'][x]=='Yes' else False
        chkFilename=f('SameName')
        chkSize=f('SameSize')
        chkDtmodif=f('SameDateModif')
        chkMD5=f('SameMD5')
        calculMD5=f('CalculateMD5')
        writeDeleteOnly=f('WriteDeleteOnly')

    if len(InputDirectory)==0:
        printLog('Error: at least ONE input directory is required')
        sys.exit(-1)
    if not (chkFilename or chkSize or chkDtmodif or chkMD5) :
        printLog('Error: at least ONE comparison criteria is required (name, size, time, or md5)')
        sys.exit(-2)

    for Inputs in InputDirectory:
        printLog('Input directory:   '+Inputs)
    for Preserves in PreserveDir:
        printLog('Preserve directory:'+Preserves)
    printLog('Database file     :'+DatabaseFile)
    printLog('Output file       :'+OutputFile)

def printProgress(n) :
    if not (n % 10) :
        print("-",end='',flush=True)

def printLog(txt):
    print(txt)
    
def printLogVerbose(txt):
    if verboseMode :
        printLog(txt)

#   Given a full filepath and filename - is this a file thats in the 'preserve' list?
def checkPreserve(fname):
    DoPreserve=0
    for PreservePath in PreserveDir:
        if fname[:len(PreservePath)] == PreservePath:
            DoPreserve=1
            for exc in PreserveDirExcept:
                if fname[:len(exc)] == exc:
                    DoPreserve=0
    return DoPreserve

# genere md5
def generateMD5(fname, chunk_size=1024):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        # Read the 1st block of the file
        chunk = f.read(chunk_size)
        # Keep reading the file until the end and update hash
        while chunk:
            hash.update(chunk)
            chunk = f.read(chunk_size)
    # Return the hex checksum
    return hash.hexdigest()

def scanDir(walk_dir) :
    global DBFiles
    #global FileCount
    
    printLog("scan de "+walk_dir)
    p=0
    for root, subdirs, files in os.walk(walk_dir, followlinks=False):
        for filename in files:
            p+=1
            printProgress(p)

            file_path = os.path.join(root, filename)
            #   Are we looking at a 'real' file?
            if os.path.isfile(file_path) and not os.path.islink(file_path):
                #FileCount = FileCount + 1
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file_path)
                # besoin de calculer le md5 ?
                # val=[path,file,size,mtime,md5,preserve]
                if calculMD5 :
                    if file_path in DBFiles and  (size == DBFiles[file_path][2] and mtime == DBFiles[file_path][3]) :
                        printLogVerbose("pas de recalcul de MD5 sur "+file_path)
                        md5=DBFiles[file_path][4]
                    else:
                        printLogVerbose("calcul du MD5 sur "+file_path)
                        md5="todo"
                else :
                    md5=""
                preserve=checkPreserve(file_path)
                DBFiles[file_path]=[root, filename, size, mtime, md5, preserve]
    printLog('')  # retour à la ligne pour la barre de progression
                
def scanAll() :
    #global FileCount

    # nettoyage
    printLog("nettoyage de la base")
    p=0
    DBDEL=[]
    for f in DBFiles.keys() :
        p+=1
        printProgress(p)
        if not os.path.isfile(f) :
            printLogVerbose("suppression de "+f+" dans la base")
            DBDEL.append(f)
    for f in DBDEL :
        del DBFiles[f]
    printLog('')  # retour à la ligne pour la barre de progression
    # scan des répertoires
    printLog("scan des répertoires")
    #FileCount=0
    for x in InputDirectory :
        scanDir(x)
    for x in PreserveDir :
        scanDir(x)
    printLog('... '+str(len(DBFiles))+' fichiers trouvés')
    # calcul MD5
    if calculMD5 :
        printLog('Calcul des MD5')
        cpt=0
        for f,v in DBFiles.items() :
            cpt+=1
            if v[4]=="todo" :
                try:
                    md5=generateMD5(f)
                    v[4]=md5
                except IOError :
                    printLog("Permission refusée de lire "+f)
            printProgress(cpt)
        printLog('')  # retour à la ligne pour la barre de progression
   
def identifyDups() :
    global DBdups
    
    n=0
    printLog("calcul groupes fichiers par cle")
    for f in DBFiles.values() :
        key=""
        #   val = [path,file,size,dtmodif,md5,preserve]
        key=key+"_"+(f[1] if chkFilename else "")
        key=key+"_"+(str(f[2]) if chkSize else "")
        key=key+"_"+(str(f[3]) if chkDtmodif else "")
        key=key+"_"+(str(f[4]) if chkMD5 else "")
        printLogVerbose("clé="+key)
        if key=="" :
            printLog("pas de critère pour dédoublonner")
            sys.exit(-2)
        DBdups[key].append( f + [0])  # ajout en + de delete
        n+=1
        printProgress(n)
    printLog('')  # retour à la ligne pour la barre de progression
    printLog("elimination fichiers qui ne sont pas en doublons")
    DBdupsDEL=[]
    for key,files in DBdups.items() :
        if len(files)==1 :
            DBdupsDEL.append(key)
    printLog("... " +str(len(DBdupsDEL))+" fichiers qui ne sont pas en doublons")
    for f in DBdupsDEL :
        del DBdups[f]
    printLog("... " +str(len(DBdups))+" groupes de fichiers en doublons")
    printLog("determination des fichiers à supprimer")
    FileCount=0
    # maj du champ delete à 1 :
    #   si la ligne n'est pas à preserver (preserve=0)
    #   et si soit il y a une ligne à preserver dans le groupe de doublons
    #         soit c'est la 2de ligne (on garde la 1ère ligne) ou les suivantes
    for key,files in DBdups.items() :
        n=0
        for x in files :
            n=n+(1 if x[5]==1 else 0)   # compteur sur ligne à préserver
        for x in files :
            n=n+1
            if n>1 and x[5]==0 :        # si la ligne peut être supprimée et (si 2ème ligne ou existe preserve) 
                x[6]=1
                FileCount+=1
    printLog("... "+str(FileCount)+" fichiers à supprimer")

def saveDBFiles() :
    printLog("Sauvegarde dans "+DatabaseFile)
    file_DB=open(DatabaseFile, 'wb') 
    pickle.dump(DBFiles, file_DB)
    file_DB.close()

def readDBFiles() :
    global DBFiles

    if os.path.isfile(DatabaseFile) :
        printLog("Import de "+DatabaseFile)
        file_DB=open(DatabaseFile, 'rb') 
        DBFiles=pickle.load(file_DB)
        file_DB.close
        printLogVerbose(str(len(DBFiles))+" files imported")
    else :
        printLog("No file found for "+DatabaseFile)

def writeDupsCsv() :
    filename=OutputFile+".csv"
    printLog("Ecriture de "+filename)
    file_csv=open(filename, "w") 
    csv_writer=csv.writer(file_csv, quoting=csv.QUOTE_MINIMAL, delimiter=",", lineterminator="\n")
    header = ["group","path","file","size","dtmodif","md5","preserve","delete"]
    csv_writer.writerow(header)
    n=0
    for files in DBdups.values() :
        n=n+1
        for x in files :
            try :
                csv_writer.writerow(list(str(n)) + x)
            except:
                printLog("Erreur sur "+str(n)+":"+x[0]+"/"+x[1])
    file_csv.close()

def writeDupsShell() :
    filename=OutputFile+".bat"
    printLog("Ecriture de "+filename)
    #file_sh=open(filename, "w", encoding="cp850")  # En Europe, cp dans le cmd
    file_sh=open(filename, "w", encoding="cp1252")  # En Europe, cp dans le cmd
    file_sh.write("chcp 1252\n")
    for key, files in DBdups.items() :
        try :
            if not writeDeleteOnly :
                file_sh.write("\nREM GROUPKEY="+key+"\n")
            for x in files :
                if x[5] :
                    # preserve
                    pfx="REM PRESERVE"
                elif x[6] :
                    # delete
                    pfx="DEL"
                else :
                    # dup but not delete
                    pfx="REM DUP"
                txt=pfx+" \""+os.path.join(x[0],x[1])+"\"\n"
                if pfx=="DEL" or not writeDeleteOnly :
                    file_sh.write(txt)
        except :
            printLog("Erreur sur "+key)
    file_sh.write("pause")
    file_sh.close()

#### TODO : ajout d'autres arguments
def parseArgs() :
    global verboseMode

    parser = argparse.ArgumentParser(description="Delete duplicate files")
    #parser.add_argument("-d", "--directory", action="append", help="directory to scan")	
    #parser.add_argument("-p", "--preserve", action="append", help="directory to preserve")	
    parser.add_argument("-c", "--config", action="store", help="config file", required=True)
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    args = parser.parse_args()
    readConfigFile(args.config)
    verboseMode=args.verbose
 
########################################################################################################
##                 MAIN CODE
########################################################################################################

if __name__ == "__main__":
    parseArgs()
    readDBFiles()
    scanAll()
#    sys.exit(0)
    saveDBFiles()
    identifyDups()
    writeDupsCsv()
    writeDupsShell()
    #pause
    os.system("pause")


