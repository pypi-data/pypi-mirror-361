import os
import shutil

def organiser_fichiers(repertoire_principal):
    # Vérifie si le répertoire principal existe
    if not os.path.isdir(repertoire_principal):
        print(f"Le répertoire {repertoire_principal} n'existe pas.")
        return

    # Liste tous les fichiers dans le répertoire principal
    fichiers = os.listdir(repertoire_principal)

    for fichier in fichiers:
        # Vérifie si le fichier est un PDF
        if fichier.endswith('.pdf'):
            nom_base = os.path.splitext(fichier)[0]
            nouveau_repertoire = os.path.join(repertoire_principal, nom_base)

            # Crée un nouveau sous-répertoire
            os.makedirs(nouveau_repertoire, exist_ok=True)

            # Copie le fichier PDF dans le nouveau sous-répertoire
            shutil.copy(os.path.join(repertoire_principal, fichier), nouveau_repertoire)

            # Copie les autres fichiers contenant le nom de base dans le nouveau sous-répertoire
            for autre_fichier in fichiers:
                if nom_base in autre_fichier and autre_fichier != fichier:
                    shutil.copy(os.path.join(repertoire_principal, autre_fichier), nouveau_repertoire)

            # Cherche dans le répertoire ../../Lettres/
            repertoire_lettres = os.path.join(repertoire_principal, '../../Lettres')
            if os.path.isdir(repertoire_lettres):
                fichiers_lettres = os.listdir(repertoire_lettres)
                for fichier_lettre in fichiers_lettres:
                    if fichier_lettre.endswith('.pdf') and nom_base in fichier_lettre:
                        shutil.copy(os.path.join(repertoire_lettres, fichier_lettre), nouveau_repertoire)

repertoire = '.'
organiser_fichiers(repertoire)