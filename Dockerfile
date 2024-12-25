FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

RUN mkdir -p /home/glue_user/.aws /home/glue_user/workspace
RUN pip install pytest-cov

EXPOSE 4040
EXPOSE 18080

CMD ["spark-submit", "/home/glue_user/workspace/${SCRIPT_FILE_NAME}"]
