import time
import logging
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, NGram
from pyspark.ml.clustering import LDA
from pyspark.sql.functions import regexp_replace, col, explode, count, udf, array_except
from pyspark.sql.types import ArrayType, StringType

# Importa i moduli personalizzati
from config import (
    TIME_UPDATE_TOPIC
)

class TopicService:
    """Servizio per l'estrazione dei topic dai tweet"""
    def __init__(self, spark_config, mongo_uri, db_name, topics_collection):
        self.spark = self._create_spark_session(spark_config)
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.topics_collection = topics_collection
        
        # Client MongoDB
        import pymongo
        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.topics_db = self.mongo_client[db_name][topics_collection]
    
    def _create_spark_session(self, config):
        """Crea una sessione Spark con la configurazione specificata"""
        builder = SparkSession.builder.appName(config["appName"])
        
        for key, value in config.items():
            if key != "appName":
                builder = builder.config(f"spark.{key}", value)
                
        return builder.getOrCreate()
    
    def extract_topics(self, tweets, num_topics=5, max_words=10):
        """Estrai i topic dai tweet usando LDA"""
        if not tweets or len(tweets) < 10:
            logging.warning("Troppo pochi tweet per l'estrazione dei topic")
            return None
            
        # Converti i tweet in DataFrame Spark
        tweet_df = self.spark.createDataFrame([(t,) for t in tweets], ["text"])
        
        # Preprocessing
        tweet_df = tweet_df.withColumn("text", regexp_replace(col("text"), r"https?://\S+", ""))
        tweet_df = tweet_df.withColumn("text", regexp_replace(col("text"), r"www\.\S+", ""))
        
        # Tokenizzazione
        tokenizer = Tokenizer(inputCol="text", outputCol="words")
        words_data = tokenizer.transform(tweet_df)
        
        # Rimozione stopwords
        remover = StopWordsRemover(inputCol="words", outputCol="filtered")
        custom_stopwords = ['https', 'http', 'co', 'rt', 'amp', 'bitcoin', 'btc', '#btc', '#bitcoin', '#cryptocurrency', '#crypto', 'bitcoin\'s']
        remover.setStopWords(remover.getStopWords() + custom_stopwords)
        filtered_data = remover.transform(words_data)
        
        # Bigrammi
        ngram = NGram(n=2, inputCol="filtered", outputCol="bigrams")
        bigram_data = ngram.transform(filtered_data)
        
        # Calcolo frequenza bigrammi
        bigrams_exploded = bigram_data.select(explode(col("bigrams")).alias("bigram"))
        bigram_freq = bigrams_exploded.groupBy("bigram").agg(count("*").alias("freq"))
        frequent_bigrams = bigram_freq.filter(col("freq") >= 3).select("bigram").rdd.flatMap(lambda x: x).collect()
        frequent_bigrams_set = set(frequent_bigrams)
        
        # Merge di parole singole e bigrammi rilevanti
        def extract_relevant_terms(words, bigrams):
            result = []
            words_to_remove = set()
            
            for bigram in bigrams:
                if bigram in frequent_bigrams_set:
                    parts = bigram.split()
                    
                    # Handle different cases based on number of parts
                    if len(parts) == 2:
                        # Normal case: two words separated by space
                        w1, w2 = parts
                        result.append(f"{w1}_{w2}")
                        words_to_remove.update([w1, w2])
                    elif len(parts) == 1:
                        # Single word case
                        result.append(parts[0])
                        if parts[0] in words:
                            words_to_remove.add(parts[0])
                    elif len(parts) == 0:
                        # Empty string case (unlikely but handling it)
                        continue
                    else:
                        # More than 2 words (join them with underscores)
                        result.append("_".join(parts))
                        words_to_remove.update(parts)
            
            remaining = [w for w in words if w not in words_to_remove]
            return remaining + result
            
        merge_udf = udf(extract_relevant_terms, ArrayType(StringType()))
        processed_data = bigram_data.withColumn(
            "final_tokens", 
            merge_udf(col("filtered"), col("bigrams"))
        )
        
        # Vettorizzazione
        cv = CountVectorizer(inputCol="final_tokens", outputCol="features", vocabSize=5000, minDF=1.0)
        cv_model = cv.fit(processed_data)
        vectorized_data = cv_model.transform(processed_data)
        
        # Estrazione topic con LDA
        k = min(num_topics, len(tweets) // 2, 5)
        k = max(k, 2)  # Almeno 2 topic
        
        lda = LDA(k=k, maxIter=20, optimizer="em")
        lda_model = lda.fit(vectorized_data)
        
        # Raccolta risultati
        topics_data = []
        vocab = cv_model.vocabulary
        topics = lda_model.describeTopics(max_words)
        
        for topic in topics.collect():
            topic_id = topic.topic
            term_indices = topic.termIndices
            term_weights = topic.termWeights
            
            terms = [(vocab[idx].replace("_", " "), float(weight)) 
                    for idx, weight in zip(term_indices, term_weights)]
            
            # Normalizzazione pesi
            max_weight = max([w for _, w in terms]) if terms else 1.0
            normalized_terms = [(term, (weight/max_weight)*100) for term, weight in terms]
            
            topics_data.append({
                "topic_id": int(topic_id),
                "terms": normalized_terms
            })
        
        return topics_data
    
    def update_topics(self, tweets, time_frame="latest"):
        """Aggiorna i topic nel database"""
        topics_data = self.extract_topics(tweets)
        
        if topics_data:
            # Salva i topic nel database
            result = self.topics_db.insert_one({
                "topics": topics_data,
                "time_frame": time_frame,
                "timestamp": time.time()
            })
            logging.info(f"Topic aggiornati per {time_frame}, ID: {result.inserted_id}")
            return topics_data
        else:
            logging.warning(f"Nessun topic generato per {time_frame}")
            return None
    
    def get_topics(self, time_frame="latest", force_update=False):
        """Recupera i topic dal database, aggiornandoli se necessario"""
        # Cerca i topic più recenti
        latest_topics = self.topics_db.find_one(
            {"time_frame": time_frame}, 
            sort=[("timestamp", -1)]
        )
        
        # Se non ci sono topic o sono vecchi, aggiorna
        if (not latest_topics or 
            time.time() - latest_topics["timestamp"] > TIME_UPDATE_TOPIC or 
            force_update):
            
            # Qui dovresti recuperare i tweet per l'aggiornamento
            # Per semplicità, supponiamo che vengano passati come parametro
            return None  # I tweet dovranno essere passati dall'esterno
        
        return latest_topics["topics"] if latest_topics else None
