# tasks.md

- [ ] Example task: Replace this with your real tasks.

## T1: Initialiser le dépôt et la structure de dossiers
- **ID**: T1
- **Description**: Créer la structure `life_assistant/`, initialiser Git, créer les JSON vides.
- **Sous-tâches**:
  1. S1: Créer dossier `life_assistant`
  2. S2: Créer sous-dossiers `utils/`, `messages/`, `memory/`, `workspace/`
  3. S3: Créer fichier `messages/queue.json` avec contenu `{ "messages": [] }`
  4. S4: Créer `memory/profile.json`, `memory/medical.json`, `memory/tasks.json` (tous vides)
  5. S5: Créer `plan.md` vide
  6. S6: Créer `tasks.md` vide
  7. S7: Créer `README.md` avec titre et sections vides
  8. S8: Initialiser un dépôt Git (`git init`, commit initial)
- **Inputs**: Aucun
- **Outputs**: Dossiers et fichiers créés, commit initial
- **Dépendances**: Aucune

## T2: Développer `utils/llm_utils.py` (Mistral AI)
- **ID**: T2
- **Description**: Écrire `llm_utils.py` pour appeler Mistral 7B, Mixtral 8×7B et Codestral Mamba via Ollama ou API Bedrock.
- **Sous-tâches**:
  1. S1: Importer `subprocess` et json
  2. S2: Écrire fonction `def run_llm(prompt: str, model_name: str) -> str:`  
     - S2a: Si `model_name` commence par `mistral-7b`, appeler Ollama/local pour Mistral 7B  
     - S2b: Si `model_name` commence par `mixtral-8x7b`, appeler Ollama/local pour Mixtral 8×7B  
     - S2c: Si `model_name` vaut `codestral-mamba`, appeler Ollama/local pour Codestral Mamba  
     - S2d: Retourner la sortie texte  
  3. S3: Gérer exceptions et logs simples (`try/except`, affichage d’erreurs)  
  4. S4: Tester localement avec un prompt “print('test')” et `mistral-7b`  
- **Inputs**: Aucune (scripts utils)
- **Outputs**: `llm_utils.py` fonctionnel
- **Dépendances**: T1

## T3: Développer `utils/file_utils.py`
- **ID**: T3
- **Description**: Écrire des fonctions pour lire et écrire du JSON de manière thread-safe.
- **Sous-tâches**:
  1. S1: Importer `json` et `Path` de `pathlib`
  2. S2: Créer `def read_json(path: str) -> dict:`  
     - Ouvrir le fichier, charger le JSON (`json.loads`), retourner le dict  
  3. S3: Créer `def write_json(path: str, data: dict) -> None:`  
     - Sérialiser `data` en JSON indenté, écrire dans le fichier  
  4. S4: Tester en lisant/écrivant un fichier JSON temporaire  
- **Inputs**: Aucune
- **Outputs**: `file_utils.py` opérationnel
- **Dépendances**: T1

## T4: Développer `utils/memory_utils.py`
- **ID**: T4
- **Description**: Fonctions pour ajouter/récupérer des entrées dans la mémoire vectorielle avec LangChain/Chroma.
- **Sous-tâches**:
  1. S1: Importer `OpenAIEmbeddings` et `Chroma` depuis `langchain`  
  2. S2: Écrire `def initialize_vector_store() -> Chroma:`  
     - Initialiser embeddings avec `OpenAIEmbeddings(model="text-embedding-ada-002")`  
     - Initialiser `vectordb = Chroma(persist_directory="memory/embeddings.db", embedding_function=embeddings)`  
     - Retourner `vectordb`  
  3. S3: Écrire `def add_to_memory(record: dict, memory_json: str) -> None:`  
     - Lire le JSON avec `read_json(memory_json)`  
     - Ajouter `record` au tableau et écrire le JSON mis à jour  
     - Appeler `vectordb.add_texts([record["text"]], metadatas=[record])`, puis `vectordb.persist()`  
  4. S4: Écrire `def retrieve_from_memory(query: str) -> list:`  
     - Initialiser `vectordb = initialize_vector_store()`  
     - Appeler `docs = vectordb.similarity_search(query, k=5)`  
     - Retourner `[doc.metadata for doc in docs]`  
  5. S5: Tester en ajoutant une entrée `{ "text": "J'aime le cyclisme" }` et en recherchant `"cyclisme"`  
