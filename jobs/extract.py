import os

from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

sc = SparkContext()
glueContext = GlueContext(sc)

logger = glueContext.get_logger()

app_environment = os.getenv("APP_ENVIRONMENT", "test")

logger.info(f"Currently in {app_environment} environment")
logger.info("Hello, from Spartan")
