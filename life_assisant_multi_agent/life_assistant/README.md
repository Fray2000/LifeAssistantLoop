# Autonomous Life Assistant (Multi-Agent) avec Mistral AI

## Description
Assistant personnel autonome multi-agent utilisant exclusivement des modèles Mistral AI :
- **Orchestrator Agent** : Mistral 7B ou Mixtral 8×7B
- **Task Management Agent** : Mistral 7B
- **Calendar Scheduling Agent** : Mistral 7B
- **Health Data Management Agent** : Mistral 7B
- **Memory Agent** : Mixtral 8×7B / Mistral 7B
- **Code Generation Agent** : Codestral Mamba

## Structure du projet
life_assistant/  
├── orchestrator.py  
├── interface_agent.py  
├── task_agent.py  
├── calendar_agent.py  
├── health_agent.py  
├── memory_agent.py  
├── code_agent.py  
├── utils/  
│   ├── file_utils.py  
│   ├── llm_utils.py  
│   └── memory_utils.py  
├── workspace/  
├── messages/  
│   └── queue.json  
├── memory/  
│   ├── profile.json  
│   ├── medical.json  
│   ├── tasks.json  
│   ├── embeddings.db  
│   └── memory_engine.py  
├── plan.md  
├── tasks.md  
└── README.md  

## Prérequis
- Python 3.10+  
- Ollama CLI (configuré pour Mistral 7B, Mixtral 8×7B, Codestral Mamba)  
- Clés API Google Calendar (`credentials.json`)  
- `pip install -r requirements.txt`  

## Installation locale
```bash
git clone <repo_url>
cd life_assistant
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python orchestrator.py
```

## Utilisation

1. Lancer `python orchestrator.py`.
2. Envoyer des messages JSON dans `messages/queue.json` (ex. créer une tâche, un événement, un enregistrement médical, une requête mémoire, ou une tâche de code).
3. Lire les messages de réponse dans `messages/queue.json` (ex. rappels, sorties de code, résultats mémoire).

## Déploiement Docker

```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "orchestrator.py"]
```

Construire l’image:

```bash
docker build -t life_assistant:latest .
docker run --rm life_assistant:latest
```

## Tests

```bash
pytest tests/
```

## Contribuer

* Créer une nouvelle branche Git
* Écrire des tests pour toute nouvelle fonctionnalité
* Soumettre un Pull Request
