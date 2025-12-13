FROM stain/jena-fuseki:latest

USER root

# Set Render port
ENV PORT=3030

# Expose the port
EXPOSE 3030

# Copy custom entrypoint script to bypass shiro.ini issues
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Override the default entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"] 
