# Hammer_pre-view
#### Django Проект: Реферальная система

Этот проект реализует систему рефералов с использованием Django и Django REST Framework (DRF). Функционал включает регистрацию, авторизацию, управление реферальными кодами и просмотр профиля.
На реплит устанавливаются зависимости при помощи poetry install
Запросы сохранены в postman: https://www.postman.com/testingfreaks2/just-fine/collection/z975t1g/hammer-systems?action=share&creator=40122653
Регистрация или вход
URL: /auth/register-login/
Метод: POST
Тело запроса:
{
    "phone": "+79999999999"
}


Ввод смс-кода
URL: /auth/verify-code/
{
    "phone": "+79999999999",
    "code": "1234"
}

Активация реферального кода
URL: /profile/
Метод: POST
Тело запроса:
{
    "invite_code": "ABC123"
}


Получение профиля
URL: /profile/?phone=%2B79999999991
Метод: GET
В запросе указывается номер телефона с "%2B", вместо "+" 
