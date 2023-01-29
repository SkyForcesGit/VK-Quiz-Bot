# VK Quiz Bot

**VK Quiz Bot** – специальный бот для **ВК**, написанный на **Python** и созданный для организации и проведения разного рода 
викторин.<br>
Находится в стадии активной разработки и проектирования.

> **Требования:**
> - **Версия интерпретатора Python:** 3.10 и выше.
> - **Дополнительные библиотеки:** перечислены в *"requirements.txt"*.
> - **Подключение к Интернету.**

## Установка

> **ВАЖНО!** Ознакомьтесь с условиями лицензии перед началом установки и использования.

- Загрузите архив со всеми файлами бота и распакуйте в удобной вам директории.<br><br>
- Перейдите в каталог с файлами бота, откройте его в **Терминале** и выполните установку библиотек из *"requirements.txt"*:
  ```shell 
  pip install -r requirements.txt
  ```

- **Отлично, установка выполнена, теперь можно переходить к настройке бота.**

## Настройка бота

Чтобы начать работу с ботом, необходимо создать сообщество **ВК** (*если у вас его нет*) и подготовить его
определенным образом, а затем произвести настройку некоторых конфигурационных файлов.

### Создание и подготовка сообщества

- Создайте сообщество **ВК**. **Если оно уже у вас есть, переходите к следующему пункту.**
  Перейдите в меню сообществ, выберите *"Создать сообщество"*, а затем следуйте инструкциям от **ВКонтакте**.<br>
  ![CreateCommunity](/assets/readmes/create_community.png)<br><br>

- Перейдите в настройки вашего сообщества, в пункт **"Сообщения"** и включите опцию **"Сообщения сообщества"**.
  **Сохраните изменения.**<br>
  ![EnableCommunityMessages](/assets/readmes/enable_community_messages.png)<br><br>

- Перейдите в пункт **"Настройки для бота"** и включите опцию **"Возможности ботов"**. **Сохраните изменения.**<br>
  ![EnableBotOpportunities](/assets/readmes/enable_bot_opportunities.png)<br><br>

- Перейдите в пункт **"Чаты"** и создайте новый (*если, конечно, вам это нужно*).<br>
  ![CreateChat](/assets/readmes/create_chat.png)<br><br>

- Перейдите в настройки вашего сообщества, в пункт **"Работа с API"**, в пункт **"Long Poll API"** и включите данную опцию.<br>
  ![EnableLongPoll](/assets/readmes/enable_longpoll.png)<br><br>

- Перейдите в **"Типы событий"** и отметьте следующие пункты:
  > **Сообщения:**
  > - Входящее сообщение
  > - Исходящее сообщение
  > - Редактирование сообщения
  > - Действие с сообщением
  > - Разрешение на получение
  > - Запрет на получение
  > - Статус набора текста<br><br>
  > 
  > **Фотографии:**
  > - Добавление<br><br>
  > 
  > **Аудиозаписи:**
  > - Добавление<br><br>
  > 
  > **Видеозаписи:**
  > - Добавление<br><br>
  > 
  > **Прочее:**
  > - Изменение настроек

  ![GetPermissions](/assets/readmes/get_permissions.png)<br><br>

- Перейдите в пункт **"Ключи доступа"** и выберите **"Создать ключ"**. Отметьте галочкой **первые четыре пункта**, а
  дальше следуйте инструкциям **ВКонтакте** по созданию ключа доступа. Скопируйте полученный ключ и сохраните куда-нибудь.
  > **ВАЖНО! НЕ ДАВАЙТЕ ЕГО НИКОМУ!**
  > 
  ![CreateToken](/assets/readmes/create_token.png)<br><br>

- **Отлично! А теперь напишите что-нибудь своему сообществу.** После того как сделаете это, перейдите в сообщения сообщества
  и посмотрите в адресную строку – видите набор цифр после **"gim"**? Эти цифры – **ID вашего сообщества, запишите их куда-нибудь**.<br>
  ![GetGroupID](/assets/readmes/get_group_id.png)<br><br>

- А теперь перейдите в диалог с собой и снова посмотрите в адресную строку – видите набор цифр после **"sel="**? Эти цифры
  – **ваш ID, запишите и его тоже**.<br>
  ![GetYourID](/assets/readmes/get_your_id.png)<br><br>

- Перейдите в созданную вами беседу сообщества и снова загляните в адресную строку – видите набор цифр после **"sel=c"**?
  Эти цифры – **ID вашего чата**, запомните и его. Скорее всего, у вас этот **ID** будет равен **1**.<br>
  ![GetChatID](/assets/readmes/get_chat_id.png)<br><br>

- **Отлично, вы великолепны, сообщество подготовлено.**

### Конфигурация бота

Сейчас мы можем перейти к настройке самого бота. Для этого нам нужно настроить под себя несколько конфигурационных файлов.
Обратите свой взор на файл **"CONFIGS_README.md"** – он расскажет и покажет вам, как устроены конфигурационные файлы бота.
Ознакомьтесь с ним и заполните конфигурационные файлы в соответствии с инструкциями и имеющимися у вас данными. 

> **ВАЖНО!** Обязательно вставьте все полученные вами ранее значения в соответствующие формы **"bot_config.json"**.

**Отлично! Если вы все сделали правильно – бот готов к работе!**

## Команды бота

Данный пункт познакомит вам с основными командами для управления ботом. Их не так много, потому что процесс в основном
автоматизированный.

> **ВАЖНО!** Список команд может изменяться и дополняться в будущем.

**Консольные команды:**
- *"/rem_arcs"* – данная команда удаляет все архивы с логами от прошлых сеансов.<br>
  ![RemArcs](/assets/readmes/rem_arcs.png)<br><br>

- *"/exit"* – данная команда инициирует завершение работы бота.<br>
  ![Exit](/assets/readmes/exit.png)<br><br>

**Команды чата:**
- *"/get_chat"* – данная команда инициирует сбор данных об участниках беседы, определяет среди них
  администраторов. В **первый раз** может быть выполнена кем угодно, **после** – только администратором.<br>
  ![GetChat](/assets/readmes/get_chat.png)<br><br>

- *"/start"* – данная команда запускает цикл викторины. **Может быть вызвана исключительно администратором.**
  После начала цикла данная команда более не может быть вызвана.<br>
  ![Start](/assets/readmes/start.png)<br><br>

- *"/kick_all"* – данная команда исключает из беседы всех пользователей за исключением
  администраторов. **Может быть использована только администратором.**
  ![KickAll](/assets/readmes/kick_all.png)<br><br>

- *"/kick"* – данная команда исключает указанного пользователя. Чтобы выбрать пользователя,
  ответьте на его сообщение. **Администраторов исключать нельзя. Команда доступна только администраторам.**
  ![Kick](/assets/readmes/kick.png)<br><br>