- **Inputs**: Aucune
- **Outputs**: `memory_utils.py` fonctionnel
- **Dépendances**: T3

## T5: Développer `orchestrator.py`
- **ID**: T5
- **Description**: Boucle principale qui lit `messages/queue.json`, délègue aux agents, marque “done” les messages traités, et boucle jusqu’à ce que toutes les tâches dans `tasks.md` soient terminées.
- **Sous-tâches**:
  1. S1: Importer `time`, `json`, `read_json`, `write_json`, `run_llm`  
  2. S2: Définir `QUEUE_PATH = "messages/queue.json"`  
  3. S3: Écrire la fonction `def orchestrate():`  
     - Boucler infiniment  
     - Lire `queue = read_json(QUEUE_PATH)`  
     - Pour chaque `message` dans `queue["messages"]`:  
       - Si `message["status"] == "new"`:  
         - Identifier `target = message["target"]`  
         - `if target == "task_agent": handle_task(message)`  
         - `elif target == "calendar_agent": handle_calendar(message)`  
         - `elif target == "health_agent": handle_health(message)`  
         - `elif target == "memory_agent": handle_memory(message)`  
         - `elif target == "code_agent": handle_code(message)`  
         - Marquer `message["status"] = "done"`  
     - Réécrire le JSON avec `write_json(QUEUE_PATH, queue)`  
     - Vérifier si **toutes** les tâches de `tasks.md` sont marquées “done” (parser `tasks.md`) ; si oui, sortir de la boucle  
     - `time.sleep(1)`  
  4. S4: Définir `def handle_task(msg):` pour appeler `task_agent.py` avec `msg["payload"]`  
  5. S5: Définir `def handle_calendar(msg):` pour appeler `calendar_agent.py`  
  6. S6: Définir `def handle_health(msg):` pour appeler `health_agent.py`  
  7. S7: Définir `def handle_memory(msg):` pour appeler `memory_agent.py`  
  8. S8: Définir `def handle_code(msg):` pour appeler `code_agent.py`  
  9. S9: Écrire le bloc `if __name__ == "__main__": orchestrate()`  
- **Inputs**: Aucune
- **Outputs**: `orchestrator.py` opérationnel  
- **Dépendances**: T2, T3, T4

## T6: Développer `task_agent.py`
- **ID**: T6
- **Description**: Gérer la création, la mise à jour, la suppression et les rappels de tâches dans `memory/tasks.json`.
- **Sous-tâches**:
  1. S1: Importer `datetime`, `read_json`, `write_json`  
  2. S2: Définir `TASK_PATH = "memory/tasks.json"`  
  3. S3: Écrire `def create_task(payload: dict) -> None:`  
     - `tasks = read_json(TASK_PATH)`  
     - Construire un objet `new_task = {"id": payload["id"], "title": payload["data"]["title"], "due_date": payload["data"]["due_date"], "status": "new"}`  
     - `tasks.append(new_task)`  
     - `write_json(TASK_PATH, tasks)`  
  4. S4: Écrire `def update_task(payload: dict) -> None:`  
     - `tasks = read_json(TASK_PATH)`  
     - Parcourir `tasks` jusqu’à `t["id"] == payload["id"]`, puis `t.update(payload["data"])`  
     - `write_json(TASK_PATH, tasks)`  
  5. S5: Écrire `def delete_task(payload: dict) -> None:`  
     - `tasks = [t for t in read_json(TASK_PATH) if t["id"] != payload["id"]]`  
     - `write_json(TASK_PATH, tasks)`  
  6. S6: Écrire `def schedule_reminders():`  
     - Importer `schedule` ou `APScheduler`  
     - Charger `tasks = read_json(TASK_PATH)`  
     - Pour chaque `task` où `task["status"] != "done"`:  
       - Convertir `due_date` en datetime Python  
       - Si `now + delta == due_date`, envoyer un message dans `messages/queue.json` pour notification  
  7. S7: Ajouter un appel à `schedule_reminders()` au lancement de `task_agent.py` (exécution asynchrone)  
  8. S8: Tester en créant une tâche avec échéance à 1 minute et vérifier la notification dans `queue.json`  
