import os
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
glueContext = GlueContext(spark)

logger = glueContext.get_logger()

app_environment = os.getenv("APP_ENVIRONMENT", "test")

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

logger.info(f"Starting job: {args['JOB_NAME']}")
logger.info(f"Currently in {app_environment} environment")
logger.info("Hello, from Spartan Job!")

job.commit()
