# dup-killer
Duplicate files finder and delete

VF plus bas !

Strongly inspired by Carl Beech's fast-duplicate-finder (https://github.com/carlbeech/fast-duplicate-finder)
With some modifications :
- Search duplicates on different possible criteria (name and date of modification for example), this allows a very fast and simple analysis without going through the calculation of MD5
- Added directories in preserve_exception (see explanations below)
- Only works on Windows
- but works on Windows in French
- necessarily requires a configuration file
- necessarily requires a backup file of the database

For the anecdote, I have not managed to correctly run Carl's source program, so I started in my own program ...

How to use : 
c:\git\dup-killer>dup_killer.py [-v] -c <config_file>

the <config_file> file is an .INI file whose content is structured as:
---------------------------------------------------------------------------------------------
[InputDirectories]
# directories to scan (1 min)
InputDirectory=C:\git\test\dups     
InputDirectory2=C:\git\test\dups2   

[PreserveDirectories]
# directories to keep (optional)
PreserveDirectory=C:\git\test\preserve
PreserveDirectory2=C:\git\test\dups\preserve

[PreserveDirectoriesExceptions]
# directories to delete in PreserveDirectories (optional)
DeleteDirectory=C:\git\test\preserve\temp
DeleteDirectory2=C:\git\test\dups\preserve\temp

[Params]
DatabaseFile=C:\git\test\cfg\bdd_files.pck
OutputFile=C:\git\test\cfg\output
CalculateMD5=Yes
SameName=Yes
SameSize=Yes
SameDateModif=No
SameMD5=Yes
WriteDeleteOnly=No
---------------------------------------------------------------------------------------------

The program scans the directories in [InputDirectories] and [PreserveDirectories].
It identifies duplicate files that have the same criteria: Name, Size, Modification Date, and / or MD5 (SameName, SameSize, SameDateModif, SameMD5).
It distinguishes the files to delete from those to keep (in [PreserveDirectories] and out [PreserveDirectoriesExceptions])
It generates a file (OutputFile).bat to delete the files, with the files to keep in comment. If (WriteDeleteOnly) = Yes it only writes the delete commands.
The program saves the file information for later use in the (DatabaseFile) file.

=============================================================================================
=============================================================================================
Le tueur de doublons !
Trouve les fichiers en double et les supprime

Fortement inspiré de fast-duplicate-finder (https://github.com/carlbeech/fast-duplicate-finder) de Carl Beech
Avec quelques modifications :
- Recherche des doublons sur différents critères possibles (nom et date de modification par exemple), cela permet de faire une analyse très rapide sans passer par le calcul des MD5
- Ajout des répertoires en preserve_exception (voir explications plus bas)
- Ne marche que sous Windows
- mais marche sous Windows en Français
- nécessite obligatoirement un fichier de configuration
- nécessite obligatoirement un fichier de sauvegarde de la base de données

Pour l'anecdote, je n'ai pas réussi à exécuter correctement le programme source de Carl, du coup je me suis lancé dans mon propre programme ...

---------------------------------------------------------------------------------------------
TODO :
- une meilleure gestion des erreurs
- ajout d'arguments en ligne de commande
- GUI
- ajout de critères : Tags MP3, Scrap Fichiers vidéo à la kodi, fuzzy search

---------------------------------------------------------------------------------------------
Utilisation : 

c:\git\dup-killer>dup_killer.py [-v] -c <config_file>

le fichier <config_file> est un fichier .INI dont le contenu est structuré comme :
---------------------------------------------------------------------------------------------
[InputDirectories]
# repertoires à scanner (1 au minimum)
InputDirectory=C:\git\test\dups     
InputDirectory2=C:\git\test\dups2   

[PreserveDirectories]
# repertoires protégés/à garder (facultatif)
PreserveDirectory=C:\git\test\preserve
PreserveDirectory2=C:\git\test\dups\preserve

[PreserveDirectoriesExceptions]
# répertoires à supprimer dans les répertoires protégés (facultatif)
DeleteDirectory=C:\git\test\preserve\temp
DeleteDirectory2=C:\git\test\dups\preserve\temp

[Params]
# Autres paramètres
DatabaseFile=C:\git\test\cfg\bdd_files.pck
OutputFile=C:\git\test\cfg\output
CalculateMD5=Yes
SameName=Yes
SameSize=Yes
SameDateModif=No
SameMD5=Yes
WriteDeleteOnly=No
---------------------------------------------------------------------------------------------

Le programme scanne les répertoires dans [InputDirectories] et [PreserveDirectories].
Il identifie les fichiers en doublons qui ont les mêmes critères : Nom, Taille, Date de Modification ou/et MD5 (SameName, SameSize, SameDateModif, SameMD5).
Il distingue les fichier à supprimer de ceux à garder (dans [PreserveDirectories] et hors [PreserveDirectoriesExceptions])
Il génère un fichier (OutputFile).bat pour supprimer les fichiers, avec les fichiers à garder en commentaire. Si (WriteDeleteOnly)=Yes il n'écrit que les commandes de suppression.
Le programme sauvegarde les informations sur les fichiers pour une utilisation ultérieure dans le fichier (DatabaseFile).

 

