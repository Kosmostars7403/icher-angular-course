run:
	mkdir -p static && docker compose --env-file .env up --build -d
stop:
	docker compose stop
