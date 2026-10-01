# Manuel utilisateur — EduPaie

**Application de gestion des paiements scolaires**

---

## 🚀 Lancer l'application

1. Double-cliquer sur **EduPaie.exe** (ou lancer `python main.py` en mode développement)
2. La fenêtre principale s'ouvre avec la liste des élèves

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
   - **Date du paiement** (pré-remplie à aujourd'hui)
   - **Mode de paiement** : Espèces / Chèque / Virement / Mobile Money
4. Cliquer sur **💰 Enregistrer le paiement**

**Le numéro de reçu est généré automatiquement** (format `REC-2026-000001`).

> ⚠️ **Attention :** le montant ne peut pas dépasser le solde restant dû.

---

## 🖨 Générer un reçu PDF

1. Sélectionner l'élève → cliquer sur **📋 Voir la fiche**
2. Dans l'historique, sélectionner le paiement concerné
3. Cliquer sur **🖨 Voir le reçu**
4. Le PDF s'ouvre automatiquement (dans le lecteur PDF par défaut)
5. Le fichier est enregistré dans `data/recus/`

**Le reçu contient :**
- Numéro de reçu unique
- Informations de l'élève
- Détails du paiement
- Situation après paiement (solde, statut)

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
- **Erreur à l'enregistrement d'un paiement** : vérifier que le montant ne dépasse pas le solde

---

## 📞 Support

Pour toute question, contacter l'administrateur de l'établissement.

---

**Version 1.0 — Octobre 2026**
**Auteur : AKUESON Adoudé Claudia Rovana**