🇺🇸 An English version of this README is availabe here: https://github.com/FluffyKn1ght/Titleify/blob/main/README.md

# Titleify
Конвертер видео в Minecraft Java 1.20+ /title. Работает на Python и FFmpeg.

## А на этом запустится Bad Apple?
Очень старый, но важный вопрос, так что отвечу на него здесь, сверху. **Да, запустится, вот пруф:** [Тык!](https://www.youtube.com/watch?v=enCyQBkFMSw)

## Как это работает?
Titleify использует функцию ресурпаков Minecraft под названием "Bitmap-шрифты". Эта функция позваляет игрокам менять любой символ в игре на PNG-картинку. Размер, увы, ограничен - 256x256, но этого должно хватить для почти всех видео.

Titleify использует FFmpeg, чтобы вытащить из входного видео все кадры, попутно меняя FPS на 20 (максимум майнкрафта) и ограничивая разрешение на 256x256 (c сохранением соотношения сторон). Затем скрипт генерирует ресурспак и датапак, при совместном использовании которых можно увидеть любое видео в Minecraft в **реальном времени!**

## Как этим пользоваться?
**Примечание:** Скрипт работает на Minecraft *JAVA EDITION*, а если быть точнее, то на 1.20+ (поддержка более старых версий не гарантируется).

Чтобы использовать Titleify, скачайте скрипт, распакуйте его куда-либо, и перетащите на него любой видеофайл.

*Или, если вы пользователь терминала, напишите python titleify.py <путьКВашемуВидео>*

## У меня вылезает ошибка конверсии!
Попробуйте другой формат видео, или другое видео.

## При заходе в мир видео начинает играть без звука
Вырубите датапак, и врубите его снова.

## У меня вместо видео квадрат!
Вы не применили ресурспак! (Он может долго применятся)