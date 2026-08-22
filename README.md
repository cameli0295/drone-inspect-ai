# DroneInspect AI

**URL publique de l'application déployée :** https://drone-inspect-ai-camelia.streamlit.app

DroneInspect AI est une plateforme d'inspection d'ouvrages en béton assistée par intelligence artificielle. Le dépôt contient deux interfaces qui partagent les mêmes modèles Keras et la base MySQL `drone_inspection_ai` :

- l'application métier **Streamlit** sur le port `8501` ;
- l'application minimale et l'API **Flask** sur le port `5000`.

## Prérequis d'installation

- Windows 10/11, Linux ou macOS ;
- **Python 3.12** recommandé (développement validé avec Python 3.12.8) ;
- **MySQL 8.0 ou 9.x** (base validée avec MySQL 9.5.0) ;
- au moins 4 Go de mémoire disponible pour charger les modèles TensorFlow ;
- les modèles présents dans `models/` ;
- Navigateur récent (Chrome, Edge ou Firefox) pour le parcours vérifié.

Les dépendances déclarées dans `requirements.txt` sont :

```text
streamlit
flask
python-dotenv
mysql-connector-python
pandas
pillow
tensorflow
numpy
openpyxl
plotly
reportlab
```

Versions principales utilisées pendant les tests : Streamlit 1.41.1, Flask 3.0.3, TensorFlow 2.20.0, mysql-connector-python 9.5.0, Pandas 2.2.2, NumPy 2.0.2, Pillow 11.1.0, OpenPyXL 3.1.5 et Plotly 6.0.0.

## Étapes d'installation

### 1. Copier ou cloner le projet

```powershell
git clone <URL_DU_DEPOT>
Set-Location Drone_inspection
```

Si le projet est livré sous forme de ZIP, décompresser l'archive puis ouvrir un terminal dans le dossier `Drone_inspection`.

### 2. Créer l'environnement virtuel

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Sous Linux/macOS, l'activation s'effectue avec `source .venv/bin/activate`.

### 3. Importer le dump SQL

Le fichier `dump_drone_inspection_ai_demo.sql` contient la structure et les données anonymisées de la base.

Avec un compte MySQL autorisé à créer une base :

```powershell
mysql -u <COMPTE_ADMIN_LOCAL> -p -e "CREATE DATABASE IF NOT EXISTS drone_inspection_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
Get-Content .\dump_drone_inspection_ai_demo.sql -Raw | mysql -u <COMPTE_ADMIN_LOCAL> -p drone_inspection_ai
```

Sous un terminal prenant en charge la redirection standard :

```bash
mysql -u <COMPTE_ADMIN_LOCAL> -p drone_inspection_ai < dump_drone_inspection_ai_demo.sql
```

Créer ensuite le compte MySQL de revue avec un compte administrateur local :

```sql
CREATE USER IF NOT EXISTS 'demo_reviewer'@'localhost'
  IDENTIFIED BY 'Reviewer_DroneInspect_2026!';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON drone_inspection_ai.* TO 'demo_reviewer'@'localhost';
FLUSH PRIVILEGES;
```

Cette commande ne confère aucun droit `DROP`, `CREATE`, `ALTER`, `INDEX` ou `GRANT OPTION`.

Le dump de livraison a été anonymisé sans modifier la base de développement :

- nom utilisateur remplacé par `Administrateur Démo` ;
- e-mail remplacé par `admin.demo@example.invalid` ;
- noms d'inspecteur remplacés par `Inspecteur Démo` ;
- valeur de `password_hash` remplacée par un hash bcrypt factice et inutilisable comme mot de passe connu.

### 4. Configurer les variables d'environnement

```powershell
Copy-Item .env.example .env
```

Le fichier `.env` est exclu de Git. Pour l'évaluation locale, `.env.example` contient le compte MySQL limité `demo_reviewer`. En dehors de cette démonstration, remplacer immédiatement son mot de passe et ne jamais publier le fichier `.env` réel.

### 5. Lancer Streamlit

```powershell
python -m streamlit run app.py --server.port 8501
```

Ouvrir `http://localhost:8501`. Les menus disponibles incluent les inspections, la classification IA, l'historique, les rapports, le dashboard, l'administration et l'import de référentiel.

### 6. Lancer Flask en parallèle

Dans un second terminal avec le même environnement virtuel :

```powershell
python -m flask_app.run
```

Points d'accès :

