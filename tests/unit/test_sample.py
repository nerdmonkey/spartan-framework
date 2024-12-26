import os
import sys
from unittest import mock

import pytest

pyspark_mock = mock.MagicMock()
sys.modules["pyspark"] = pyspark_mock
sys.modules["pyspark.sql"] = pyspark_mock.sql
sys.modules["pyspark.sql.dataframe"] = pyspark_mock.sql.dataframe
sys.modules["pyspark.sql.SparkSession"] = pyspark_mock.sql.SparkSession
sys.modules["pyspark.rdd"] = pyspark_mock.rdd
sys.modules["pyspark.serializers"] = mock.Mock()

awsglue_mock = mock.MagicMock()
sys.modules["awsglue"] = awsglue_mock
sys.modules["awsglue.utils"] = mock.Mock()
sys.modules["awsglue.context"] = mock.Mock()
sys.modules["awsglue.job"] = mock.Mock()
sys.modules["awsglue.dynamicframe"] = mock.Mock()

sys.modules["awsglue.utils"].getResolvedOptions = mock.Mock(
    return_value={"JOB_NAME": "test_job"}
)

from jobs.extract import args, glueContext, job, logger


@pytest.fixture
def mock_sys_argv(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "--JOB_NAME", "test_job"])


@pytest.fixture
def mock_environment(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "test")


@pytest.fixture
def mock_getResolvedOptions(monkeypatch):
    monkeypatch.setattr(
        "awsglue.utils.getResolvedOptions",
        lambda argv, options: {"JOB_NAME": "test_job"},
    )


@pytest.fixture
def mock_spark_session():
    spark = mock.Mock()
    spark.builder.getOrCreate.return_value = spark
    return spark


@pytest.fixture
def mock_glue_context(mock_spark_session):
    glue_context = mock.Mock()
    glue_context.get_logger.return_value = mock.Mock()
    return glue_context


@pytest.fixture
def mock_job(mock_glue_context):
    job = mock.Mock()
    job.init = mock.Mock()
    job.commit = mock.Mock()
    return job


@pytest.fixture
def mock_logger(mock_glue_context):
    return mock_glue_context.get_logger()


def test_environment_variable(mock_environment):
    assert os.getenv("APP_ENVIRONMENT") == "test"


def test_getResolvedOptions(mock_getResolvedOptions, mock_sys_argv):
    options = sys.modules["awsglue.utils"].getResolvedOptions(sys.argv, ["JOB_NAME"])
    assert options == {"JOB_NAME": "test_job"}


def test_glue_context_logger(mock_glue_context):
    assert mock_glue_context.get_logger() is not None


def test_logger_messages(mock_logger):
    mock_logger.info("Starting job: test_job")
    mock_logger.info("Currently in test environment")
    mock_logger.info("Hello, from Spartan Job!")

    mock_logger.info.assert_any_call("Starting job: test_job")
    mock_logger.info.assert_any_call("Currently in test environment")
    mock_logger.info.assert_any_call("Hello, from Spartan Job!")


def test_job_initialization(mock_job):
    mock_job.init("test_job", {"JOB_NAME": "test_job"})
    mock_job.init.assert_called_with("test_job", {"JOB_NAME": "test_job"})


def test_job_commit(mock_job):
    mock_job.commit()
    mock_job.commit()

    assert mock_job.commit.call_count == 2


def test_missing_job_name():
    original_getResolvedOptions = sys.modules["awsglue.utils"].getResolvedOptions

    def mock_getResolvedOptions(argv, options):
        raise KeyError("JOB_NAME")

    sys.modules["awsglue.utils"].getResolvedOptions = mock_getResolvedOptions

    try:
        with pytest.raises(KeyError, match="JOB_NAME"):
            sys.modules["awsglue.utils"].getResolvedOptions(sys.argv, ["JOB_NAME"])
    finally:
        sys.modules["awsglue.utils"].getResolvedOptions = original_getResolvedOptions
