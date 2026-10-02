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

---

## ➕ Enregistrer un nouvel élève

1. Cliquer sur le bouton **➕ Ajouter un élève**
2. Remplir les champs obligatoires (*) :
   - **Nom** (ex : KOUASSI)
   - **Prénom** (ex : Ami)
   - **Date de naissance** (format AAAA-MM-JJ, ex : 2014-03-15)
   - **Année scolaire** (ex : 2026-2027)
   - **Montant total dû** (en F CFA, ex : 150000)
   - **Classe** (choisir dans la liste)
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
3. Filtrer par statut : **Tous / Soldé / Partiellement payé / Non payé**

---

## 🔍 Rechercher un élève

- **Par nom/prénom** : taper dans la barre de recherche
- **Par classe** : utiliser le menu déroulant à droite

Les résultats se filtrent automatiquement.

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
- **Erreur à l'enregistrement d'un paiement** : vérifier que le montant ne dépasse pas le solde

> La base active et les reçus PDF ne sont pas chiffrés. Protégez l'accès à Windows
> et au dossier `data/`, ou utilisez le chiffrement de disque de Windows.

---

## 📞 Support

Pour toute question, contacter l'administrateur de l'établissement.

---

**Version 1.0 — Octobre 2026**
**Auteur : AKUESON Adoudé Claudia Rovana**