- **Inputs**: Aucune
- **Outputs**: `task_agent.py` opérationnel  
- **Dépendances**: T5

## T7: Développer `calendar_agent.py`
- **ID**: T7
- **Description**: Communiquer avec l’API Google Calendar pour créer des événements, détecter les conflits, et répondre avec les créneaux disponibles.
- **Sous-tâches**:
  1. S1: Installer `google-api-python-client` et `oauth2client`  
  2. S2: Importer `build` depuis `googleapiclient.discovery` et `service_account` depuis `google.oauth2`  
  3. S3: Définir `SCOPES = ['https://www.googleapis.com/auth/calendar']` et `SERVICE_ACCOUNT_FILE = 'credentials.json'`  
  4. S4: Écrire `def get_service() -> Resource:`  
     - Charger les credentials via `service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)`  
     - `service = build('calendar', 'v3', credentials=creds)`  
     - Retourner `service`  
  5. S5: Écrire `def create_event(payload: dict) -> str:`  
     - Construire l’objet `event` avec `summary`, `start`, `end`, `attendees` (list d’emails)  
     - `created = service.events().insert(calendarId='primary', body=event).execute()`  
     - `return created.get("id")`  
  6. S6: Écrire `def detect_conflicts(payload: dict) -> bool:`  
     - Construire `body = {"timeMin": payload["data"]["start"], "timeMax": payload["data"]["end"], "items": [{"id": 'primary'}]}`  
     - `events_result = service.freebusy().query(body=body).execute()`  
     - `busy = events_result["calendars"]['primary']["busy"]`  
     - `return len(busy) == 0`  
  7. S7: Exemple d’appel : si conflit, écrire dans `messages/queue.json` un message `{"type":"calendar_response","payload":{"status":"conflict"}}`  
  8. S8: Tester en créant un événement dans un calendrier vide, puis essayer un événement qui chevauche.  
- **Inputs**: `credentials.json` (API Google Calendar)  
- **Outputs**: `calendar_agent.py` fonctionnel  
- **Dépendances**: T5

## T8: Développer `health_agent.py`
- **ID**: T8
- **Description**: Gérer `memory/medical.json` : ajouter des enregistrements médicaux (médicaments, allergies, rendez-vous) et planifier des rappels santé.
- **Sous-tâches**:
  1. S1: Importer `read_json`, `write_json`, `datetime`  
  2. S2: Définir `MEDICAL_PATH = "memory/medical.json"`  
  3. S3: Écrire `def update_medical(payload: dict) -> None:`  
     - `data = read_json(MEDICAL_PATH)`  
     - Construire `entry = {"id": payload["id"], "type": payload["data"].get("type","medication"), "details": payload["data"]["details"], "timestamp": datetime.datetime.now().isoformat()}`  
     - `data.append(entry)`  
     - `write_json(MEDICAL_PATH, data)`  
  4. S4: Écrire `def set_reminder(payload: dict) -> None:`  
     - Utiliser `schedule` ou `APScheduler` pour planifier un rappel quotidien/hebdomadaire selon `payload["data"]["frequency"]`  
     - Exemple: si `payload["data"]["type"] == "medication"`, planifier un rappel `messages/queue.json` tous les jours à heure définie  
  5. S5: Tester : envoyer un message `{"type":"medical_update","payload":{"id":"m1","data":{"type":"medication","details":"Lisinopril 10mg"}}}` dans `queue.json`, vérifier que `medical.json` est mis à jour et que le rappel est planifié.  
- **Inputs**: Aucune  
- **Outputs**: `health_agent.py` opérationnel  
- **Dépendances**: T5

