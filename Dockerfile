FROM ghcr.io/appleboy/go-jira:0.6.1

USER root
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

USER 1001

ENTRYPOINT ["/entrypoint.sh"]
