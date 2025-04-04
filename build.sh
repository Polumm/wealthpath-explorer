# sudo systemctl stop postgresql # If you have native postgresql

docker-compose down
docker volume prune -f
docker-compose up --build
