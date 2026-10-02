# EduPaie — Gestion des paiements scolaires

Application desktop de gestion des paiements scolaires pour un établissement.
Permet d'enregistrer les élèves, leurs paiements, de calculer le solde restant
et de générer des reçus PDF numérotés.

---

## 📋 Fonctionnalités

- **Gestion des élèves** : ajouter, modifier, supprimer, rechercher par nom/classe
- **Enregistrement des paiements** : montant, date, mode (espèces, chèque, virement, Mobile Money)
- **Calcul automatique du solde** : statut dérivé (Soldé / Partiellement payé / Non payé)
- **Historique des paiements** : liste chronologique par élève
- **Génération de reçus PDF** : numéro unique (REC-AAAA-NNNNNN), ré-impression possible
- **Tableau de bord** : statistiques globales et filtre par statut
- **Connexion protégée** : création d'un compte administrateur au premier lancement

---

Au premier lancement, créez le compte administrateur avec un identifiant et un mot
de passe d'au moins 10 caractères. Choisissez aussi un mot de passe **différent**,
d'au moins 12 caractères, dédié aux sauvegardes chiffrées. Il sera demandé à chaque
lancement pour produire la sauvegarde automatique. Les empreintes sont salées; le
mot de passe de sauvegarde n'est pas conservé en clair. Ne le perdez pas : les
sauvegardes ne peuvent pas être déchiffrées sans lui.

## 🛠 Technologies

| Composant | Technologie |
|---|---|
| Langage | Python 3.14 |
| Interface | PySide6 (Qt6) |
| Base de données | SQLite (module `sqlite3`) |
| Génération PDF | ReportLab |
| Packaging | PyInstaller |

---

## 📦 Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/rovana-0412/EduPaie.git
cd EduPaie

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer la base de données
python init_db.py

# 6. Insérer les données de démonstration (optionnel, base vide seulement)
python seed_db.py

