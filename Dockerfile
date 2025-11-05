FROM ghcr.io/appleboy/go-jira:0.5.0

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER 1001

ENTRYPOINT ["/entrypoint.sh"]
