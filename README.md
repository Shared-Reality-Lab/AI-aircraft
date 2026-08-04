# McGill — Éditeur et simulateur de trajectoires d'aéronefs

Projet en deux parties pour concevoir et rejouer des scénarios de trafic aérien sur un aéroport donné :

- **Un éditeur graphique** (PySide6, à la racine du dépôt) pour tracer des trajectoires, définir des conflits entre aéronefs, et exporter le tout au format XML.
- **Un module de simulation** (dossier `simulation/`) qui lit ces scénarios XML et pilote les aéronefs IA en temps réel dans **X-Plane**, via le protocole [XPlaneConnect](https://github.com/nasa/XPlaneConnect) (`xpc`).

## Fonctionnalités

### Éditeur (racine du dépôt)

- **Chargement d'un aéroport réel** à partir de son code OACI (ICAO), lu depuis un fichier `apt.dat` (format X-Plane) : pistes, nœuds et segments de taxiways.
  - Si vous avez le fichier 'apt.dat' en local vous pouvez changer le chemin dans le module Airport.py ligne 26 car le fichier 'apt.dat' inclus au programme ne contient que l'aéroport LFPG.
- **Visualisation interactive de la carte** de l'aéroport (zoom à la molette, déplacement au clic-glisser).
- **Création d'aéronefs et de trajectoires** : ajout de points de passage (waypoints) au clic droit, gestion de la vitesse par segment.
- **Définition de conflits entre aéronefs** :
  - *Intersection* : point de croisement avec un décalage temporel/spatial (offset).
  - *Lead-follow* : un aéronef en suit un autre avec un ralentissement sur une portion du trajet.
- **Sauvegarde / chargement de scénarios** au format XML :
  - `Save` écrase le fichier courant.
  - `Save as` permet d'enregistrer sous un nouveau nom.
  - `Load file` recharge un scénario existant.
- **Confirmation à la fermeture** : une boîte de dialogue propose de sauvegarder (écraser ou enregistrer sous), d'ignorer les modifications, ou d'annuler la fermeture.

### Simulation (`simulation/`)

- **Connexion à X-Plane** via XPlaneConnect pour prendre le contrôle des aéronefs IA (autopilote et trajectoire désactivés côté X-Plane).
- **Lecture du scénario** exporté par l'éditeur (`trajTEST.xml`) : positions de départ, waypoints, vitesses par segment.
- **Suivi de trajectoire** : correction de cap et de vitesse en boucle pour amener chaque aéronef d'un waypoint à l'autre.
- **Gestion des conflits en simulation** :
  - *Intersection* : ajustement de vitesse pour respecter un décalage temporel au point de croisement.
  - *Lead-follow* : un aéronef ralentit et se cale sur la vitesse de l'utilisateur avant de reprendre sa trajectoire.
- **Tracé de courbes de vitesse** (via `matplotlib`) en fin de manœuvre pour analyser le comportement des aéronefs suivis.

## Structure du projet

```
McGill/
├── main.py                   # Point d'entrée de l'éditeur : demande le code OACI, lance l'interface
├── Interface.py               # Fenêtre principale (liste des aéronefs, boutons save/load)
├── Map.py                     # Widget de carte : rendu, interactions souris, lecture XML
├── WriteXML.py                 # Écriture des scénarios au format XML
├── Aircraft.py                 # Modèle de données d'un aéronef (trajectoire, conflits, follow)
├── AircraftItem.py             # Carte UI représentant un aéronef dans la liste
├── Airport.py                  # Lecture du fichier apt.dat et modélisation de l'aéroport
├── CoordConverter.py           # Conversions entre coordonnées géo / UTM / écran
├── Runway.py                    # Modèle de piste
├── TaxiwayNode.py               # Modèle de nœud de taxiway
├── TaxiwaySegment.py            # Modèle de segment de taxiway
├── ScenarioDialog.py            # (optionnel) Boîte de dialogue de choix de scénario prédéfini
├── apt.dat                      # Base de données d'aéroports (format X-Plane)
├── scenarios/                   # Exemples de scénarios XML prêts à charger
├── images/                      # Icônes utilisées pour l'affichage (positions AI / utilisateur)
├── trajTEST.xml                 # Dernier scénario exporté par l'éditeur (lu par la simulation)
└── simulation/                  # Module de simulation X-Plane
    ├── main.py                   # Point d'entrée : connexion X-Plane, lance la boucle de simulation
    ├── Simulation.py              # Lecture du XML, initialisation et boucle principale des aéronefs
    ├── Aircraft.py                # Contrôle d'un aéronef IA (position, cap, vitesse, freins)
    ├── Terrain.py                 # Calcul de l'élévation du terrain pour le positionnement au sol
    ├── CoordConverter.py          # Conversions de coordonnées côté simulation
    ├── xpc/                        # Client XPlaneConnect (communication UDP avec X-Plane)
    ├── moving_forward.py           # Script de test manuel (déplacement de deux aéronefs)
    ├── tests/velocity_regulation.py # Script de test de la régulation de vitesse
    ├── Makefile                    # Lancement de scripts de test en parallèle
    └── *.xml                       # Scénarios et fichiers de test utilisés par la simulation
```

## Prérequis

- Python 3.8+
- Dépendances Python pour l'**éditeur** :
  - [`PySide6`](https://pypi.org/project/PySide6/)
  - [`geopy`](https://pypi.org/project/geopy/)
  - [`utm`](https://pypi.org/project/utm/)
- Dépendances Python supplémentaires pour la **simulation** :
  - [`matplotlib`](https://pypi.org/project/matplotlib/) (tracé des courbes de vitesse)
  - `geopy` (déjà listé ci-dessus, réutilisé pour les calculs de distance)
- Pour la simulation, **X-Plane** doit être installé et lancé avec le plugin [XPlaneConnect](https://github.com/nasa/XPlaneConnect) côté serveur. Le client Python correspondant est déjà inclus dans `simulation/xpc/`.

Installation des dépendances Python :

```bash
pip install PySide6 geopy utm matplotlib
```

## Utilisation

### 1. Créer un scénario avec l'éditeur

1. Lancer l'application :

   ```bash
   python main.py
   ```

2. Entrer le **code OACI** de l'aéroport souhaité (par exemple `CYUL` pour Montréal-Trudeau) lorsque l'invite s'affiche dans le terminal. L'aéroport doit être présent dans `apt.dat`.

3. Dans l'interface :
   - Cliquer sur **`+`** pour créer un nouvel aéronef, puis **clic droit** sur la carte pour ajouter des points de trajectoire.
   - Cliquer sur **`OK`** pour terminer la trajectoire en cours.
   - Utiliser les boutons **`Intersection`** et **`Follow`** sur une carte d'aéronef pour définir des conflits.
   - **`Save`** / **`Save as`** pour exporter le scénario en XML, **`Load file`** pour en recharger un.

Par défaut, `Save` écrit dans `trajTEST.xml` à la racine du dépôt — c'est ce fichier que le module de simulation va lire.

### 2. Rejouer le scénario dans X-Plane

1. Lancer X-Plane avec le plugin XPlaneConnect actif, et placer les aéronefs IA nécessaires sur l'aéroport correspondant au scénario.
2. Depuis le dossier `simulation/`, lancer :

   ```bash
   cd simulation
   python main.py
   ```

3. Le script se connecte à X-Plane, désactive l'autopilote et le suivi de trajectoire natif des aéronefs IA, puis lit `../trajTEST.xml` pour initialiser les positions et trajectoires.
4. La boucle principale déplace ensuite chaque aéronef IA le long de ses waypoints, en gérant les éventuels conflits (intersection ou lead-follow) définis dans l'éditeur.

## Format des fichiers XML générés

Chaque scénario est structuré ainsi :

```xml
<aircraft>
  <ac id="1">
    <waypoints>
      <waypoint lat="..." lon="..." speed="..."/>
      ...
    </waypoints>
    <conflict type="intersection">
      <location lat="..." lon="..."/>
      <offset dist="..."/>
    </conflict>
    <conflict type="lead-follow">
      <location lat="..." lon="..."/>
      <offset dist="..."/>
      <slow-down dist="..." reduc="..."/>
      <end-position lat="..." lon="..."/>
    </conflict>
  </ac>
  ...
</aircraft>
```

## Licence

Distribué sous licence MIT — voir le fichier [LICENSE](LICENSE).
