docker build -t chatbot:v1 .
docker run -d -p 8080:8080 chatbot:v1