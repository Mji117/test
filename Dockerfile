FROM ubuntu:latest
RUN apt update && apt install -y ffmpeg nginx

COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
