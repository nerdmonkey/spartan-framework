import os
import shutil

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Spartan DB to CSV - Local").getOrCreate()


if os.getenv("APP_ENVIRONMENT") == "test" or os.getenv("APP_ENVIRONMENT") == "local":
    DB_DRIVER = os.getenv("DB_DRIVER")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    connection_mysql_options = {
        "url": f"jdbc:mysql://{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "driver": DB_DRIVER,
        "user": DB_USERNAME,
        "password": DB_PASSWORD,
        "dbtable": "users",
    }

    df = spark.read.format("jdbc").options(**connection_mysql_options).load()
    df.show()
    df.coalesce(1).write.csv("./storage/core/users_temp", header=True, mode="overwrite")

    temp_dir = "./storage/core/users_temp"
    for filename in os.listdir(temp_dir):
        if filename.endswith(".csv"):
            os.rename(os.path.join(temp_dir, filename), "./storage/core/users.csv")

    shutil.rmtree(temp_dir)

else:
    connection_mysql_options = {
        "url": "jdbc:mysql://mysql:3306/spartan",
        "driver": "com.mysql.cj.jdbc.Driver",
        "user": "root",
        "password": "root",
        "dbtable": "users",
    }
