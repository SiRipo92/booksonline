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

## Structure du Projet
```text
booksonline/
├── main.py                       # Point d'entrée du projet
├── requirements.txt              # Dépendances Python à installer
├── assets/                       # Contient les fichiers générés
│   ├── csv/                      # CSV exporté contenant les données livres
│   │   └── book_data.csv
│   └── images/                   # Images téléchargées pour chaque livre
├── utils/                        # Package utilitaire contenant les fonctions du scraper
│   ├── __init__.py
│   ├── book_scraper.py          # Scrape les infos de chaque livre, écrit le CSV, supprime les doublons
│   └── category_scraper.py      # Scrape les catégories et les URL de chaque livre
```
### Comment les fichiers fonctionnent ensemble

#### 🔁 `main.py`
- Coordonne tout le processus ETL.
- Appelle les fonctions des modules `utils/` dans l'ordre logique :
  1. `generate_categories_list()` → récupère les catégories du site.
  2. `scrape_category()` → récupère toutes les URLs de livres par catégorie.
  3. `scrape_book()` → récupère les données de chaque livre (appel depuis `book_scraper.py`).
  4. `write_csv()` → écrit les données nettoyées dans un fichier CSV en supprimant les doublons.
  5. `download_book_images_from_csv()` → télécharge les images selon les URL valides dans le CSV.

#### 🧠 `book_scraper.py`
- Fonction principale : `scrape_book(url)` :
  - Isole les données pertinentes (titre, prix, stock, etc.).
  - Nettoie et structure les résultats dans un dictionnaire Python.
- `write_csv(book_info_list, file_path)` :
  - Supprime les doublons à partir des `UPC`.
  - N'écrit que les nouvelles entrées valides.
- `remove_csv_duplicate_rows(file_path)` :
  - Supprime toute répétition ou ligne de type "header accidentel".

#### 📚 `category_scraper.py`
- `generate_categories_list(base_url)` :
  - I/O: URL du site en entrée, dictionnaire `{nom_catégorie: url}` en sortie.
- `scrape_category(category_url)` :
  - Récupère les pages d'une catégorie en gérant la pagination.
  - En sortie :
    - le nombre total de livres,
    - le nombre total de pages,
    - une liste d’URL de chaque livre.
- `extract_book_urls(page_url)` :
  - Récupère toutes les URL de livres listés dans une page de catégorie.

### Avantages de l'organisation modulaire
- **Lisibilité améliorée** : chaque fichier a une mission claire (extraction, transformation, chargement).
- **Maintenance facilitée** : on peut modifier une fonction sans impacter le reste du système.
- **Réutilisabilité** : fonctions comme `write_csv()` ou `scrape_book()` peuvent être appelées ailleurs.
- **Séparation des responsabilités** : évite un fichier monolithique.


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

### Phase 1 : Extraction d'une Page Produit
- Extraire les données détaillées d'un livre donné.
- Générer un dictionnaire des infos du livre.

### Phase 2 : Extraction d'une Catégorie
- Scraper toutes les pages d'une catégorie et leurs produits.
- Gérer la pagination.

### Phase 3 : Extraction Globale
- Automatiser le scraping de toutes les catégories du site.
- Agréger les données dans un CSV.

### Phase 4 : Téléchargement des Images
- Identifier et télécharger toutes les images depuis les URL extraites.
- Vérifier qu’elles respectent les extensions autorisées (`.jpg`, `.jpeg`, `.png`, `.svg`, `.gif`, `.webp`).
- Réessayer les téléchargements échoués avec un `timeout` et `retry`.

## Installation et Configuration

### Prérequis

- **Python 3.12**
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

Exécuter le projet avec :
```bash
python3 main.py
```

Ce script :
- scrape toutes les catégories,
- télécharge toutes les informations produit,
- nettoie les doublons,
- écrit le CSV,
- télécharge les images si elles sont valides.

### Remarques
- **Surveillance en Temps Réel:** Ce projet ne réalise pas une surveillance continue des prix, mais un relevé des prix au moment de l'exécution.
- **Fichiers à Exclure:** Les fichiers générés (CSV, images, dossier de l'environnement virtuel dans le .gitignore)
- **Documentation:** Des commentaires dans le code et ce README fournissent une vue d'ensemble pour faciliter la compréhension et la maintenance du projet.

## Author
Sierra Ripoche - Junior web developer

## License

Ce projet est licencié sous la Licence Apache, Version 2.0.  
Voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.