# Manuel utilisateur — EduPaie

**Application de gestion des paiements scolaires**

---

## 🚀 Lancer l'application

1. Double-cliquer sur **EduPaie.exe** (ou lancer `python main.py` en mode développement)
2. Au premier lancement, créer le compte administrateur avec un identifiant et un mot de passe d'au moins 10 caractères
3. Choisir aussi un mot de passe distinct d'au moins 12 caractères pour les sauvegardes chiffrées
4. Aux lancements suivants, saisir les deux mots de passe dans l'écran de connexion
5. La fenêtre principale s'ouvre après une connexion et une sauvegarde réussies

Une sauvegarde chiffrée est créée automatiquement à chaque lancement réussi. Les
30 plus récentes sont conservées dans `data/backups/`. Le mot de passe dédié est
indispensable pour les ouvrir et ne peut pas être récupéré.

Pour restaurer une sauvegarde, fermez EduPaie puis lancez :

```bash
python restore_backup.py data/backups/nom-de-la-sauvegarde.enc
```

La restauration vérifie le fichier et crée une sauvegarde de sécurité chiffrée de
la base actuelle avant le remplacement.

### Mot de passe administrateur oublié

Le mot de passe de connexion n'est pas récupérable. Pour le remplacer, fermez
EduPaie et lancez PowerShell ou un terminal dans le dossier du projet :

```bash
python reset_password.py
```

Saisissez `REINITIALISER` pour confirmer, puis entrez deux fois un nouveau mot de
passe d'au moins 10 caractères. L'identifiant reste inchangé. Cette opération ne
modifie ni les élèves, ni les paiements, ni le mot de passe de sauvegarde, ni les
reçus PDF. Relancez ensuite EduPaie et connectez-vous avec le même identifiant et
le nouveau mot de passe.

---

## ➕ Enregistrer un nouvel élève

1. Cliquer sur le bouton **➕ Ajouter un élève**
2. Remplir les champs obligatoires (*) :
   - **Nom** (ex : KOUASSI)
   - **Prénom** (ex : Ami)
   - **Date de naissance** (format AAAA-MM-JJ, ex : 2014-03-15)
   - **Année scolaire** (ex : 2026-2027)
   - **Montant total dû** (en F CFA, ex : 150000)
   - **Classe** (choisir parmi 6ème A/B, 5ème A/B, 4ème A/B, 3ème A/B,
     2nd A4/S, 1ère A4/D/C ou Tle A4/D/C)
3. Cliquer sur **Valider**

> 💡 **Astuce :** une fenêtre d'erreur s'affiche si un champ est mal rempli.

---

## ✏ Modifier ou 🗑 supprimer un élève

1. Sélectionner l'élève dans le tableau (clic sur la ligne)
2. Cliquer sur **✏ Modifier** ou **🗑 Supprimer**
3. Pour la suppression : confirmer avec **Oui**

> ⚠️ **Attention :** un élève qui a des paiements ne peut pas être supprimé.

---

## 💰 Enregistrer un paiement

1. Sélectionner l'élève dans le tableau
2. Cliquer sur **💰 Enregistrer un paiement**
3. Saisir :
   - **Montant à payer** (ne doit pas dépasser le solde restant)
   - **Date du paiement** (remplie automatiquement avec la date du jour)
   - **Mode de paiement** : Espèces / Chèque / Virement / Mobile Money
4. Cliquer sur **💰 Enregistrer le paiement**

**Le numéro de reçu est généré automatiquement** (format `REC-2026-000001`).

> ⚠️ **Attention :** le montant ne peut pas dépasser le solde restant dû.

---

## 🖨 Générer un reçu PDF

1. Sélectionner l'élève → cliquer sur **📋 Voir la fiche**
2. Dans l'historique, sélectionner le paiement concerné
3. Cliquer sur **Générer le reçu** pour créer le PDF ou sur **Ouvrir le reçu généré** pour consulter un reçu déjà créé
4. Le PDF s'ouvre avec le lecteur par défaut et reste disponible dans `data/recus/`

**Le reçu contient :**
- Numéro de reçu unique
- Informations de l'élève
- Montant reçu, mode de paiement et solde restant
- Emplacements de signature du caissier et du parent

Le reçu est généré sur une seule page au format compact A6.

---

## 📊 Consulter le tableau de bord

1. Cliquer sur **📊 Tableau de bord**
2. Voir les statistiques globales :
   - 👥 Nombre d'élèves
   - 💰 Total encaissé
   - ⏳ Total restant dû
   - ⚠ Nombre d'élèves non soldés
3. Filtrer par **classe**, **année scolaire** et **situation**
4. Cliquer sur une carte pour afficher les élèves associés : tous les élèves,
   ceux ayant payé, ou ceux ayant encore un solde
5. Utiliser **Actualiser** pour recharger les données
6. Utiliser **Exporter le rapport PDF** ou **Imprimer le rapport** pour produire
   un document correspondant aux filtres actuellement appliqués

Les statistiques tiennent compte de la classe et de l'année sélectionnées; le
filtre de situation agit sur la liste. Le rapport inclut les filtres et les
élèves affichés.

---

## 🔍 Rechercher un élève

- **Par nom/prénom** : taper dans la barre de recherche
- **Par classe** : utiliser le menu déroulant à droite

Les résultats se filtrent automatiquement.

Les classes de l'établissement sont ajoutées automatiquement à l'année scolaire
par défaut (`2026-2027`) au démarrage. Les classes déjà enregistrées et les
inscriptions existantes sont conservées.

Pour créer une classe qui ne figure pas dans la liste, cliquer sur
**Ajouter une classe**, saisir son nom, son niveau et son année scolaire, puis
valider. La classe apparaît ensuite dans le filtre et dans le formulaire
d'inscription des élèves. Un même nom peut être repris pour une autre année,
mais pas deux fois pour la même année.

---

## 🎨 Comprendre les statuts

| Statut | Couleur | Signification |
|---|---|---|
| ✅ **Soldé** | Vert | L'élève a payé la totalité |
| 🟡 **Partiellement payé** | Orange | L'élève a payé une partie |
| 🔴 **Non payé** | Rouge | Aucun paiement enregistré |

---

## 🆘 En cas de problème

- **L'application ne démarre pas** : vérifier que Python 3.10+ est installé
- **Erreur "Base de données introuvable"** : lancer `python init_db.py`
- **Sauvegarde impossible** : vérifier l'espace disque et les droits d'écriture dans `data/`
- **Mot de passe de sauvegarde perdu** : les sauvegardes existantes ne peuvent pas être déchiffrées
- **Mot de passe administrateur oublié** : fermer l'application et suivre la procédure `python reset_password.py` ci-dessus
- **Erreur à l'enregistrement d'un paiement** : vérifier que le montant ne dépasse pas le solde

> La base active et les reçus PDF ne sont pas chiffrés. Protégez l'accès à Windows
> et au dossier `data/`, ou utilisez le chiffrement de disque de Windows.

---

## 📞 Support

Pour toute question, contacter l'administrateur de l'établissement.

---

**Version 1.0 — Octobre 2026**
**Auteur : AKUESON Adoudé Claudia Rovana**