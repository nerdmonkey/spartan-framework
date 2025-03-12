FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

RUN mkdir -p /home/glue_user/.aws /home/glue_user/workspace
RUN pip install pytest-cov

COPY ./storage/driver/mysql-connector-j-9.2.0.jar /home/glue_user/workspace/storage/driver/mysql-connector-j-9.2.0.jar

CMD ["spark-submit", "--jars", "/home/glue_user/workspace/storage/driver/mysql-connector-j-9.2.0.jar", "/home/glue_user/workspace/${SCRIPT_FILE_NAME}", "--JOB_NAME", "${JOB_NAME}"]