## T9: Développer `memory_agent.py`
- **ID**: T9
- **Description**: Gérer la mémoire structurée (`memory/profile.json`) et la mémoire vectorielle (`memory/embeddings.db`).
- **Sous-tâches**:
  1. S1: Importer `read_json`, `write_json`, fonctions `add_to_memory`, `retrieve_from_memory` depuis `memory_utils.py`  
  2. S2: Définir `PROFILE_PATH = "memory/profile.json"`  
  3. S3: Écrire `def update_memory(payload: dict) -> None:`  
     - `add_to_memory(payload["data"], PROFILE_PATH)`  
  4. S4: Écrire `def query_memory(payload: dict) -> list:`  
     - `results = retrieve_from_memory(payload["data"]["query"])`  
     - `return results`  
  5. S5: Ajouter dans `orchestrator.py` un appel à `query_memory` pour répondre aux requêtes mémoire (le résultat peut être écrit dans `messages/queue.json` pour l’affichage)  
  6. S6: Tester en ajoutant un enregistrement `{ "text": "Utilisateur aime le cyclisme" }` et en interrogeant “cyclisme”.  
- **Inputs**: Aucune  
- **Outputs**: `memory_agent.py` opérationnel  
- **Dépendances**: T4, T5

## T10: Développer `code_agent.py`
- **ID**: T10
- **Description**: Gérer la génération et la modification de code dans `workspace/` en utilisant **Codestral Mamba**.
- **Sous-tâches**:
  1. S1: Importer `os`, `subprocess`, `read_json`, `write_json`, `run_llm`  
  2. S2: Définir `CODE_WORKSPACE = "workspace/"`  
  3. S3: Écrire `def generate_code(payload: dict) -> str:`  
     - `spec = payload["data"]["spec"]` (description NL)  
     - `filename = payload["data"]["filename"]`  
     - `code = run_llm(spec, model_name="codestral-mamba")`  
     - `file_path = os.path.join(CODE_WORKSPACE, filename)`  
     - Ouvrir `file_path` en écriture et y écrire `code`  
     - `return file_path`  
  4. S4: Écrire `def modify_code(payload: dict) -> None:`  
     - `file_path = os.path.join(CODE_WORKSPACE, payload["data"]["filename"])`  
     - Lire le contenu existant, remplacer `old` par `new` selon `payload["data"]`, puis réécrire  
  5. S5: Écrire `def delete_code(payload: dict) -> None:`  
     - `file_path = os.path.join(CODE_WORKSPACE, payload["data"]["filename"])`  
     - `if os.path.exists(file_path): os.remove(file_path)`  
  6. S6: Écrire `def run_code(payload: dict) -> str:`  
     - `file_path = os.path.join(CODE_WORKSPACE, payload["data"]["filename"])`  
     - `result = subprocess.run(["python", file_path], capture_output=True, text=True)`  
     - `return result.stdout`  
  7. S7: Tester en envoyant un message `{"type":"code_task","payload":{"id":"c1","data":{"spec":"Écrire un script Python qui affiche 'Bonjour, monde'","filename":"hello.py"}}}` dans `queue.json`, puis vérifier que `hello.py` est créé et exécutable.  
- **Inputs**: Aucune  
- **Outputs**: `code_agent.py` opérationnel  
- **Dépendances**: T5

## T11: Rédiger des tests unitaires pour chaque agent
- **ID**: T11
- **Description**: Créer un dossier `tests/` et écrire un fichier de tests pour chaque agent, utilisant `pytest`.  
- **Sous-tâches**:
  1. S1: Créer dossier `tests/`  
  2. S2: Écrire `tests/test_orchestrator.py` :  
     - Simuler un message JSON de type `task_agent`  
     - Vérifier que `orchestrator.py` délègue correctement et marque “done”  
  3. S3: Écrire `tests/test_task_agent.py` :  
     - Appeler `create_task`, `update_task`, `delete_task`  
     - Vérifier le contenu de `memory/tasks.json`  
  4. S4: Écrire `tests/test_calendar_agent.py` :  
     - Simuler `create_event` et `detect_conflicts` (utiliser un mock de l’API)  
  5. S5: Écrire `tests/test_health_agent.py` :  
     - Appeler `update_medical` et `set_reminder`, vérifier `memory/medical.json`  
  6. S6: Écrire `tests/test_memory_agent.py` :  
     - Ajouter des entrées, interroger, vérifier vecteur et JSON  
  7. S7: Écrire `tests/test_code_agent.py` :  
     - Générer un script, modifier, exécuter, vérifier la sortie  
