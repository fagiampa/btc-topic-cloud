from decouple import config

# MongoDB configuration
MONGO_URI = config('MONGO_URI', default="mongodb://mongodb:27017/")
MONGO_DB = config('MONGO_DB', default="crypto_analysis")
MONGO_TWEETS_COLLECTION = config('MONGO_TWEETS_COLLECTION', default="btc_tweets")
TOPIC_COLLECTION = config('TOPIC_COLLECTION', default="btc_topics")

# Fonte dei tweet: "openai" o "twitter"
TWEET_SOURCE = config('TWEET_SOURCE', default="openai")

# Intervallo di polling in secondi
POLLING_INTERVAL = config('POLLING_INTERVAL', default=3600, cast=int)  # 1 ora

# Time Frame update topic
TIME_UPDATE_TOPIC = 60

# OpenAI configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default="")
# X configuration
BEARER_TOKEN = config('BEARERTOKEN')

# Spark configuration
SPARK_CONFIG = {
    "appName": "BTC_Topic_Cloud",
    "master": "local[*]",
    "executor.heartbeatInterval": "30s",
    "rpc.askTimeout": "600s",
    "network.timeout": "800s",
    "python.worker.reuse": "false",
    "driver.memory": "2g",
    "executor.memory": "2g",
    "rpc.message.maxSize": "256"
}

# Topic model configuration
NUM_TOPICS = config('NUM_TOPICS', default=5, cast=int)
MAX_WORDS_PER_TOPIC = config('MAX_WORDS_PER_TOPIC', default=10, cast=int)
