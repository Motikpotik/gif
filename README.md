# GiftGif — подарок Telegram в анимированную карточку (Hikka)

Анимированная карточка NFT-подарка Telegram в стиле приложения: узор и цвет
берутся со страницы подарка, модель анимируется, подпись «Название #номер».
MP4 или GIF, 40–60 fps, ~3 секунды.

## Установка

.dlmod https://raw.githubusercontent.com/Motikpotik/gif/main/giftgif.py

или как репозиторий:

.addrepo https://raw.githubusercontent.com/Motikpotik/gif/main
.dlmod giftgif

Зависимости: rlottie-python Pillow pilmoji imageio-ffmpeg>=0.5,<0.8
numpy не обязателен (нужен только .giftest).

## Команды

| команда | что делает |
|---|---|
| .gif | карточка подарка реплаем |
| .gif t.me/nft/ResistanceDog-3424 | карточка по ссылке |
| .gif 512 · .gif видео | размер и формат разово |
| .gif текст <свой текст> | своя подпись |
| .gif <ссылка1> <ссылка2> | пачка отдельными карточками (до 10) |
| .gif сетка <ссылки> | одна сетка плиток (до 9, 3×3) |
| .gifttext | текст подписи в конфиге |
| .giftest | самопроверка на трёх Ginger Cookie |
| .gifhelp | справка в чате |

## Конфиг

format (mp4/gif), size, fps, pattern, footer, caption, cache_minutes.