- **Inputs**: Aucune  
- **Outputs**: Jeux de tests `tests/*`  
- **Dépendances**: T6, T7, T8, T9, T10

## T12: Mettre en place la boucle finale de complétion
- **ID**: T12
- **Description**: Mettre à jour `orchestrator.py` pour lire `tasks.md` après chaque itération et vérifier si toutes les tâches sont marquées “done”. Si oui, quitter la boucle et générer un rapport dans `logs/completion_report.txt`.  
- **Sous-tâches**:
  1. S1: Dans `orchestrator.py`, après avoir traité `queue.json`, ouvrir et parser `tasks.md`  
  2. S2: Vérifier que tous les pointeurs Markdown `- [ ]` sont remplacés par `- [x]`  
  3. S3: Si toutes les tâches sont “done”, écrire dans `logs/completion_report.txt` la date/heure et le résumé des tâches terminées  
  4. S4: Sortir de la boucle principale  
  5. S5: Tester en mettant manuellement toutes les tâches comme “done” dans `tasks.md`, lancer l’orchestrateur, vérifier la sortie dans `completion_report.txt`.  
- **Inputs**: `tasks.md`  
- **Outputs**: `orchestrator.py` mis à jour, rapport de complétion généré  
- **Dépendances**: T11

## T13: Préparer le déploiement Docker et finaliser la documentation
- **ID**: T13
- **Description**: Écrire un `Dockerfile` pour conteneuriser l’application, créer `requirements.txt`, et finaliser `README.md` avec instructions d’installation, configuration (clés API, modèles Mistral via Ollama) et exemples d’utilisation.  
- **Sous-tâches**:
  1. S1: Créer `Dockerfile` basé sur `python:3.10-slim`  
  2. S2: Copier tout le dossier `life_assistant/` dans le conteneur  
  3. S3: Installer les dépendances Python (`pip install -r requirements.txt`)  
  4. S4: Définir point d’entrée `CMD ["python", "orchestrator.py"]`  
  5. S5: Créer `requirements.txt` listant `langchain`, `chromadb`, `google-api-python-client`, `oauth2client`, `APScheduler`, `pytest`, `mistral-ai` (ou llm client approprié)  
  6. S6: Mettre à jour `README.md` :  
     - Description générale  
     - Prérequis (Ollama, Google Calendar, Python 3.10)  
     - Instructions d’installation locale (`venv`, `pip install`)  
     - Exemple d’utilisation (démarrer orchestrateur, envoyer un message)  
     - Structure du projet  
- **Inputs**: Code final, dépendances  
- **Outputs**: `Dockerfile`, `requirements.txt`, `README.md` finalisé  
- **Dépendances**: T12

## T14: Validation finale et livraison
- **ID**: T14
- **Description**: Vérifier que toutes les tâches sont terminées, exécuter tous les tests, valider le conteneur Docker, puis créer un tag Git `v1.0-release`.  
- **Sous-tâches**:
  1. S1: Lancer `pytest` et corriger les éventuels tests en erreur  
  2. S2: Construire l’image Docker (`docker build -t life_assistant:latest .`)  
  3. S3: Lancer un conteneur avec l’image et vérifier qu’il démarre correctement (`docker run --rm life_assistant:latest`)  
  4. S4: Faire un commit final (`Git tag v1.0-release`)  
- **Inputs**: Code, tests, Dockerfile  
- **Outputs**: Binaire/service Docker fonctionnel, tag Git  
- **Dépendances**: T13
