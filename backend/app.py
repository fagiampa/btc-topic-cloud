from flask import Flask
from flask_cors import CORS
import logging
import os
import threading

# Importa i moduli personalizzati
from config import (
    MONGO_URI, MONGO_DB, MONGO_TWEETS_COLLECTION, TOPIC_COLLECTION,
    OPENAI_API_KEY, TWEET_SOURCE, SPARK_CONFIG, POLLING_INTERVAL,BEARER_TOKEN
)
from repositories.tweet_repository import OpenAITweetRepository, TwitterTweetRepository
from services.tweet_service import TweetService
from services.topic_service import TopicService
from api.routes import topic_bp

# Configurazione logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inizializza il repository appropriato
if TWEET_SOURCE.lower() == "twitter":
    tweet_repository = TwitterTweetRepository(
        MONGO_URI, 
        MONGO_DB, 
        MONGO_TWEETS_COLLECTION,
        BEARER_TOKEN
    )
else:  # Default: OpenAI
    tweet_repository = OpenAITweetRepository(
        MONGO_URI, 
        MONGO_DB, 
        MONGO_TWEETS_COLLECTION,
        OPENAI_API_KEY
    )

# Inizializza i servizi
tweet_service = TweetService(tweet_repository, POLLING_INTERVAL)
topic_service = TopicService(SPARK_CONFIG, MONGO_URI, MONGO_DB, TOPIC_COLLECTION)

# Crea l'app Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Registra i blueprint
app.register_blueprint(topic_bp)

# Condividi i servizi con i blueprint
app.config['TWEET_SERVICE'] = tweet_service
app.config['TOPIC_SERVICE'] = topic_service

@app.route('/')
def index():
    """Pagina principale che serve l'interfaccia frontend"""
    return app.send_static_file('index.html')

if __name__ == "__main__":
    try:
        # Avvia il polling dei tweet
        tweet_service.start_polling()
        
        # Assicurati di avere alcuni tweet iniziali
        tweet_service.update_tweets()
        
        # Avvia l'app
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Ferma il polling quando l'app termina
        tweet_service.stop_polling()