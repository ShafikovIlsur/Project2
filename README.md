Главная страница выглядит следующим образом:
![изображение](https://github.com/user-attachments/assets/3ed8f289-9bc7-4eea-90fc-167326e3066a)

Принцип работы:
Пользователь вводит название стартового города и конечного, после чего получает информацию о погоде в этих города и оценку погодных условий

Пример работы:

![изображение](https://github.com/user-attachments/assets/77872d35-f1f2-46ce-8749-2c78942c8d0b)

Если пользователь ничего не вводит, то он получает следующую ошибку:

![изображение](https://github.com/user-attachments/assets/2f9f7a74-6fd3-4a61-8d98-06b6945a1cd2)

Если пользователь вводит несуществующий город или город, координаты которого отсуствуют в базе данных Яндекс.Карты, то он получает следующую ошибку:

![изображение](https://github.com/user-attachments/assets/378289cd-68eb-4a68-a940-cbf6f972aee4)

Ошибки, которые могут возникнуть не по вине пользователя:
1) Произошла ошибка HTTP: Превышен лимит по запросам к AccuWeather API - возникает при превышении лимита по запросам к AccuWeather API
2) Что-то пошло не так. - возникает при неудачном запросе к Яндекс.Картам
3) Ключ локации не найден, проверьте корректность координат. - возникает при отсуствии ключа в ответе от AccuWeather API
