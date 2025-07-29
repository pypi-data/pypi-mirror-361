import os
import shutil

from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
from pyspark import SparkFiles
from pyspark.sql.types import StringType
from pyspark.sql import dataframe as spark_df
import pandas as pd 
from zipfile import ZipFile
from pathlib import Path

from abtranslate.translator.package import ArgosPackage, load_argostranslate_model
from abtranslate.utils.file_manager import extract_package
from abtranslate.utils.logger import logger

from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
from pyspark import SparkFiles

PACKAGES_PATH = "/tmp/abtranslate/packages/"
MODELS_PATH = "/tmp/abtranslate/model/"

# Pandas UDF
@pandas_udf(StringType())
def translate_column(column: pd.Series) -> pd.Series:
    import abtranslate.config.constants  # or wherever PACKAGE_DIR is defined
    task_id = os.getenv('SPARK_TASK_ATTEMPT_ID', str(os.getpid()))
    abtranslate.config.constants.PACKAGE_DIR = Path(f"/tmp/abtranslate/packages_{task_id}")
    
    # Fix: Use only the filename with SparkFiles.get()
    package_path = SparkFiles.get("model.zip")
    
    if not os.path.exists(package_path):
        raise Exception(f"Model path {package_path} doesn't exist")
    
    package = load_argostranslate_model(package_path)
    translator = package.load_translator(optimized_config=True)
    
    return pd.Series(translator.translate_batch(column.tolist()))

def translate_with_udf(model_path: str, spark_df: SparkDataFrame, input_column_name: str, output_column_name: str) -> SparkDataFrame:
    # Salin model zip ke lokasi kerja Spark
    if not os.path.exists(PACKAGES_PATH):
        os.makedirs(PACKAGES_PATH, exist_ok=True)
    
    dst_model_path = os.path.join(PACKAGES_PATH, "model.zip")
    shutil.copy(model_path, dst_model_path)
    
    spark = SparkSession.builder.getOrCreate()
    
    added_files = spark.sparkContext.listFiles
    if not any(dst_model_path in f for f in added_files):
        spark.sparkContext.addFile(dst_model_path)
    else:
        logger.info(f"Skip adding file to spark, file \"{dst_model_path}\" already exist")
    
    # Tambahkan kolom hasil translate
    df_translated = spark_df.withColumn(output_column_name, translate_column(input_column_name))
    return df_translated