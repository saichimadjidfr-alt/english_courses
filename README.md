# English Course RAG

Génère automatiquement, chaque jour à 9h, un **cours d'anglais de 30 minutes avec exercice et corrigé** à partir de tes propres livres, et le publie dans **Notion**.

Le projet utilise un **RAG** (*Retrieval-Augmented Generation*) : les passages pertinents de tes livres sont retrouvés dans une base vectorielle, puis un LLM (Groq) rédige le cours à partir de ces extraits.

## Fonctionnement

```
Indexation (manuelle, en local)
data/books/ → loader → cleaner → chunker → embeddings → ChromaDB

Génération (automatique, GitHub Actions)
curriculum.yaml → thème suivant → retriever → LLM Groq → Markdown → page Notion
```

Chaque cours contient : objectifs, warm-up (5 min), explication (10 min), exemples guidés (5 min), exercice (7 min) avec corrigé dans un toggle, récap (3 min) et les sources (livre + page).

## Technologies

| Rôle | Outil |
|---|---|
| Langage | Python 3.11 |
| Lecture des livres | `pypdf`, `ebooklib`, `beautifulsoup4` |
| Base vectorielle | ChromaDB (local) |
| Embeddings | `all-MiniLM-L6-v2` (défaut de ChromaDB) |
| LLM | Groq, `openai/gpt-oss-20b` |
| Validation | Pydantic |
| Publication | API Notion (`requests`) |
| Automatisation | GitHub Actions |

## Structure

```
english_course_rag/
├── .github/workflows/daily_course.yml   # cron quotidien
├── data/
│   ├── books/            # tes livres (non versionnés)
│   ├── vectorstore/      # base ChromaDB
│   ├── state/progress.json
│   └── curriculum.yaml   # thèmes à traiter, dans l'ordre
├── src/
│   ├── ingestion/        # loader.py, cleaner.py
│   ├── chunking/         # chunker.py
│   ├── vectordb/         # vector_store.py
│   ├── retrieval/        # retriever.py
│   ├── llm/              # llm_client.py
│   ├── prompts/          # lesson_prompt.py
│   ├── course/           # schemas.py, lesson_generator.py
│   └── notion/           # notion_client.py, formatter.py, publisher.py
├── scripts/              # outils manuels (index_books.py, test_*.py)
├── config.yaml
├── main.py               # point d'entrée
└── requirements.txt
```

## Installation

### 1. Cloner et installer

```bash
git clone https://github.com/TON_PSEUDO/english_course_rag.git
cd english_course_rag
python -m venv .venv
```

Activer l'environnement :

```bash
# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 2. Créer le fichier `.env`

```
GROQ_API_KEY=ta_cle_groq
NOTION_TOKEN=ton_token_notion
NOTION_DATABASE_ID=id_de_ta_base
```

- Clé Groq : https://console.groq.com/keys
- Intégration Notion : https://www.notion.so/my-integrations

### 3. Préparer Notion

Crée une base **en pleine page** avec ces propriétés :

| Propriété | Type |
|---|---|
| Name (ou Nom) | Titre |
| Niveau | Select |
| Thème | Texte |
| Date | Date |
| Statut | Select |

Puis partage la base avec ton intégration : `⋯` → **Connections**. L'ID de la base correspond aux 32 caractères avant `?v=` dans son URL.

### 4. Vérifier l'installation

```bash
python scripts/check_setup.py
```

## Utilisation

### Indexer tes livres

Dépose tes fichiers (PDF, EPUB, TXT) dans `data/books/`, puis :

```bash
python scripts/index_books.py --reset
```

`--reset` est nécessaire quand tu remplaces un livre ou changes le découpage. Sans lui, les nouveaux livres sont simplement ajoutés.

### Définir les thèmes

Édite `data/curriculum.yaml` (les thèmes doivent exister dans tes livres) :

```yaml
- topic: present simple
  level: A2
- topic: present perfect
  level: B1
```

### Lancer un cours

```bash
python main.py --force
```

`--force` ignore la règle des 9h et du cours déjà publié. Sans cette option, le script ne s'exécute qu'à partir de 9h (Paris) et une seule fois par jour.

### Outils de test

| Commande | Rôle |
|---|---|
| `python scripts/test_loader.py` | Vérifier la lecture des livres |
| `python scripts/test_cleaner.py` | Voir le nettoyage avant / après |
| `python scripts/test_chunker.py` | Voir les chunks |
| `python scripts/test_retriever.py "present perfect"` | Tester la recherche |
| `python scripts/test_course.py "present simple" A2` | Générer un cours dans le terminal |
| `python scripts/test_notion.py` | Publier le dernier cours sur Notion |

## Configuration

Les réglages sont dans `config.yaml` :

| Clé | Rôle |
|---|---|
| `llm.model` | Modèle Groq (ex. `openai/gpt-oss-120b` pour plus de qualité) |
| `llm.max_tokens` | Limite de sortie (12000 recommandé pour ce modèle) |
| `chunking.max_chars` / `overlap` | Taille des morceaux et chevauchement |
| `retrieval.top_k` | Nombre d'extraits récupérés |
| `retrieval.max_distance` | Seuil au-delà duquel un thème est jugé absent des livres |
| `course.explanation_language` | Langue des explications (`French` ou `English`) |

## Automatisation (GitHub Actions)

Le workflow `.github/workflows/daily_course.yml` lance `python main.py` chaque jour. Deux crons (7h et 8h UTC) couvrent l'heure d'été et d'hiver à Paris ; `main.py` garantit un seul cours par jour.

Mise en place :

1. Crée un dépôt GitHub **privé** (la base vectorielle contient des extraits de tes livres).
2. Pousse le projet (sans `.env` ni `data/books/`).
3. Dans **Settings → Secrets and variables → Actions**, ajoute `GROQ_API_KEY`, `NOTION_TOKEN` et `NOTION_DATABASE_ID`.
4. Teste depuis l'onglet **Actions → Daily English Course → Run workflow**.

Le workflow enregistre lui-même `data/state/progress.json` dans le dépôt pour mémoriser les cours déjà générés. Fais un `git pull` avant de relancer le script en local.

## Maintenance

| Je veux... | Je fais... |
|---|---|
| Ajouter des thèmes | Modifier `curriculum.yaml`, commit + push |
| Changer de livre | `index_books.py --reset`, puis commit + push de `data/vectorstore/` |
| Rejouer un thème | Retirer son entrée de `progress.json`, commit + push |

## Dépannage

| Erreur | Cause probable |
|---|---|
| Notion `404 object_not_found` | Base non partagée avec l'intégration, ou mauvais ID |
| `max completion tokens reached` | `max_tokens` trop bas dans `config.yaml` |
| `KeyError` sur `config.yaml` | Clé manquante dans le fichier de configuration |
| « Thème absent des livres » | Aucun extrait sous `max_distance` : vérifier le thème ou le seuil |
| Base illisible sur GitHub | Version de ChromaDB différente : garder `chromadb==1.5.9` |

## Sécurité

- Ne jamais pousser `.env` ni les clés API.
- Garder le dépôt **privé** et respecter les droits d'auteur de tes livres.
- En cas de clé exposée, la révoquer et en créer une nouvelle.

Pour le détail des choix techniques et des problèmes rencontrés, voir `DOCUMENTATION.md`.
