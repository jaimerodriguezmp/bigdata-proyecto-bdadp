#!/bin/bash
# Script para ejecutar el analisis Hadoop Streaming
# Requiere: Hadoop instalado y DATA_FILE en HDFS

DATA_FILE="car_sales.csv"
HDFS_INPUT="/user/$(whoami)/car_sales"
HDFS_OUTPUT="/user/$(whoami)/car_analysis"

ANALYSIS=${1:-avg_price_by_brand}

echo "=== Ejecutando analisis Hadoop: $ANALYSIS ==="

# Copiar datos a HDFS
echo "Copiando datos a HDFS..."
hdfs dfs -mkdir -p "$HDFS_INPUT" 2>/dev/null
hdfs dfs -put -f "$DATA_FILE" "$HDFS_INPUT/" 2>/dev/null

# Limpiar output anterior
hdfs dfs -rm -r "$HDFS_OUTPUT" 2>/dev/null

# Ejecutar Hadoop Streaming
mapred streaming \
    -input "$HDFS_INPUT/$DATA_FILE" \
    -output "$HDFS_OUTPUT" \
    -mapper "python3 mapper.py $ANALYSIS" \
    -reducer "python3 reducer.py" \
    -file mapper.py \
    -file reducer.py

echo "Resultados:"
hdfs dfs -cat "$HDFS_OUTPUT/part-*" 2>/dev/null

# Limpiar
hdfs dfs -rm -r "$HDFS_OUTPUT" 2>/dev/null
