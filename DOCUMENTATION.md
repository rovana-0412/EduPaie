# Documentation technique — EduPaie

**Application de gestion des paiements scolaires**  
**Auteur :** AKUESON Adoudé Claudia Rovana  
**Date :** 2 octobre 2026  
**Version :** 1.1

---

## 1. Présentation

EduPaie est une application de bureau destinée au suivi des inscriptions et
paiements scolaires. Elle permet de gérer les élèves, d'enregistrer leurs
versements, de consulter leur situation financière et de générer des reçus PDF.

L'application est conçue pour un usage local par un établissement sur un poste
de secrétariat. La base de données est un fichier SQLite; l'application n'est
pas un service réseau multi-utilisateur.

### Fonctionnalités

- Création et modification des dossiers d'élèves.
- Recherche par nom ou prénom et filtrage par classe.
- Enregistrement des paiements en espèces, par chèque, virement ou Mobile Money.
- Calcul automatique du total payé, du solde et du statut de paiement.
- Historique chronologique des paiements par élève.
- Génération et ouverture des reçus PDF au format scolaire A6.
- Tableau de bord avec indicateurs globaux et filtre par statut.
- Connexion administrateur et sauvegardes chiffrées de la base SQLite.
- Restauration contrôlée d'une sauvegarde chiffrée.

---

## 2. Architecture

Le code est séparé en couches afin de distinguer l'interface, les règles métier
et l'accès aux données :

```text
Interface PySide6 (src/ui/)
        ↓
Services métier (src/service.py, src/auth.py, src/backup.py)
        ↓
Repositories SQLite (src/repository.py)
        ↓
Base locale (data/edupaie.db)
```

Les widgets n'exécutent pas directement les requêtes SQL. Ils appellent les
services, qui appliquent les règles métier avant de demander au repository
d'accéder à SQLite.

### Fichiers principaux

| Fichier | Responsabilité |
|---|---|
| `main.py` | Démarrage, connexion à la base, authentification, sauvegarde automatique |
| `src/models.py` | Modèles `Classe`, `Eleve`, `Paiement` et `SoldeEleve` |
| `src/constants.py` | Classes de l'établissement, année par défaut et ordre d'affichage |
| `src/repository.py` | Connexion SQLite et opérations sur les classes, élèves et paiements |
| `src/service.py` | Validation des élèves/paiements, soldes et numérotation des reçus |
| `src/date_utils.py` | Validation stricte des dates ISO |
| `src/auth.py` | Création du compte administrateur et vérification de connexion |
| `src/backup.py` | Configuration du mot de passe dédié, sauvegarde et restauration chiffrées |
| `src/ui/main_window.py` | Liste principale, recherche, filtre et actions sur les élèves |
| `src/ui/eleve_form.py` | Formulaire d'ajout/modification d'élève |
| `src/ui/classe_dialog.py` | Dialogue de création d'une classe personnalisée |
| `src/ui/paiement_dialog.py` | Formulaire d'enregistrement de paiement |
| `src/ui/fiche_eleve.py` | Fiche financière, historique et accès aux reçus |
| `src/ui/tableau_bord.py` | Indicateurs et liste filtrée par statut |
| `src/ui/statut_delegate.py` | Affichage coloré des statuts dans les tableaux |
| `src/ui/style.py` | Style général de l'interface |
| `src/pdf_generator.py` | Génération des reçus A6 dans `data/recus/` |
| `init_db.py` | Création protégée d'une nouvelle base |
| `seed_db.py` | Insertion protégée des données de démonstration |
| `restore_backup.py` | Outil en ligne de commande pour restaurer une sauvegarde |
| `reset_password.py` | Remplacement explicite du mot de passe administrateur oublié |
| `schema.sql` | Schéma initial de la base métier |

---

## 3. Modèle de données

### Tables métier

```text
classes
  id_classe (PK), nom_classe, niveau, annee_scolaire

eleves
  id_eleve (PK), nom, prenom, date_naissance, annee_scolaire,
  montant_total_du, id_classe (FK)

paiements
  id_paiement (PK), date_paiement, montant, mode_paiement,
  numero_recu, id_eleve (FK)
```

Les tables internes `administrateur` et `mot_de_passe_sauvegarde` stockent les
empreintes et paramètres nécessaires à la vérification des mots de passe.
Elles ne contiennent pas les mots de passe en clair.

### Relations et contraintes

- Une classe peut regrouper plusieurs élèves; chaque élève est rattaché à une
  classe.
- Un élève peut avoir plusieurs paiements; chaque paiement concerne un élève.
- `classes(nom_classe, annee_scolaire)` est unique.
- Le montant dû et le montant d'un paiement doivent être supérieurs à zéro.
- Le mode de paiement est limité à `Espèces`, `Chèque`, `Virement` et
  `Mobile Money`.
