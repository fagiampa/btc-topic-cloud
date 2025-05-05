# Bitcoin Topic Cloud

Un'applicazione web che analizza i tweet su Bitcoin, identifica i principali argomenti di discussione e li visualizza in una word cloud interattiva. L'applicazione utilizza una pipeline di elaborazione dati con PySpark, MongoDB, Flask e D3.js.

![Screenshot dell'applicazione](./screenshots/docs/images/WordCloudExample.png)

## 🔍 Panoramica

Bitcoin Topic Cloud estrae e analizza automaticamente i tweet relativi a Bitcoin da:
- Twitter/X (tramite API ufficiale)
- OpenAI (generazione di tweet simulati per testing)

L'applicazione applica algoritmi di elaborazione del linguaggio naturale per identificare gli argomenti più discussi e li visualizza in una word cloud interattiva dove la dimensione e il colore delle parole riflettono la loro rilevanza.

## 🏗️ Architettura


- **Backend (Python/Flask)**:
  - API RESTful per l'accesso ai dati
  - Polling automatico per nuovi tweet
  - Elaborazione NLP con PySpark
  - Estrazione dei topic con algoritmo LDA

- **Frontend**:
  - Visualizzazione dei topic con D3.js
  - Word cloud interattiva
  - Filtri temporali (ultimo aggiornamento, 24 ore, settimana)

- **Persistenza**:
  - MongoDB per l'archiviazione di tweet e topic
  - Aggiornamento periodico dei dati

## 🚀 Installazione

### Prerequisiti

- Docker e Docker Compose
- Account Twitter/X con Bearer Token (opzionale)
- Chiave API OpenAI (opzionale)

### Configurazione

1. Clona il repository:
   ```bash
   git clone https://github.com/yourusername/bitcoin-topic-cloud.git
   cd bitcoin-topic-cloud
   ```

2. Configura le variabili d'ambiente:
   - Crea o modifica il file `backend/.env` con i seguenti parametri:
   ```
   BEARERTOKEN=il_tuo_bearer_token_twitter
   OPENAI_API_KEY=la_tua_chiave_api_openai
   TWEET_SOURCE=twitter  # oppure "openai" per i tweet simulati
   ```

### Avvio

Avvia l'applicazione con Docker Compose:

```bash
docker-compose up -d
```

L'applicazione sarà disponibile all'indirizzo: http://localhost:5000

## 🔧 Configurazione avanzata

### Parametri modificabili in `config.py`:

- `POLLING_INTERVAL`: intervallo di aggiornamento dei tweet (default: 3600 secondi)
- `TIME_UPDATE_TOPIC`: intervallo di aggiornamento dei topic (default: 60 secondi)
- `NUM_TOPICS`: numero di topic da estrarre (default: 5)
- `MAX_WORDS_PER_TOPIC`: massimo numero di parole per topic (default: 10)

### Configurazione dello stack Spark

Modifica i parametri in `SPARK_CONFIG` nel file `config.py` per ottimizzare le prestazioni in base al tuo hardware.

## 📚 Funzionalità principali

- **Estrazione automatica dei tweet**:
  - Da Twitter/X con autenticazione Bearer Token
  - Generati da OpenAI per test e sviluppo

- **Analisi del linguaggio naturale**:
  - Tokenizzazione e rimozione delle stopwords
  - Estrazione di bigrammi significativi
  - Modellazione dei topic con LDA (Latent Dirichlet Allocation)

- **Visualizzazione interattiva**:
  - Word cloud dinamica con animazioni
  - Filtri temporali
  - Interazioni hover

## 🔄 API

### Endpoints disponibili:

- `GET /api/topics/`
  - Parametri: `time_frame` (values: "latest", "day", "week")
  - Restituisce i topic estratti dai tweet nel periodo specificato

## 👨‍💻 Sviluppo

### Struttura del progetto

```
bitcoin-topic-cloud/
├── backend/
│   ├── api/
│   │   └── routes.py           # Endpoints API
│   ├── repositories/
│   │   └── tweet_repository.py # Accesso a Twitter/OpenAI
│   ├── services/
│   │   ├── topic_service.py    # Analisi NLP con PySpark
│   │   └── tweet_service.py    # Gestione tweet
│   ├── static/
│   │   └── index.html          # Frontend
│   ├── .env                    # Configurazioni private
│   ├── app.py                  # Server Flask
│   ├── config.py               # Configurazioni
│   ├── Dockerfile              # Configurazione container
│   └── requirements.txt        # Dipendenze Python
└── docker-compose.yml          # Orchestrazione container
```

## 📝 Note

- L'applicazione richiede una quantità significativa di memoria per eseguire Apache Spark
- Per ridurre il consumo di risorse, modificare i parametri `driver.memory` e `executor.memory` in `config.py`
- I tweet vengono aggiornati periodicamente in base alla configurazione `POLLING_INTERVAL`

## 🤝 Contributi

Contributi, issue e feature request sono benvenuti! Sentiti libero di controllare la pagina [issues](https://github.com/yourusername/bitcoin-topic-cloud/issues).

## 📄 Licenza

Questo progetto è distribuito con licenza MIT. Vedi il file `LICENSE` per maggiori informazioni.
