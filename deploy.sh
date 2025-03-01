# Генерация токена приложения
token=$(echo $RANDOM|md5sum|head -c 20);
sed -i "s/app_key=.*/app_key=$token/" config.ini
echo "$token"