# 7. Lancer l'application
python main.py
```

---

## 🚀 Utilisation

### Enregistrer un élève

1. Cliquer sur **➕ Ajouter un élève**
2. Remplir le formulaire (nom, prénom, date, montant dû, classe)
3. Cliquer sur **Valider**

### Enregistrer un paiement

1. Sélectionner un élève dans le tableau
2. Cliquer sur **💰 Enregistrer un paiement**
3. Saisir le montant et le mode de paiement
4. Cliquer sur **Valider**
5. Le numéro de reçu est généré automatiquement

### Voir la fiche d'un élève

1. Sélectionner un élève
2. Cliquer sur **📋 Voir la fiche**
3. L'historique des paiements s'affiche
4. Sélectionner un paiement → **Générer le reçu** pour le créer ou **Ouvrir le reçu généré** pour consulter son PDF existant

### Tableau de bord

1. Cliquer sur **📊 Tableau de bord**
2. Voir les statistiques (élèves, encaissé, restant dû, non soldés)
3. Filtrer par statut (Soldé / Partiel / Non payé)

---

## 📁 Structure du projet

```
EduPaie/
├── data/                    # Base SQLite + reçus PDF
├── src/
│   ├── models.py            # Dataclasses (Classe, Eleve, Paiement, SoldeEleve)
│   ├── repository.py        # Accès SQLite (requêtes SQL)
│   ├── service.py           # Logique métier (calculs, validations)
│   ├── pdf_generator.py     # Génération des reçus PDF
│   └── ui/
│       ├── main_window.py   # Fenêtre principale
│       ├── eleve_form.py    # Formulaire élève
│       ├── paiement_dialog.py # Dialogue paiement
│       ├── fiche_eleve.py   # Fiche élève + historique
│       ├── tableau_bord.py  # Tableau de bord
│       ├── statut_delegate.py # Colorisation des statuts
│       └── style.py         # Feuille de style QSS
├── init_db.py               # Création de la base
├── seed_db.py               # Données de test
├── restore_backup.py        # Restauration d'une sauvegarde chiffrée
├── schema.sql               # Script SQL
├── main.py                  # Point d'entrée
└── requirements.txt         # Dépendances
```

---

## 🧪 Jeu de données de test

La commande `python seed_db.py` insère :

- **3 classes** : 6ème A, 6ème B, 5ème A
- **15 élèves** : 5 par classe
- **12 paiements** : soldés, partiels, non payés

---

## 🗄 Base de données

### Tables métier (3 tables)

| Table | Colonnes principales |
|---|---|
| `classes` | id_classe, nom_classe, niveau, annee_scolaire |
| `eleves` | id_eleve, nom, prenom, date_naissance, montant_total_du, id_classe |
| `paiements` | id_paiement, date_paiement, montant, mode_paiement, numero_recu, id_eleve |

Les tables internes `administrateur` et `mot_de_passe_sauvegarde` contiennent
uniquement les empreintes des mots de passe d'accès et de sauvegarde.

### Contraintes

- FK `id_classe` et `id_eleve` : `NOT NULL`
- `montant` > 0
- `mode_paiement` ∈ {Espèces, Chèque, Virement, Mobile Money}
- `numero_recu` : unique, format `REC-AAAA-NNNNNN`

---

## 🏗 Architecture en couches

```
┌──────────────────────────┐
│   Interface (PySide6)    │  ← Fenêtres, formulaires, tableaux
├──────────────────────────┤
│   Métier (service.py)    │  ← Calcul du solde, validations
├──────────────────────────┤
│   Données (repository.py)│  ← Requêtes SQLite
└──────────────────────────┘
```

**Règle :** un widget ne touche jamais la base directement.

---

## 🔒 Sécurité

- Validation des champs (nom, date, montant)
- Vérification du solde avant paiement
- Confirmation avant suppression
- Sauvegarde SQLite cohérente et chiffrée à chaque connexion réussie; conservation
  des 30 sauvegardes les plus récentes dans `data/backups/`
- Une restauration crée d'abord une sauvegarde chiffrée de la base courante

### Sauvegardes et restauration

Les sauvegardes utilisent un mot de passe dédié, dérivé avec PBKDF2-HMAC-SHA256
et protégé par un chiffrement authentifié. Le mot de passe de sauvegarde ne peut
pas être récupéré ou réinitialisé : sans lui, les fichiers `.enc` sont inutilisables.
Gardez-le séparément de l'ordinateur et fermez EduPaie avant une restauration.

Pour restaurer une sauvegarde :

```bash
python restore_backup.py data/backups/edupaie-AAAAmmjjTHHMMSSffffffZ.enc
```

Le programme demande le mot de passe dédié. Il vérifie l'intégrité SQLite et les
relations avant le remplacement; la base existante est préalablement sauvegardée
de façon chiffrée. Ne supprimez pas cette sauvegarde de sécurité avant d'avoir
vérifié les données restaurées.

**Limite importante :** la base SQLite active et les reçus PDF restent des fichiers
locaux non chiffrés. L'écran de connexion ne remplace pas la protection du compte
Windows et des permissions du dossier `data/`. Utilisez un compte Windows protégé
et un disque chiffré pour protéger aussi les fichiers actifs.

### Protection contre l'effacement accidentel

- `python init_db.py` refuse de modifier une base déjà présente.
- `python seed_db.py` refuse d'insérer le jeu de démonstration si des données
  scolaires sont déjà présentes.
- N'exécutez pas manuellement `schema.sql` sur votre base : ce fichier contient
  des instructions de suppression de tables et sert uniquement à créer une base
  neuve via `init_db.py`.

---

## 📝 Licence

Projet scolaire — AKUESON Adoudé Claudia Rovana — 2026

---

## 👤 Auteur

**AKUESON Adoudé Claudia Rovana**
- GitHub : [@rovana-0412](https://github.com/rovana-0412)