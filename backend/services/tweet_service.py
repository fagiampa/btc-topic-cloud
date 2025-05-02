import logging
import threading
import time

from repositories.tweet_repository import OpenAITweetRepository, TwitterTweetRepository

class TweetService:
    """Servizio per la gestione dei tweet"""
    def __init__(self, repository, polling_interval=180):
        self.repository = repository
        self.polling_interval = polling_interval
        self._polling_thread = None
        self._continue_polling = False

    def get_tweets(self, time_frame="latest", limit=100):
        """Recupera i tweet dal repository"""
        return self.repository.get_tweets(time_frame, limit)

    def update_tweets(self):
        """Aggiorna i tweet (recupera o genera nuovi tweet)"""
        if isinstance(self.repository, OpenAITweetRepository):
            tweets = self.repository.generate_tweets(count=10)
        elif isinstance(self.repository, TwitterTweetRepository):
            tweets = self.repository.fetch_tweets(query="bitcoin", max_results=10)
        else:
            logging.warning("Tipo di repository non riconosciuto per l'aggiornamento dei tweet")
            tweets = []

        if tweets:
            saved = self.repository.save_tweets(tweets)
            logging.info(f"Salvati {saved} nuovi tweet")
            return saved
        return 0

    def start_polling(self):
        """Avvia il polling periodico per i tweet"""
        if self._polling_thread and self._polling_thread.is_alive():
            return  # Thread già attivo

        self._continue_polling = True
        self._polling_thread = threading.Thread(
            target=self._polling_worker,
            daemon=True
        )
        self._polling_thread.start()
        logging.info("Polling per i tweet avviato")

    def stop_polling(self):
        """Ferma il polling periodico"""
        self._continue_polling = False
        if self._polling_thread:
            self._polling_thread.join(timeout=1.0)
            logging.info("Polling per i tweet fermato")

    def _polling_worker(self):
        """Worker thread per il polling periodico"""
        while self._continue_polling:
            try:
                self.update_tweets()
            except Exception as e:
                logging.error(f"Errore durante il polling dei tweet: {e}")

            time.sleep(self.polling_interval)
