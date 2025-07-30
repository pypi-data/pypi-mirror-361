from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def init_spark(app_name="SAZ Spark App"):
    return SparkSession.builder.appName(app_name).getOrCreate()

def spark_schema(df_spark):
    df_spark.printSchema()

def spark_cardinality(df_spark):
    for col_name in df_spark.columns:
        print(f"Cardinality of {col_name}:")
        df_spark.groupBy(col_name).count().show()

def spark_save_csv(df_spark, path, mode="overwrite"):
    df_spark.write.mode(mode).option("header", True).csv(path)
