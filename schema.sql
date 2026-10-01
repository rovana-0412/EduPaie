-- =====================================================================
-- EduPaie — Script de création de la base de données SQLite
-- Auteur : AKUESON Adoudé Claudia Rovana
-- Date : 01/10/2026
-- =====================================================================

-- Active les clés étrangères (désactivées par défaut dans SQLite)
PRAGMA foreign_keys = ON;

-- Supprime les tables si elles existent (pour repartir de zéro)
DROP TABLE IF EXISTS paiements;
DROP TABLE IF EXISTS eleves;
DROP TABLE IF EXISTS classes;

-- =====================================================================
-- Table CLASSES
-- =====================================================================
CREATE TABLE classes (
    id_classe       INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_classe      TEXT    NOT NULL,
    niveau          TEXT    NOT NULL,
    annee_scolaire  TEXT    NOT NULL,
    UNIQUE (nom_classe, annee_scolaire)
);

-- =====================================================================
-- Table ELEVES
-- =====================================================================
CREATE TABLE eleves (
    id_eleve           INTEGER PRIMARY KEY AUTOINCREMENT,
    nom                TEXT    NOT NULL,
    prenom             TEXT    NOT NULL,
    date_naissance     TEXT    NOT NULL,
    annee_scolaire     TEXT    NOT NULL,
    montant_total_du   REAL    NOT NULL CHECK (montant_total_du > 0),
    id_classe          INTEGER NOT NULL,
    FOREIGN KEY (id_classe) REFERENCES classes(id_classe) ON DELETE RESTRICT
);

CREATE INDEX idx_eleves_nom ON eleves(nom);
CREATE INDEX idx_eleves_classe ON eleves(id_classe);

-- =====================================================================
-- Table PAIEMENTS
-- =====================================================================
CREATE TABLE paiements (
    id_paiement    INTEGER PRIMARY KEY AUTOINCREMENT,
    date_paiement  TEXT    NOT NULL,
    montant        REAL    NOT NULL CHECK (montant > 0),
    mode_paiement  TEXT    NOT NULL CHECK (mode_paiement IN (
                       'Espèces', 'Chèque', 'Virement', 'Mobile Money'
                   )),
    numero_recu    TEXT    NOT NULL UNIQUE,
    id_eleve       INTEGER NOT NULL,
    FOREIGN KEY (id_eleve) REFERENCES eleves(id_eleve) ON DELETE RESTRICT
);

CREATE INDEX idx_paiements_eleve ON paiements(id_eleve);
CREATE INDEX idx_paiements_date ON paiements(date_paiement);

-- =====================================================================
-- Fin du script
-- =====================================================================