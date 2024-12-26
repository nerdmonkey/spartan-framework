FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

RUN mkdir -p /home/glue_user/.aws /home/glue_user/workspace
RUN pip install pytest-cov

CMD ["spark-submit", "--JOB_NAME", "${JOB_NAME}", "/home/glue_user/workspace/${SCRIPT_FILE_NAME}"]
