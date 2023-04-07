# Honeypot data server

ssh mnecas@192.168.0.99 -i keys/id_ed25519 -p 35695 -L 8000:localhost:8000

scp -i honeypot-data-server/keys/id_ed25519 -P 35695 -r honeypot-data-server/
mnecas@192.168.0.99:/home/mnecas/

firewall-cmd --zone=public --add-service=http

semanage permissive -a haproxy_t

python3 manage.py runserver
