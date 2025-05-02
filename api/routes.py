from flask import Blueprint, jsonify, request, current_app
import logging

# Blueprint API per i topic
topic_bp = Blueprint('topics', __name__, url_prefix='/api/topics')

@topic_bp.route('/', methods=['GET'])
def get_topics():
    """Endpoint per recuperare i topic"""
    time_frame = request.args.get('time_frame', 'latest')
    
     # Ottieni i servizi dal contesto dell'applicazione
    topic_service = current_app.config['TOPIC_SERVICE']
    tweet_service = current_app.config['TWEET_SERVICE']
    
    try:
        # Recupera i topic dal servizio
        topics = topic_service.get_topics(time_frame)
        
        # Se i topic non esistono o sono vecchi, aggiornali
        if not topics:
            # Recupera i tweet per l'aggiornamento
            tweets = tweet_service.get_tweets(time_frame)
            tweets_text = [t["text"] for t in tweets if "text" in t]
            
            # Aggiorna i topic
            topics = topic_service.update_topics(tweets_text, time_frame)
        
        if topics:
            return jsonify(topics)
        else:
            return jsonify([])  # Array vuoto invece che errore
            
    except Exception as e:
        logging.error(f"Errore nell'endpoint dei topic: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Altri endpoint possono essere aggiunti qui
