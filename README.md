# McGill — Éditeur et simulateur de trajectoires d'aéronefs

Projet en deux parties pour concevoir et rejouer des scénarios de trafic aérien sur un aéroport donné :

- **Un éditeur graphique** (`interface/`, PySide6) pour tracer des trajectoires, définir des conflits entre aéronefs, et exporter le tout au format XML.
- **Un module de simulation** (`simulation/`) qui lit ces scénarios XML et pilote les aéronefs IA en temps réel dans **X-Plane**, via le protocole [XPlaneConnect](https://github.com/nasa/XPlaneConnect) (`xpc`).

## Structure du projet

```
McGill/
├── data/
│   └── apt.dat                 # Base de données d'aéroports (format X-Plane)
├── interface/                   # Éditeur graphique
│   ├── main.py                   # Point d'entrée : demande le code OACI, lance l'interface
│   ├── Interface.py               # Fenêtre principale (liste des aéronefs, boutons OK/save/load)
│   ├── Map.py                     # Widget de carte : rendu, interactions souris, lecture XML
│   ├── WriteXML.py                 # Écriture des scénarios au format XML
│   ├── Aircraft.py                 # Modèle de données d'un aéronef (trajectoire, conflits, follow)
│   ├── AircraftItem.py             # Carte UI représentant un aéronef dans la liste de droite
│   ├── Airport.py                  # Lecture du fichier apt.dat et modélisation de l'aéroport
│   ├── CoordConverter.py           # Conversions entre coordonnées géo / UTM / écran
│   ├── Runway.py                    # Modèle de piste
│   ├── TaxiwayNode.py               # Modèle de nœud de taxiway
│   ├── TaxiwaySegment.py            # Modèle de segment de taxiway
│   ├── scenarios/                   # Exemples de scénarios XML prêts à charger
│   ├── images/                      # Icônes utilisées pour l'affichage (positions AI / utilisateur)
└── simulation/                  # Module de simulation X-Plane
    ├── main.py                   # Point d'entrée : connexion X-Plane, lance la boucle de simulation
    ├── Simulation.py              # Lecture du XML, initialisation et boucle principale des aéronefs
    ├── Aircraft.py                # Contrôle d'un aéronef IA (position, cap, vitesse, freins)
    ├── Terrain.py                 # Calcul de l'élévation du terrain pour le positionnement au sol
    ├── CoordConverter.py          # Conversions de coordonnées côté simulation
    ├── xpc/                        # Client XPlaneConnect (communication UDP avec X-Plane)
    └── *.xml                       # Scénarios et fichiers de test utilisés par la simulation
```

> ⚠️ **Attention au chemin de `apt.dat`** : `Airport.py` (ligne 26) lit le fichier avec le chemin relatif `"apt.dat"`, alors que le fichier fourni dans le dépôt se trouve maintenant dans `data/apt.dat`. Deux options :
> - copier/déplacer `data/apt.dat` dans `interface/` avant de lancer le programme, **ou**
> - modifier la ligne `pathToAptData = r"apt.dat"` dans `Airport.py` pour pointer vers `data/apt.dat` (ou le chemin absolu de votre fichier local, si vous utilisez une base `apt.dat` plus complète — celle fournie ne contient que l'aéroport LFPG).

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

## Utilisation de l'éditeur (`interface/`)

### Lancement

```bash
cd interface
python main.py
```

Le terminal demande le **code OACI** de l'aéroport (par exemple `CYUL` pour Montréal-Trudeau, ou `LFPG` si vous utilisez le fichier `apt.dat` fourni par défaut). L'aéroport doit être présent dans le fichier `apt.dat` utilisé. La fenêtre principale s'ouvre ensuite en plein écran, avec la carte à gauche et la liste des aéronefs à droite.

### Se déplacer sur la carte

- **Molette** : zoomer / dézoomer, centré sur la position du curseur.
- **Clic gauche + glisser** : déplacer la vue.

### Créer un aéronef et sa trajectoire

1. Cliquer sur **`+`** dans le panneau de droite : un nouvel aéronef est créé (numéroté automatiquement) et le programme se met en attente de points de trajectoire.
2. **Clic droit** sur la carte, à chaque endroit où vous voulez ajouter un point de passage (waypoint). Un tracé relie les points au fur et à mesure.
3. Cliquer sur **`OK`** (le bouton devient jaune tant qu'une trajectoire est en cours de saisie) pour terminer la trajectoire. L'aéronef est alors ajouté à la liste de droite, sous forme d'une carte affichant :
   - son nom (`Aircraft N`),
   - les boutons `Delete`, `Intersection`, `Follow`,
   - un champ **`Speed`** par segment de trajectoire (en nœuds), pré-rempli à `10`.

Vous pouvez répéter l'opération avec **`+`** pour ajouter d'autres aéronefs.

### Définir des conflits entre aéronefs

Deux types de conflits sont disponibles, à créer depuis la carte de l'aéronef concerné dans la liste de droite :

- **`Intersection`** : marque un point où l'aéronef traverse la trajectoire d'un autre, avec un décalage (offset) en mètres.
  1. Cliquer sur **`Intersection`** sur la carte de l'aéronef.
  2. **Clic droit** sur la carte, à l'endroit du point d'intersection.
  3. Un petit champ de saisie apparaît : entrer l'**offset en mètres** puis valider avec **Entrée**.

- **`Follow`** (lead-follow) : l'aéronef suit un autre aéronef en ralentissant sur une portion de trajectoire.
  1. Cliquer sur **`Follow`** sur la carte de l'aéronef.
  2. **Clic droit** sur la carte pour placer le **point de début** du suivi, entrer l'offset (mètres) et valider avec **Entrée**.
  3. Le programme attend ensuite le **point de fin** du suivi : **clic droit** à nouveau, puis entrer cette fois la **réduction de vitesse** (en nœuds) et valider.

Chaque conflit posé apparaît sur la carte sous forme d'un point rouge, à la position choisie.

### Consulter les conflits d'un aéronef

En cliquant sur la carte d'un aéronef dans la liste de droite, une section **`Conflicts:`** s'affiche sous les champs de vitesse, listant tous les conflits assignés à cet aéronef, par exemple :

```
Conflicts:
Conflict 1 : intersection | Offset : 50m
Conflict 2 : lead-follow | Offset : 0m | Reduced Speed : -5kt
```

Cette liste se met à jour automatiquement dès qu'un nouveau conflit est ajouté (pas besoin de recliquer sur l'aéronef), et reste consultable en re-cliquant sur l'aéronef même après avoir validé sa trajectoire avec `OK`.

### Supprimer un aéronef

Le bouton **`Delete`** sur la carte d'un aéronef le retire de la liste et de la simulation.

### Sauvegarder / charger un scénario

- **`Save`** : écrase le fichier XML actuellement chargé (par défaut `trajTEST.xml`, à la racine de `interface/` — c'est ce fichier que le module de simulation va lire).
- **`Save as`** : enregistre le scénario sous un nouveau nom.
- **`Load file`** : charge un scénario XML existant (par exemple ceux du dossier `scenarios/`) ; la liste des aéronefs et leurs conflits sont reconstruits à partir du fichier.

### Fermeture

À la fermeture de la fenêtre, une boîte de dialogue propose :
- **Save** : sauvegarder par-dessus le fichier courant puis quitter,
- **Save as** : choisir un nouveau nom puis quitter,
- **Discard** : quitter sans sauvegarder,
- **Cancel** : annuler la fermeture.

## Rejouer le scénario dans X-Plane

1. Lancer X-Plane avec le plugin XPlaneConnect actif, et placer les aéronefs IA nécessaires sur l'aéroport correspondant au scénario.
2. Depuis le dossier `simulation/`, lancer :

   ```bash
   cd simulation
   python main.py
   ```

3. Le script se connecte à X-Plane, désactive l'autopilote et le suivi de trajectoire natif des aéronefs IA, puis demande de charger le scénario XML à lire pour initialiser les positions et trajectoires (Attention : il se peut que si vous utilisez un "petit" avion de type Cessna, celui-ci se crashe au moment où l'avion utilisateur est placé au début de sa trajectoire. Vous pouvez alors soit choisir un autre avion, soit modifier le code dans simulation/Simulation.py dans l'initialisation pour que l'avion utilisateur ne soit pas déplacé au début de sa trajectoire au lancement du programme.).
4. La boucle principale déplace ensuite chaque aéronef IA le long de ses waypoints, en gérant les éventuels conflits (intersection ou lead-follow) définis dans l'éditeur :
   - *Intersection* : ajustement de vitesse pour respecter le décalage temporel/spatial au point de croisement.
   - *Lead-follow* : l'aéronef ralentit et se cale sur la vitesse de l'utilisateur avant de reprendre sa trajectoire normale.
5. À la fin d'une manœuvre de suivi, une courbe de vitesse (`matplotlib`) est tracée pour analyser le comportement de l'aéronef suivi.

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
