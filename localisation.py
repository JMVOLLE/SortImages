""" Language localisation resoure file for SortImage """
__author__ = "Jean-Marc Volle"
__copyright__ = "Copyright 2016 Jean-Marc Volle"
__license__ = "Apache-2.0"


# string resource constant
_T = {
    'SRC_bt': {'en': 'source folder', 'fr': 'source'},
    'SRC_val': {'en': 'source folder', 'fr': 'répertoire source'},
    'DST_bt': {'en': 'destination folder', 'fr': 'destination'},
    'DST_val': {'en': 'destination folder', 'fr': 'répertoire de destination'},
    'STATUS_txt': {'en': 'Waiting for inputs', 'fr': 'En attente de saisie utilisateur'},
    'ACTION_rb_cp': {'en': 'Copy images', 'fr': 'Copier les images'},
    'ACTION_rb_mv': {'en': 'Move images', 'fr': 'Déplacer les images'},
    'ACTION_val': {'en': 'Copy', 'fr': 'Copier'},
    'COPYMOVE_bt_cp': {'en': 'COPY', 'fr': 'COPIER'},
    'COPYMOVE_bt_mv': {'en': 'MOVE', 'fr': 'DEPLACER'},
    'SRC_cb_dlg': {'en': 'Please select Images source folder', 'fr': "Choisissez le répertoire source s'il vous plait"},
    'SRC_cb_log': {'en': 'source folder', 'fr': 'répertoire source'},
    'DST_cb_dlg': {'en': 'Please select Images destination folder',
                   'fr': "Choisissez le répertoire de destination s'il vous plait"},
    'DST_cb_log': {'en': 'destination folder', 'fr': 'répertoire de destination'},
    'missing_src': {'en': 'Missing source', 'fr': 'Répertoire source manquant'},
    'missing_dst': {'en': 'Missing destination', 'fr': 'Répertoire destination manquant'},

    'log1': {'en': 'images found\n', 'fr': 'images trouvés\n'},
    'log2': {'en': 'destination folders(s) to create\n', 'fr': 'repertoires destination à créer\n'},
    'log3': {'en': 'created', 'fr': 'créé'},
    'log4': {'en': 'already exists', 'fr': 'existe déja'},
    'log5': {'en': 'moving:', 'fr': 'deplacement:'},
    'log6': {'en': 'copying:', 'fr': 'copie:'},
    'log7': {'en': 'skipped: already exists in', 'fr': 'sauté, existe déja dans'},
    'log8': {'en': 'images moved', 'fr': 'images déplacées'},
    'log9': {'en': 'images copied', 'fr': 'images copiées'},
    'log10': {'en': 'images skipped', 'fr': 'images sautées'},

    'status1': {'en': 'analyzing source folder', 'fr': 'analyze du répertoire source'},
    'status2': {'en': 'Creating destination folder(s)', 'fr': 'création des repertoires de destination'},
    'status3': {'en': 'Moving images', 'fr': 'Déplacement des images'},
    'status4': {'en': 'Copying files', 'fr': 'Recopie des images'},
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