- Le numéro de reçu est unique.
- Les suppressions d'élèves/classes liés à des données financières sont
  restreintes par les clés étrangères.

Le solde et le statut ne sont pas stockés : ils sont calculés à partir du montant
dû et des paiements associés.

```text
total payé = somme des paiements de l'élève
solde      = montant total dû - total payé
```

Statuts calculés :

- **Soldé** si le solde est nul ou négatif.
- **Partiellement payé** si le total payé est positif et le solde reste dû.
- **Non payé** si aucun versement n'a été enregistré.

---

## 4. Règles métier importantes

### Dates

Les dates de naissance et de paiement sont validées au format ISO strict
`AAAA-MM-JJ` et doivent correspondre à une date réelle du calendrier. Le
formulaire de paiement affiche automatiquement la date du jour et la rend non
modifiable; le service valide aussi les données reçues avant enregistrement.

### Paiements et reçus

- Un paiement doit avoir un montant positif et ne peut pas dépasser le solde
  restant.
- Si aucune date n'est transmise au service, la date du jour est utilisée.
- Les numéros de reçu suivent le format `REC-AAAA-NNNNNN`.
- Le numéro suivant est calculé à partir du plus grand numéro existant de
  l'année, pour éviter un doublon lorsqu'il existe des trous dans la séquence.
- La sélection du numéro et l'insertion du paiement sont réalisées dans une
  transaction SQLite `BEGIN IMMEDIATE`.
- Pour calculer le solde historique sur un reçu, les paiements sont ordonnés
  par date puis par identifiant; les paiements le même jour ont donc un ordre
  déterministe.

### Protection des scripts de données

- `init_db.py` refuse de réinitialiser un fichier de base existant.
- `seed_db.py` refuse d'insérer des données de démonstration si la base contient
  déjà des données scolaires ou une configuration d'application.
- `schema.sql` contient des `DROP TABLE` pour la création initiale et ne doit
  pas être exécuté manuellement sur une base utilisée.

### Classes de l'établissement

La liste standard comprend 16 classes : 6ème A/B, 5ème A/B, 4ème A/B, 3ème A/B,
2nd A4/S, 1ère A4/D/C et Tle A4/D/C. Après connexion réussie, l'application
ajoute par `INSERT OR IGNORE` les classes manquantes pour l'année par défaut
`2026-2027`. L'opération est répétable et ne modifie pas les élèves, paiements
ou classes d'autres années. Les formulaires et le filtre du tableau de bord
affichent les classes dans l'ordre scolaire défini.

---

## 5. Authentification et sauvegardes

### Authentification

Au premier lancement, l'utilisateur crée un compte administrateur. L'identifiant
doit comporter de 3 à 64 caractères; le mot de passe doit en contenir au moins
10. Le mot de passe est dérivé avec PBKDF2-HMAC-SHA256, un sel aléatoire et
600 000 itérations. La comparaison de l'empreinte utilise une comparaison
constante en temps.

### Sauvegarde chiffrée

Un mot de passe de sauvegarde distinct du mot de passe de connexion est demandé.
Il doit comporter au moins 12 caractères. Son empreinte salée est stockée dans
la base; le mot de passe n'est pas enregistré en clair.

Après une connexion réussie, `main.py` crée une copie SQLite cohérente via
l'API `Connection.backup()`, puis chiffre le fichier obtenu avec Fernet
(AES-128-CBC avec authentification HMAC) et une clé dérivée par
PBKDF2-HMAC-SHA256. Les fichiers sont placés sous `data/backups/`; les
30 sauvegardes les plus récentes sont conservées.

Pour restaurer une sauvegarde, fermer l'application puis exécuter :

```powershell
python restore_backup.py data/backups/nom-de-sauvegarde.enc
```

Le programme demande le mot de passe de sauvegarde, déchiffre le fichier,
vérifie l'intégrité SQLite, la présence des tables métier et les clés étrangères.
Si une base existe déjà, une sauvegarde chiffrée de sécurité est créée avant le
remplacement.

### Mot de passe administrateur oublié

Le mot de passe de connexion est conservé sous forme d'empreinte et ne peut pas
être retrouvé. Sur le poste autorisé, fermer EduPaie puis exécuter
`python reset_password.py`. Le script exige la confirmation `REINITIALISER`,
puis demande deux fois un nouveau mot de passe d'au moins 10 caractères. Il
remplace uniquement l'empreinte du compte existant : identifiant, données métier,
mot de passe de sauvegarde et reçus PDF sont conservés.

### Limites de protection