- interface Flask : `http://localhost:5000` ;
- contrôle de santé : `http://localhost:5000/health` ;
- import CSV/XLSX/JSON : `http://localhost:5000/imports` ;
- API de prédiction : `POST http://localhost:5000/predict`.

## Identifiants de test

Compte MySQL destiné uniquement à la revue locale :

```text
Utilisateur : demo_reviewer
Mot de passe : Reviewer_DroneInspect_2026!
Hôte autorisé : localhost
Base : drone_inspection_ai
```

Droits accordés exclusivement sur `drone_inspection_ai.*` :

- `SELECT` ;
- `INSERT` ;
- `UPDATE` ;
- `DELETE`.

Le compte ne possède ni `DROP`, ni `CREATE`, ni `ALTER`, ni `INDEX`, ni `GRANT OPTION`, et aucun privilège global autre que `USAGE`.

Ces identifiants sont des identifiants de démonstration livrables. Ils doivent être changés ou supprimés après l'évaluation.

## Identifiants de connexion à la base SQL

```text
Host : localhost
Port : 3306
Base : drone_inspection_ai
Utilisateur : demo_reviewer
Mot de passe : voir la section « Identifiants de test » et .env.example
```

L'application ne doit jamais utiliser ni exposer le compte MySQL `root`. La configuration est chargée depuis `.env` par `shared_config.py`.

## Accès administrateur au back-office

Dans la version locale actuelle, Streamlit ne présente pas encore d'écran d'authentification applicative. Pour accéder au back-office :

1. lancer Streamlit ;
2. ouvrir `http://localhost:8501` ;
3. sélectionner **Administration** dans le menu latéral.

Le premier utilisateur actif ayant le rôle `Administrateur` dans la table `users` est utilisé pour la traçabilité des actions. Le compte MySQL `demo_reviewer` permet les lectures et écritures nécessaires, mais ne constitue pas un compte de connexion visuel au back-office. Avant toute exposition publique, une authentification serveur et un contrôle d'accès par rôle doivent être ajoutés.

## Import du référentiel

La page **Import référentiel** de Streamlit et la page `/imports` de Flask acceptent CSV, XLSX et JSON. Un exemple est fourni avec `sample_inspections_import.csv` et dans `examples/`.

Champs requis : `drone_id`, `inspection_date`, `location`, `infrastructure_type`, `inspector_name`, `weather_conditions`, `status` et `description`.

Chaque ligne est contrôlée avant insertion. Les lignes rejetées et leurs motifs sont consignés dans un rapport JSON.

## Compatibilité navigateur

- **Google Chrome** : testé avec succès ;
- **Microsoft Edge** : testé avec succès ;
- **Mozilla Firefox** : testé avec succès ;
- Safari : non testé.

## Déploiement Streamlit Community Cloud

Dans les paramètres **Secrets** de l'application Streamlit Cloud, renseigner :

```toml
[mysql]
host = "db4free.net"
port = 3306
database = "VOTRE_BASE_DB4FREE"
user = "VOTRE_UTILISATEUR_DB4FREE"
password = "VOTRE_MOT_DE_PASSE_DB4FREE"
charset = "utf8mb4"
use_unicode = true
```

`shared_config.py` utilise en priorité `st.secrets["mysql"]` dans un contexte Streamlit, puis retombe sur `.env` en local. Ne jamais commiter `.streamlit/secrets.toml`.

Pour initialiser une base de démonstration distante sans les données synthétiques du benchmark, utiliser `dump_drone_inspection_ai_demo.sql`.

## Fichiers de livraison importants

```text
app.py                              Application Streamlit
6_Import_Referentiel.py             Page d'import Streamlit
flask_app/                          Application Flask et API
import_referentiel.py               Logique d'import CSV/XLSX/JSON
models/                             Modèles Keras
notebooks/                          Notebooks d'entraînement et d'analyse
dump_drone_inspection_ai_demo.sql   Dump léger sans les 20 000 lignes synthétiques
.env.example                        Configuration de démonstration
shared_config.py                    Chargement sécurisé de la configuration
requirements.txt                    Dépendances Python
README.md                           Instructions d'installation
```

## Limites connues avant mise en production

- le serveur de développement Flask doit être remplacé par un serveur WSGI de production derrière TLS ;
- l'authentification du back-office doit être renforcée ;
- les identifiants de démonstration doivent être remplacés après l'évaluation.
