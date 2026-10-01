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

---

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

# 6. Insérer les données de test (optionnel)
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
4. Sélectionner un paiement → **🖨 Voir le reçu** pour générer le PDF

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

### Schéma (3 tables)

| Table | Colonnes principales |
|---|---|
| `classes` | id_classe, nom_classe, niveau, annee_scolaire |
| `eleves` | id_eleve, nom, prenom, date_naissance, montant_total_du, id_classe |
| `paiements` | id_paiement, date_paiement, montant, mode_paiement, numero_recu, id_eleve |

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
- Gestion des exceptions (aucune erreur non gérée)

---

## 📝 Licence

Projet scolaire — AKUESON Adoudé Claudia Rovana — 2026

---

## 👤 Auteur

**AKUESON Adoudé Claudia Rovana**
- GitHub : [@rovana-0412](https://github.com/rovana-0412)