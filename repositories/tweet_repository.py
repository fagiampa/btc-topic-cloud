import time
import json
import logging
import pymongo
from typing import List, Dict, Any

class BaseTweetRepository:
    """Repository base per l'accesso ai tweet"""
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = pymongo.MongoClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]
    
    def get_tweets(self, time_frame="latest", limit=100):
        """Recupera tweet in base al timeframe"""
        query = {}
        if time_frame == "day":
            query = {"timestamp": {"$gte": time.time() - 86400}}  # 24 ore
        elif time_frame == "week":
            query = {"timestamp": {"$gte": time.time() - 604800}}  # 7 giorni
            
        return list(self.collection.find(query).sort("timestamp", -1).limit(limit))
    
    def save_tweets(self, tweets):
        """Salva i tweet nel database"""
        if not tweets:
            return 0
            
        for tweet in tweets:
            if "timestamp" not in tweet:
                tweet["timestamp"] = time.time()
                
        try:
            result = self.collection.insert_many(tweets)
            return len(result.inserted_ids)
        except Exception as e:
            logging.error(f"Errore nel salvare i tweet: {e}")
            return 0


class OpenAITweetRepository(BaseTweetRepository):
    """Repository che genera tweet sintetici con OpenAI"""
    def __init__(self, mongo_uri, db_name, collection_name, openai_api_key):
        super().__init__(mongo_uri, db_name, collection_name)
        self.openai_api_key = openai_api_key
        
        # Inizializza client OpenAI
        try:
            from openai import OpenAI
            self.client_ai = OpenAI(api_key=openai_api_key)
        except Exception as e:
            logging.error(f"Errore nell'inizializzazione di OpenAI: {e}")
            self.client_ai = None
    
    def generate_tweets(self, count=3):
        """Genera tweet sintetici usando OpenAI"""
        if not self.client_ai:
            return []
            
        prompt = f"Return {count} tweets about Bitcoin trends, news, and insights. Format as JSON array with 'text' and 'source' fields."
        
        try:
            response = self.client_ai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You provide JSON data only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=800
            )
            
            text = response.choices[0].message.content.strip()
            
            # Pulizia della risposta
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
                
            tweets = json.loads(text)
            return tweets
            
        except Exception as e:
            logging.error(f"Errore nella generazione di tweet con OpenAI: {e}")
            return []


class TwitterTweetRepository(BaseTweetRepository):
    """Repository che ottiene tweet reali da Twitter/X con Bearer Token e tweepy.Client"""
    def __init__(self, mongo_uri, db_name, collection_name, bearer_token):
        super().__init__(mongo_uri, db_name, collection_name)
        self.bearer_token = bearer_token

        # Inizializza client Twitter con Bearer Token
        try:
            import tweepy
            self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        except Exception as e:
            logging.error(f"Errore nell'inizializzazione di Tweepy Client: {e}")
            self.client = None

    def fetch_tweets(self, query="bitcoin", max_results=100):
        """Recupera tweet reali da Twitter/X usando il nuovo client"""
        if not self.client:
            return []

        try:
            response = self.client.search_recent_tweets(
                query=query,
                tweet_fields=["created_at", "lang"],
                max_results=min(max_results, 100),  # Twitter limita a 100 per richiesta
            )

            result = []
            for tweet in response.data or []:
                if tweet.lang == "en":  # Filtra per lingua inglese
                    tweet_data = {
                        "text": tweet.text,
                        "source": f"https://twitter.com/i/web/status/{tweet.id}",
                        "timestamp": tweet.created_at.timestamp()
                    }
                    result.append(tweet_data)

            return result

        except Exception as e:
            logging.error(f"Errore nel recupero dei tweet con Client: {e}")
            return []
