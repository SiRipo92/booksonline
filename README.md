# Projet 2: Analyse de Marché avec Python

## Description

Ce projet vise à développer une application Python qui automatise l'extraction, la transformation et le chargement (ETL) de données depuis le site [Books To Scrape](http://books.toscrape.com/). Le but est de récupérer des informations produits, de les transformer en données exploitables et de les enregistrer dans des fichiers CSV. En parallèle, une version beta est mise en place pour suivre les prix des livres au moment de l'exécution.

## Objectifs d'Apprentissage

- **Programmation avec Python :** Automatiser la collecte de données depuis un site web.
- **Configuration d'un environnement de travail :** Mise en place d’un environnement virtuel et gestion des dépendances.
- **Utilisation de Git et GitHub :** Suivi des versions avec des commits réguliers et messages descriptifs.
- **Développement d'une pipeline ETL :** Extraction, transformation et chargement des données dans des CSV.

## Mission Principale

Développer un scraper capable de :
- Extraire les informations produits depuis le site Books To Scrape.
- Transformer ces données en fichiers CSV.
- Télécharger et enregistrer les images associées aux produits.
- Mettre en place une version beta du système de surveillance des prix.

## Phases du Projet

### Phase 1 : Extraction d'une Page Produit

- **Objectif :**  
  Choisir une page produit sur Books To Scrape et extraire les informations suivantes :
  - `product_page_url`
  - `universal_product_code (upc)`
  - `title`
  - `price_including_tax`
  - `price_excluding_tax`
  - `number_available`
  - `product_description`
  - `category`
  - `review_rating`
  - `image_url`
- **Livrable :**  
  Un fichier CSV avec ces informations en en-têtes de colonnes.

### Phase 2 : Extraction des Données d'une Catégorie

- **Objectif :**  
  Choisir une catégorie sur Books To Scrape et extraire l'URL de la page produit pour chaque livre de la catégorie.  
  Combiner ces URL avec le script de la Phase 1 pour extraire les informations de tous les livres de la catégorie.
- **Points Importants :**  
  - Gestion de la pagination : Certaines catégories contiennent plus de 20 livres répartis sur plusieurs pages.
- **Livrable :**  
  Un fichier CSV unique regroupant les données de tous les livres d'une catégorie.

### Phase 3 : Extraction des Données de Toutes les Catégories

- **Objectif :**  
  Étendre le script pour :
  - Extraire toutes les catégories disponibles sur le site.
  - Pour chaque catégorie, extraire les informations produits de tous les livres.
- **Livrable :**  
  Un fichier CSV distinct pour chaque catégorie de livres.

### Phase 4 : Téléchargement et Enregistrement des Images

- **Objectif :**  
  Prolonger le travail des phases précédentes pour :
  - Télécharger l'image associée à chaque page produit visitée.
  - Enregistrer ces images dans un dossier dédié.
- **Livrable :**  
  Un dossier contenant toutes les images téléchargées.

## Installation et Configuration

### Prérequis

- **Python 3.12** (vérifiez avec `python3 --version`)
- **Git** pour le contrôle de version

### Installation des Dépendances

1. **Créez un environnement virtuel** (recommandé) :
   ```bash
   python3 -m venv env
   ```
2. **Activez l'environnement virtuel**
   - Sur Windows
   ```
   .\env\Scripts\activate
   ```
   - Sur MacOs
   ```
   source env/bin/activate
3. **Installez les dépendances** depuis <code>requirements.txt</code>
```
pip install -r requirements.txt
```
    
*Note - ceci n'est pas inclus dans ce repository*

## Utilisation
- Exécution du script:
  ```
  python3 main.py
  ```
- Mise-à-jour du Repository
  <p>J'éffectuerai des commits réguliers avec des messages clairs décrivant vos modifications.</p>

### Remarques
- **Surveillance en Temps Réel:** Ce projet ne réalise pas une surveillance continue des prix, mais un relevé des prix au moment de l'exécution.
- **Fichiers à Exclure:** Les fichiers générés (CSV, images, dossier de l'environnement virtuel dans le .gitignore)
- **Documentation:** Des commentaires dans le code et ce README fournissent une vue d'ensemble pour faciliter la compréhension et la maintenance du projet.

## Author
Sierra Ripoche - Junior web developer

## License

Ce projet est licencié sous la Licence Apache, Version 2.0.  
Voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.