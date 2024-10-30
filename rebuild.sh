git pull
docker build -t trading-app .
docker stop trading-container
docker rm trading-container
docker run -d --name trading-container -p 1521:1521 trading-app

# docker build --no-cache -t trading-app .