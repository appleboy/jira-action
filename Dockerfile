FROM ghcr.io/appleboy/go-jira:0.5.0

COPY --chmod=755 entrypoint.sh /entrypoint.sh

USER 1001

ENTRYPOINT ["/entrypoint.sh"]
