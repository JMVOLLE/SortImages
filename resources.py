""" Language localisation resoure file for SortImage """
__author__ = "Jean-Marc Volle"
__copyright__ = "Copyright 2016 Jean-Marc Volle"
__license__ = "Apache-2.0"

# string resource constant
_T = {
    'uiSourceButton': {'en': 'folder', 'fr': 'répertoire'},
    'uiSourceFrame': {'en': 'Source', 'fr': 'Source'},
    'uiDestinationFrame': {'en': 'Destination', 'fr': 'Destination'},
    'uiSourceValue': {'en': 'source folder', 'fr': 'répertoire source'},
    'uiDestinationButton': {'en': 'folder', 'fr': 'répertoire'},
    'uiDestinationValue': {'en': 'destination folder', 'fr': 'répertoire de destination'},
    'uiStatusText': {'en': 'Waiting for inputs', 'fr': 'En attente de saisie utilisateur'},
    'ACTION_rb_cp': {'en': 'Copy', 'fr': 'Copier'},
    'ACTION_rb_mv': {'en': 'Move', 'fr': 'Déplacer'},
    'ACTION_val': {'en': 'Copy', 'fr': 'Copier'},
    'uiProcessButton': {'en': 'go', 'fr': 'executer'},
    'COPYMOVE_bt_mv': {'en': 'MOVE', 'fr': 'DEPLACER'},
    'ANALYSE_bt': {'en': 'ANALYSE', 'fr': 'ANALYSER'},
    'SRC_cb_dlg': {'en': 'Please select Images source folder', 'fr': "Choisissez le répertoire source s'il vous plait"},
    'SRC_cb_log': {'en': 'source folder', 'fr': 'répertoire source'},
    'DST_cb_dlg': {'en': 'Please select Images destination folder',
                   'fr': "Choisissez le répertoire de destination s'il vous plait"},
    'DST_cb_log': {'en': 'destination folder', 'fr': 'répertoire de destination'},
    'missing_src': {'en': 'Missing source', 'fr': 'Répertoire source manquant'},
    'missing_dst': {'en': 'Missing destination', 'fr': 'Répertoire destination manquant'},

    'log1': {'en': 'images/video found\n', 'fr': 'images/video trouvées\n'},
    'log2': {'en': 'creation date found\n', 'fr': 'dates de création trouvées\n'},
    'log3': {'en': 'created', 'fr': 'créé'},
    'log4': {'en': 'already exists', 'fr': 'existe déja'},
    'log5': {'en': 'moving:', 'fr': 'deplacement:'},
    'log6': {'en': 'copying:', 'fr': 'copie:'},
    'log7': {'en': 'skipped: already exists in', 'fr': 'sauté, existe déja dans'},
    'log8': {'en': 'images moved', 'fr': 'images déplacées'},
    'log9': {'en': 'images copied', 'fr': 'images copiées'},
    'log10': {'en': 'images skipped', 'fr': 'images sautées'},
    'log11': {'en': 'not selected', 'fr': 'non selectionné'},
    'status1': {'en': 'analyzing source folder', 'fr': 'analyze du répertoire source'},
    'status2': {'en': 'Creating destination folder(s)', 'fr': 'création des repertoires de destination'},
    'status3': {'en': 'Coping/Moving images', 'fr': 'Copie/Déplacement des images'},
    'status4': {'en': 'Copying files', 'fr': 'Recopie des images'},
    'file': {'en': 'File', 'fr': 'Fichier'},
    'quit': {'en': 'Quit', 'fr': 'Quitter'},
    'about': {'en': 'About', 'fr': 'A propos'},
    'help': {'en': 'Help', 'fr': 'Aide'},

    '': {'en': '', 'fr': ''},
}


class R:
    @staticmethod
    def T(lang):
        if lang != 'en' and lang != 'fr':
            raise NotImplementedError
        translations = dict()
        for entry in _T.keys():
            translations[entry] = _T[entry][lang]
        return translations


