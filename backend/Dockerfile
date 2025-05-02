FROM python:3.9-slim

# Installa Java (OpenJDK 17) per PySpark
RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk \
    curl \
    && apt-get clean

# Imposta JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Verifica il percorso esatto di Python e crea un symlink se necessario
RUN which python3 && \
    ln -sf $(which python3) /usr/bin/python3

# Installa Spark
ENV SPARK_VERSION=3.3.2
ENV SPARK_HOME=/opt/spark

RUN curl -sL https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz | tar -xz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop3 ${SPARK_HOME}

# Aggiungi Spark al PATH
ENV PATH=$PATH:${SPARK_HOME}/bin

# Imposta variabili PySpark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di configurazione
COPY .env /app/.env
COPY requirements.txt .

# Aumenta il timeout per i download pip
RUN pip config set global.timeout 1000

# Installa le dipendenze
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install pyspark pymongo tweepy python-decouple requests python-dotenv openai vaderSentiment

# Assicurati che la directory sia accessibile
ENV PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python3.9/site-packages"

# Copia il resto dell'applicazione
COPY . .

# Crea directory per i template e static files
RUN mkdir -p templates static

# Esponi la porta
EXPOSE 5000

# Comando di esecuzione
CMD ["python", "-u", "app.py"]