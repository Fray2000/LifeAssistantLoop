# plan.md

- [ ] **Initialisation du dépôt et structure de dossiers**  
  Description: Créer la structure `life_assistant/`, initialiser Git, créer les JSON vides dans `messages/` et `memory/`.  
  Dépendance: Aucune  

- [ ] **Installation des modèles Mistral AI**  
  Description: Installer et configurer Mistral 7B et Mixtral 8×7B pour l’Orchestrator, le Task Agent, le Calendar Agent, le Health Agent et le Memory Agent; installer Codestral Mamba pour le Code Agent.  
  Dépendance: Initialisation du dépôt  

- [ ] **Développement de l’Orchestrator Agent**  
  Description: Écrire `orchestrator.py` pour lire `messages/queue.json`, parser chaque message (“new”), identifier le champ `target`, et déléguer la charge à l’agent concerné (task_agent, calendar_agent, health_agent, memory_agent, code_agent), puis marquer le message comme “done”. Ajouter gestion d’erreurs et logs.  
  Dépendance: Installation des modèles Mistral AI  

- [ ] **Développement du Task Management Agent**  
  Description: Écrire `task_agent.py` avec fonctions pour créer, mettre à jour, supprimer des tâches dans `memory/tasks.json` et planifier des rappels. Inclure un scheduler (par ex. `APScheduler` ou `schedule`) pour envoyer des rappels selon les échéances.  
  Dépendance: Développement de l’Orchestrator Agent  

- [ ] **Développement du Calendar Scheduling Agent**  
  Description: Écrire `calendar_agent.py` pour se connecter à Google Calendar (via l’API) et prendre en charge la création d’événements (`create_event`), la détection de conflits (`detect_conflicts`), et l’envoi de réponses au queue JSON.  
  Dépendance: Développement de l’Orchestrator Agent  

- [ ] **Développement du Health Data Management Agent**  
  Description: Écrire `health_agent.py` pour gérer `memory/medical.json` : ajouter des entrées (médicaments, rendez-vous) et planifier des rappels santé (prise de médicaments).  
  Dépendance: Développement de l’Orchestrator Agent  

- [ ] **Développement du Memory Agent**  
  Description: Écrire `memory_agent.py` pour gérer `memory/profile.json` (mise à jour des préférences, historique) et `memory/embeddings.db` (index de vecteurs via LangChain ou Chromadb). Fournir fonctions `add_to_memory(record: dict)` et `retrieve_from_memory(query: str)`.  
  Dépendance: Développement de l’Orchestrator Agent  

- [ ] **Développement du Code Generation Agent**  
  Description: Écrire `code_agent.py` pour utiliser **Codestral Mamba** (via `run_llm(prompt, "codestral-mamba")`) afin de générer et modifier du code dans `workspace/`. Inclure fonctions :  
    - `generate_code(spec: str, filename: str) -> str` (création d’un fichier `.py`)  
    - `modify_code(filename: str, old: str, new: str) -> None` (remplacement de chaînes)  
    - `delete_code(filename: str) -> None`  
    - `run_code(filename: str) -> str` (exécution Python via `subprocess.run`)  
  Dépendance: Développement de l’Orchestrator Agent  

- [ ] **Intégration et Tests**  
  Description: Créer `tests/` avec des tests unitaires pour chaque agent (orchestrator, task, calendar, health, memory, code). Écrire des scénarios d’intégration qui simulent des messages dans `queue.json` et vérifient que chaque agent répond correctement.  
  Dépendance: Tous les agents  

- [ ] **Boucle de complétion automatique**  
  Description: Mettre à jour `orchestrator.py` pour relire `tasks.md` et s’assurer que la boucle d’exécution s’arrête seulement lorsque toutes les tâches sont marquées “done” dans `tasks.md`. Ajouter un script qui, à la fin, génère un rapport final des tâches complétées.  
  Dépendance: Intégration et Tests  

- [ ] **Déploiement (Docker) et Documentation**  
  Description: Écrire un `Dockerfile` pour conteneuriser l’application (inclure installation des dépendances Python, configuration des modèles Mistral via Ollama). Rédiger `README.md` avec :  
    - Instructions d’installation locale (venv, dependances).  
    - Configuration des clés API (Google Calendar, Ollama).  
    - Exemple d’utilisation pas à pas (démarrer l’orchestrator, envoyer un message).  
    - Structure du projet.  
  Dépendance: Boucle de complétion automatique