- Le fichier SQLite actif n'est pas chiffré.
- Les reçus PDF dans `data/recus/` ne sont pas chiffrés et ne sont pas inclus
  dans les sauvegardes actuelles, qui portent uniquement sur la base.
- L'écran de connexion ne remplace pas les permissions Windows. Protéger le
  compte utilisateur Windows et le dossier `data/`; envisager le chiffrement du
  disque pour protéger les fichiers locaux.
- Le mot de passe de sauvegarde ne peut pas être récupéré. Sans lui, les
  sauvegardes `.enc` existantes ne peuvent pas être ouvertes.

---

## 6. Interface et reçus

### Fenêtre principale

La liste permet de rechercher les élèves par nom/prénom et de filtrer par classe.
Les colonnes affichent l'identité, la classe, le montant dû, le solde et le
statut coloré. Les actions disponibles sont : ajouter, modifier, supprimer,
ajouter une classe personnalisée, ouvrir la fiche, enregistrer un paiement,
actualiser et afficher le tableau de bord.

Une classe personnalisée comprend un nom, un niveau et une année scolaire. Le
couple nom/année doit être unique; une même classe peut donc être réutilisée lors
d'une autre année scolaire. Après sa création, elle est proposée dans le filtre
principal, le tableau de bord et les formulaires d'élève.

### Tableau de bord

Le tableau de bord affiche le nombre d'élèves, le montant encaissé, le reste à
recouvrer et le nombre d'élèves non soldés. La liste peut être filtrée par
classe, année scolaire et situation. Les cartes interactives appliquent un
filtre approprié aux élèves; les indicateurs sont recalculés selon la classe et
l'année sélectionnées. L'action Actualiser recharge les données depuis la base.
Le rapport PDF ou imprimé reprend les filtres et les élèves actuellement
affichés.

### Fiche d'élève

La fiche réunit les informations de l'élève, sa situation financière et la liste
chronologique de ses paiements. Depuis cette liste, l'utilisateur peut générer
un reçu PDF ou ouvrir le PDF existant du paiement sélectionné.

Le reçu est produit sur une page A6 et comprend le numéro, la date, l'élève, la
classe, l'année scolaire, le mode de paiement, le montant reçu, la situation
après paiement et des emplacements de signature.

### Captures disponibles

![Fenêtre principale](captures/ecran_liste.png)

![Tableau de bord](captures/tableau_de_bord.png)

---

## 7. Installation et lancement

Prérequis : Python 3.10 ou supérieur et `pip`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python init_db.py
python main.py
```

Le jeu de démonstration est facultatif et doit être inséré uniquement dans une
base neuve :

```powershell
python seed_db.py
```

Ne pas exécuter `init_db.py` après avoir commencé à utiliser la base : le script
refusera désormais de toucher à une base existante. Pour recréer des données de
test, utiliser un dossier de démonstration distinct; ne jamais effacer la base
utilisateur pour cette opération.

---

## 8. Tests

Les tests automatisés se trouvent dans `tests/`. Ils couvrent l'authentification,
les sauvegardes/restaurations sur bases temporaires, la protection de
l'initialisation et des données de démonstration, la validation des dates, la
numérotation des reçus et l'historique des paiements.

Lancer les tests avec :

```powershell
python -m unittest discover -s tests -v
```

Les tests utilisent des bases temporaires et ne doivent pas nécessiter
l'ouverture de `data/edupaie.db`.

---

## 9. Limites et évolutions possibles

- **Historique des inscriptions** : un élève possède actuellement une classe et
  une année scolaire dans son dossier; le modèle ne gère pas un historique
  complet d'inscriptions sur plusieurs années.
- **Gestion des classes** : l'interface permet d'ajouter des classes, mais pas
  encore de modifier ou supprimer une classe.
- **Corrections de paiements** : l'interface ne propose pas de modification ou de
  suppression de paiements ni de journal d'audit.
- **Export** : pas d'export CSV/Excel ou de rapports périodiques intégrés.
- **Reçus dans les sauvegardes** : les PDF doivent être sauvegardés séparément.
- **Multi-utilisateur** : SQLite et l'application locale sont destinées à un
  usage sur un seul poste; un partage multi-postes demanderait une architecture
  serveur et une base adaptée.
- **Interface de restauration** : la restauration s'effectue avec un script
  séparé et non depuis une commande de l'interface graphique.

---

## 10. Technologies

| Composant | Technologie |
|---|---|
| Langage | Python |
| Interface | PySide6 / Qt 6 |
| Base de données | SQLite (`sqlite3`) |
| Reçus PDF | ReportLab |
| Chiffrement des sauvegardes | `cryptography` / Fernet |
| Tests | `unittest` |
| Packaging | PyInstaller |
