# # If you have native postgresql
# sudo systemctl stop postgresql

docker-compose down
docker volume prune -f
docker-compose up --build
