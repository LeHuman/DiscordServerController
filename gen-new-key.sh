#https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -sha256
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 36500 -out cert.pem -subj '/C=US/ST=IL/L=Earth/O=JoeMama/OU=IT/CN=www.koolkidz.club/emailAddress=isaiasr0205@gmail.com/'
