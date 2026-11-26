# ◇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◇
# meta developer: @n3post
# scope: Heroku, Hikka
# version: 1.4.25
# author: n3
# Description: Подарок Telegram → анимированная карточка GIF или MP4.
# Собирает ту же карточку, что показывает приложение: градиентный фон,
# узор-силуэт подарка, анимированная модель, название и номер.
# Геометрия, шрифт (Roboto Medium) и тайминг сверены по эталонным роликам:
# плитка 81% ширины кадра, модель 49% ширины плитки, 60 fps, 3.00 с.
# Анимацию берёт из самого Telegram (application/x-tgsticker со страницы
# t.me/nft/<slug>-<номер>), фон и узор — из SVG той же страницы.
# Команды: .gif — реплаем на подарок или ссылкой · .gif 512 · .gif видео
# .gif текст <свой текст> — подпись под карточкой (эмодзи тоже рисуются)
# 1.4.5: фон рисуется нативно, без cairosvg/libcairo и без скачивания
# узора — это снимает 4 пакета и один запрос, установка не упирается в диск.
# 1.4.6: узор снова по калиброванной раскладке app-square (21 метка на всю
# плитку, нижний ряд включён) — в 1.4.5 низ плитки оставался пустым.
# 1.4.9: команда .giftest — проверка на трёх печеньках: узор по третям,
# габарит модели, живая ли анимация, плюс скриншот кадра в чат.
# 1.4.25: прямой sendMedia теперь действительно работает. random_id брался
# из беззнаковых 64 бит, а в MTProto это знаковый int64 — struct.pack('<q')
# падал с «'q' format requires …», и КАЖДАЯ гифка с 1.4.20 уходила резервным
# путём (видно в логах: «gif: sendMedia не удался»). Теперь маска 2^63-1.
# 1.4.24: главный баг гифки с 1.4.17 — normalize_fmt("animation") превращал
# режим анимации в mp4, поэтому гифка собиралась СО звуковой дорожкой, а с
# ней Telegram обязан показывать видео с плеером. Теперь .gif gif / format:gif
# дают mp4 без звука (1 поток) и уходят через sendMedia с Animated.
# 1.4.23: качество. Главное — .gif diag рендерил карточку в 256 px, и клиент
# растягивал её вчетверо («шакальное»); теперь размер как у обычной сборки.
# Кодировщик: -tune animation и crf 10 для гифки, 14 для видео (было 16):
# yuv444p дал бы заметно чище, но это профиль High 4:4:4 — мобильные
# декодеры его не проигрывают. В статусе подсказка, если размер < 768.
# 1.4.22: диагностика доступна из уже работающей команды — .gif diag
# (отдельная .gifdiag могла не зарегистрироваться после обновления, и это
# ничем не отличалось от «команда не работает»). .gif без подарка и с
# непонятным текстом показывает справку с номером версии — сразу видно,
# обновился ли модуль. Версия вынесена в MODULE_VERSION и печатается в
# статусе и справке.
# 1.4.21: у гифки нет звуковой дорожки вообще (-an): даже пустая дорожка
# делает из неё обычное видео. Новая команда .gifdiag — показывает, каким
# путём ушёл файл, что сохранил сервер и что видит клиент, вместо догадок.
# 1.4.20: гифка уходит прямым запросом messages.sendMedia, а не через
# send_file: раньше DocumentAttributeAnimated до сервера не доходил, и любой
# mp4 показывался видео с таймером (все правки 1.4.16–1.4.19 лечили симптомы).
# Запрос собирается как в pyrogram: video + filename + animated, mime
# video/mp4, без nosound_video. Если прямой путь не сработал — откат на
# send_file и запись причины в лог, чтобы не гадать по скриншотам.
# 1.4.19: возврат к 1.4.17: nosound в атрибуте и nosound_video в send_file
# убраны — с ними клиент показывал видео с таймером и иконкой звука.
# Размеры и длительность по-прежнему настоящие, из самого mp4.
# 1.4.18: плеер вместо гифки — не хватало флага nosound в
# DocumentAttributeVideo: без него клиент считает mp4 обычным видео и рисует
# кнопку play. Теперь nosound=True (+ nosound_video в send_file), а размеры и
# длительность берутся из самого mp4, а не из догадки 512×512×3.
# 1.4.17: .gif отдаётся как гифка Telegram — mp4 без звука с атрибутами
# video+animated. Настоящий .gif iOS показывает файлом со стрелкой «скачать»
# (баг клиента, bugs.telegram.org/c/577), а mp4-анимацию крутит сам.
# Заодно: ffmpeg-ошибки больше не прячутся за «Broken pipe», сетка не теряет
# имя файла (grid.animation → grid.mp4).
# 1.4.16: gif снова гифка, а не файл. hikkatl в get_attributes не ставит
# DocumentAttributeAnimated, поэтому Telegram показывал .gif документом
# (стрелка «скачать», без автоплея). Теперь атрибуты анимации передаются
# явно; mp4 не тронут.
# 1.4.15: отправка починена по исходникам Hikka: файл с подписью идёт
# через utils.answer_file / send_file, а не message.respond(file=…,
# caption=…) — тот путь уходит в send_message и падал с «unexpected
# keyword argument 'caption'». Если клиент не принимает подпись к видео,
# видео уходит без неё, подпись — отдельным сообщением.
# Кадр больше не тянет фиксированную высоту ASPECT: обрезается по низу
# фактической подписи, пустой полосы под коротким названием нет.
# Кеш готовых карточек ограничен по памяти (файл 12 МБ, всего 48 МБ).
# say() при повторе без разметки больше не срезает теги эмодзи в пустоту.
# 1.4.14: в справке команда проверки называлась .gifтест — опечатка,
# теперь .giftest. У эмодзи shield document_id был из 16 цифр (у остальных
# 19) — id не подтверждён, поэтому оставлен обычный символ 🛡: иначе
# сообщение с ним просто не отправится.
# 1.4.13: реплай + размер (.gif 512) больше не считается подарком
# «slug-512»: число в 64…1536 — это размер карточки, номером подарка оно
# не считается (номера почти всегда вне этого окна).
# 1.4.12: сообщение «Собираю карточку…» удаляется после отправки файла;
# mp4 пишется с пустой звуковой дорожкой, иначе Telegram показывает его
# как GIF (значок GIF, маленькое превью) даже при format: mp4.
# 1.4.11: узор берётся со страницы подарка (#giftPattern), а не из вшитого
# силуэта печеньки — у каждого подарка и даже у каждого номера он свой.
# Фон — радиальный градиент, как в SVG карточки (был линейный).
# 1.4.10: аудит перед публикацией — numpy больше не обязателен (без него
# молчит только .giftest), узор без альфа-канала не ломает рендер, битый
# подарок в пачке больше не обрывает всю сетку, две сборки разом (у двух
# людей) встают в очередь, а не ломают друг друга.
# 1.4.8: команда .gifhelp — вся инструкция с премиум-эмодзи (document_id
# взяты из живых модулей Hikka; если клиент их не примет, say() отправит
# текст без тегов, а не упадёт).
# 1.4.7: пачка подарков — реплай на сообщение с несколькими подарками или
# список ссылок: по карточке на подарок (до 10) либо .gif сетка (до 9 плиток
# в одном видео). Страница подарка запрашивается с повтором: Telegram иногда
# отдаёт урезанную заглушку вместо карточки.
# Legacy-раскладка SVG 420×280 сохранена в ядре как svg-cover.
# Модель: нативный rlottie с запасом вокруг холста.
# Roboto Medium и emoji 🎄🎅 встроены: один .py без папок ресурсов.
# requires: rlottie-python Pillow pilmoji imageio-ffmpeg>=0.5,<0.8
# Фон рисуется нативно (радиальный градиент, силуэт узора, суперэллипс);
# cairosvg и libcairo не нужны, узор не скачивается — только .tgs.
# Требует: rlottie-python, Pillow, pilmoji (цветные эмодзи в своей
# подписи); для MP4 — ffmpeg или imageio-ffmpeg (иначе отдаёт GIF).
# ◇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◇

from __future__ import annotations

import asyncio
import base64
import contextlib
import zlib
import gzip
import io
import itertools
import json
import logging
import math
import os
import re
import subprocess
import shutil
import tempfile
import time
from pathlib import Path
import urllib.request
from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageDraw, ImageFont

try:
    from .. import loader, utils
except Exception:  # pragma: no cover
    loader = utils = None


MODULE_VERSION = "1.4.25"

INT64_MAX = 0x7FFFFFFFFFFFFFFF       # random_id в MTProto — знаковый int64


def _random_id() -> int:
    """Случайный random_id в пределах знакового int64.

    `int.from_bytes(os.urandom(8), "big")` может дать число больше 2^63-1, и
    struct.pack('<q') падает с «'q' format requires …» — из-за этого в 1.4.20
    прямой sendMedia не срабатывал никогда и гифка уходила резервным путём.
    """
    return int.from_bytes(os.urandom(8), "big") & INT64_MAX

logger = logging.getLogger("giftgif")


def esc(text: Any) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


# Self-contained assets from the supplied case: Roboto Medium latin+cyrillic.
# Twemoji graphics: Twitter, Inc. and contributors, CC-BY 4.0.
# https://github.com/jdecked/twemoji/tree/v16.0.1
# https://creativecommons.org/licenses/by/4.0/
_EMBEDDED_ROBOTO = zlib.decompress(base64.b64decode(
    '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'
    'P/IP8D/i8CkgImBnwQcCXQI7Bb4MrA50G9g44HBwUnB39d27X2/jpRdRrX6RXiEhIWMjRkZ8hrQ7ZhueHfoe6hUaFDQ1eH3gl9EEbCgsMSw7YZ'
    'VcZ045m6urp54SnhxyO0EQsjfoqwRS6qF1avb7019W45/t2r91t9z/qm+l3q968/qv7b9U/Vv1b/twaqBgENohscaOjeMKxhQcM7UdOjOfg3Lv'
    'p09K+N4hrtbPTA1Na00/RlTN+YkzHXY36M+TPWNTYoNi62dWzf2Amxm2N3wL/9cbXj4uM6xA2NmxpXFLc1bl/cubhv456ZXcwh5kRzJ/MI83Tz'
    'CvP75o/MX5ofxpN4n/iG8a3i+8VPil8Q/1b8ofiL8Xfjf0vACd4J9RNSEnoljEtYkLApYX/C+YSbCQ8TyhN9EhsmNk/skZiVODtxbeKuxIuJ1x'
    'JvJd5N/DnxSeKLRClJlVQrqeK/nkmFSSeTvkp6mPSysXfj2MY9Gi9tfKjxucY/Nn7exNRkSJPZTbY3KWliTU5M7pU8PXlD8s5kMfly8u3kR039'
    'mnZsurjpsaZ3m75oZmjWrtm0ZmKzS80eNvds3q35mOZLm29vfq75oxaBLVJaTGtxtMW9lnVadmyZ2XJRy+KWv7a0pQSnNEvpmzIxZX7Kmyn3Uv'
    '5K9Us1pXZOnZq6NfVc6h9p9dO6pS1MO5L2uFVwq/RWma0mt1rU6lKr+61+b2VNb5Kemt4p/Y30zPQx6Tnpc9IXpS9PfzP93fQ96cXpx9PPpl9O'
    'v5H+bfr36b+m/55uzRAyPDOaZrTK6JDRK2NoRlbG5Iy5GQUZazLeydiTcSTjbMbnGY9bu4F2A3oOVw/WDodUYNt7IC80QfTQaLW6JhYPjQWV0L'
    'OKnV3Z2bMEWVBGHwsxBRUTQ4u+7AbBDdK06CvyBMEvRUG+qOWLC7tY3O6IHvIDT/kB0Vhq3YmJDQ3VhnJajLWYC8UJOJSrZ21GLiRKT6QT2OMn'
    'wkkSJlarYHm9Q1Bb55DpZVqSax1IBhaSgYiglbbneDuD3xM1E1W1vGjPKo0F1wSnB9x4AJzFKk+LW8M+od8E/dEXWlqwKSYWG+H18Ylxfr4+qr'
    'AIPPeGHiPpVfv89m0XtsUHeO71+SYdOjRJat+euiVGcH+QFBX1J7micPlFHPTNhcGLSAm81KIusahNFk5jcSmxuNDuOaPWLNAT9jYuO4ij4SRM'
    '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'
    '+Er8TewQX4udGEFUOzLX/wSxd61V'
))
# Силуэт узора 128×128 из альфа-канала WebP #giftPattern (нужен только
# канал прозрачности: цвет задаёт flood-цвет SVG). Вшит, чтобы фон не
# зависел от скачивания картинки и от cairo: один .py — всё внутри.
_EMBEDDED_PATTERN = zlib.decompress(base64.b64decode(
    "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"
    "AElFTkSuQmCCOJl/xA=="
))

_EMBEDDED_EMOJI = {
    '1f384': base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcExckTvWM0NfkjtYjTdYjTdckTtgjjZckTtckTtmIRP/rDNbkDo+ch'
        '3/rDNckTtAdB9IfSdmIRP/rDM+ch1mIRNmIRNmIRNmIRNckTv/rDP/rDNgXylCdiH/rDNmIRPdLkTJozZckTs+ch1MgSpGeiTdLkT/rDNThzJX'
        'jDaMnTxnlT7/zE2byn3owkim04h3ZDDKOEBBdSCcXz/VvEdigyZmIRNypVLDP0DPpDV6kjGrnjdhWSeOUDFkPh1SfyiBG0V1AAAAInRSTlMA7/'
        'xsQCrPEJ+6QGCAiobfqdNkMGTPEDC/j++q5++/n1CP6OF9vgAAAvBJREFUeF7NlteSmzAUhsEGg2yvy/ae5EiiuZbtJXn/t4pQWdCyDkLsRb4b'
        'j2eYTzqc/0g4JowGzrdwFF8G3yK6jePRd3gGcRxfHrWtajC6inMuR4NWrrjMVQvRqCxq1bur1h7Fre6x55cSddt5/Fclcv02nsB9VqKXXtDC0w'
        'Mmes0ypssA2YsQQPY6A0b2zH5CW08IGramAEGFsNV+UkpTkNiE4AI4CcUMkgBnaCE6oISQ3LJNyJa5+N9jC9EEc7YEGEzFObAJ0ZQQkqQgSQlj'
        'atv82d18fjeDgq6dB5iHmcDapDww58xso6Q8SvSHQImLRiIQLHlpeQKgwGZHL8y0vBcp2HWiqLNrnMkJJYRSjO+ZhvMUcZ4mDWONJSLZGL9Hkv'
        'dmmcQFlKexo0Sdm0apvlEW1bDog2mzIzZNCElkr3QRhE08FYrSAFBgKJIe7WDbKdEOwPQa8LjgcbFaLR4BgIizRLWfuz0jkc89K86jPIiKQHJ8'
        'wy0hFxZCtCjnSb59F3mOIccYryT4C47NY62LCLEz+ZhRlEYTgGSrm3yzrmEGCBEwDUdXeWZxJNzE25+W4kSo8pBeYBbrNBEXSIUkITO+QL3JH8'
        'N+inzVmnwXqhBSiFQTYByYj1lx+RdfEStJzcB5FU2aZ4gf3dknEdSOmb6b3DPnZFpp4P47Q+P1Joo2a+Ctk9lZCtGSDdvHMAOqCeXPiLOmpQDO'
        'JXxyeb5m09psy5NwoyS6qGBS0/4gkgiFXhouU3MHTKqiLcmE6EU5DL65hnijlyYilOXtZx6d7n5PmOK1fNlKk2hJ0IB9piAEoFi0XxaV6tnUjh'
        'Ky91sJiYXF05Qoi+6iVKyRb3WP6QIs+KK6AGxwa+bVnKooqJxEY4Su335/8HaNUOWZnlPFD6XKRWjY9fgwPZQ54U95wyFCaqlw36B4nqfJHzQ+'
        'Peo7xvQrIg1rUd9adPjfic500aljzXnZ88Ox5/Sk8JyfOm04lKrzQ6c1Z/3+Wa3gL0wyGP2TtahcAAAAAElFTkSuQmCC'
    ),
    '1f385': base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEzt7u7/3F3q6+zdLkTr7e3x8vLm5+js7e3p6uvm5+jr7OzdLkTm5+'
        'jm5+jdLkT/3F3dLkTm5+jdLkTdLkTdLkTm5+jdLkTx8vL/3F3l16HdLkT5vVj/3F3dLkT/3F3R09TdLkTdLkT/3F3m5+jR09RmIRO3dV793Wnw'
        '47L434Ts5cyzfzjt25X63nfkV03l16DDkoHbqV7o5t/5vFjz4qPd1ba9g2/ym1TswcfUqrDdLkTx8vLib33t7u7r49lTyLOYAAAAI3RSTlMAxu'
        '/qK2XPvyAQ31kQpkCAz1yGQHCPMKLvMN/vVb/Pn7+/3yhZ0xUAAAKdSURBVHjatdZrW9owFMDxg6VIpYVxl6E4SNReRBzgbSny/b/VCM1STw0j'
        'nHW/Nz5PW/62pykUDvO7vdZ0Oha52bTfrsJJqu3hTJjN+lXrSl9HzCZtOM7vTcRxs+6xTGss7Ax9egabHB5VdyZOMT5U6guEWvLljKkl3CGY+P'
        'QONoSCqSBqA9ITVDN8YWNB1sInRDf2IVeYNH1KAqFPyRf/pAqZhpMSbDc61FedlGhTuDaHGtoWri0l06FeWaFhWaFJWSFR1rBFt4zbnz8ljQ9K'
        '5mPz9RvgVmFWbhXxP0LDskLTLPQj2/PCrLxkR/8yhNxs15xZmWdHbwyherYrZFbC7OiFITT6jk/o4e7ugSl4W35KT2y9KIZGZ+xJ7tHudhiCtu'
        'mjF4XQN5axCGFrHLpi1BBboNANPfSGVvYZPcRQiJUQaqOQ1e3H0PcRI8EhKCk0hmzYZGu0Hm8Y2Rv6zb5iZAv9A5k/ImH8yKw9xiF6RLrq4ZdT'
        'Sjjfxgxb3u8tGRZvOU92f8+uiu81o2sWciliyL2CNoYRlxi7HukXPch5fC8Jj4XChO+B1N68pzvvLuS4obR8/bnzusSdPFSvpUqtrkMVntnqmc'
        'fRKtu0imI95S3PVGTnMtUudWngcOU5lP95rj6i8nM1HsUZAEAt/aQGfzS4lkTyZLBVFCVcawCAmyJ6TgE/QSCHgUMVUM45EsWPnxdgxJFzw3sV'
        'KC7usAJccgG8QyHvAk03/rqacxeeMaQMUIknz3Go1k78nHDUGYDp0jSPW6oDmIad45ZAMtx+LbC/92BYkLkmt9IEyfiI5KvbQgMU/NBi9cDhf+'
        'UE6CNuZT9nFwy8I/fLnsMPcuAUHX5QBwglWgfzmp1OoxlwLWhKHhANOhVZqQQDsPEbhunlEkGiKuMAAAAASUVORK5CYII='
    ),
}

# Telegram отдаёт полноценную страницу подарка не всем клиентам: с
# «X11; Linux» примерно каждая четвёртая попытка приходит урезанной
# заглушкой на 9 КБ без .tgs. Поэтому UA как у настольного Chrome и
# несколько попыток с разными заголовками.
UA_POOL = (
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                   "Version/17.0 Safari/605.1.15"},
    {"User-Agent": "TelegramBot (like TwitterBot)"},
)
UA = UA_POOL[0]

COMMAND_WORDS = frozenset({
    "gif", "гиф", "гифка", "видео", "video", "mp4", "сетка", "grid", "коллаж",
    "статус", "status", "?", "текст", "убрать", "сброс", "clear",
})
SIZE_MIN, SIZE_MAX = 64, 1536       # сторона карточки, px (.gif 512)
MAX_BATCH = 10                     # сколько карточек собирать за одну команду
MAX_TILES = 9                      # максимум плиток в сетке (3×3)
BATCH_DELAY = 1.0                  # пауза между отправками, секунды
CARD_W, CARD_H = 420, 280
GRID_GAP = 0.03                    # зазор между плитками в сетке
GRID_MARGIN = 0.03                 # поле страницы сетки          # координаты SVG карточки Telegram
CARD_RADIUS = 46                   # скругление «плитки» в приложении
PAGE_BG = (16, 16, 16)             # тёмный фон вокруг карточки
MODEL_INSET = 0.61                 # холст модели; видимое тело = 47.5% плитки
# Замеры с эталонного ролика 784×920 (плитка 638 px):
TILE_WIDTH = 0.8139                # плитка / ширина кадра
ASPECT = 1.1735                    # высота кадра / ширину
TILE_TOP = 0.0777                  # отступ сверху / высоты кадра
NAME_CAP = 0.0540                  # высота заглавной названия / ширины плитки
NUMBER_CAP = 0.0380                # номер (мельче названия)
AUTHOR_CAP = 0.0172                # подпись автора
NAME_GAP = 0.075                   # плитка → название
NUMBER_GAP = 0.060                 # название → номер
AUTHOR_GAP = 0.038                 # номер → автор
CAPTION_CAP = 0.032                # кегль своего текста
TEXT_STACK = 0.115                 # от верха плитки до строки «автор/свой текст»
SQUARE_MODEL_INSET = 0.6155        # body width calibrated against 8851
SQUARE_MODEL_DY = -0.006           # square 8851: body centre y ≈ 0.477
MODEL_DY = -0.030                  # сдвиг модели по вертикали, доля плитки
MODEL_PAD = 0.12                   # запас вокруг кадра Lottie: модель
                                   # вылезает за 512 и раньше резалась
PATTERN_BOOST = 1.00               # исходная прозрачность SVG, без усиления
TEXT_GAP = 0.021                   # зазор между названием и номером
GRAD_TOP, GRAD_BOTTOM = "#6c9edd", "#5c6ec9"   # стопы из SVG Telegram
GRAD_SHIFT = (-4, 0, 1)            # поправка под рендер приложения (замер)
PATTERN_RGB = (0x12, 0x39, 0xa2)
PATTERN_ALPHA = 0.20               # средняя прозрачность в SVG
BASE_MARK = 100                    # <image width=100 height=100> в SVG
RADIAL_R = 0.6965                  # r="69.65%" из radialGradient (доля меньшей стороны)
PATTERN_GAIN = 1.22               # множитель размера метки: замер по IMG_8877
                                   # (покрытие по третям сходится с приложением)
                                   # сверено с плиткой в приложении)


# Normalized motif centres / sizes / opacity, measured from app_card_8851.
# This is a calibrated square-card profile, not the rectangular SVG's lattice.
# Keep it separate: stretching/repeating the 420x280 viewBox is not equivalent.
SQUARE_PATTERN_SPOTS = (
    (0.217346, 0.004801, 0.095502, 0.153366),
    (0.498945, 0.033132, 0.092167, 0.216002),
    (0.782023, 0.004807, 0.095501, 0.155126),
    (0.317400, 0.150328, 0.120370, 0.222858),
    (0.678638, 0.151802, 0.120397, 0.222539),
    (0.022000, 0.196000, 0.096000, 0.155000),
    (0.978000, 0.196000, 0.096000, 0.155000),
    (0.181353, 0.291079, 0.095377, 0.219557),
    (0.817783, 0.291050, 0.095197, 0.219311),
    (0.115508, 0.481714, 0.132913, 0.225252),
    (0.881112, 0.482535, 0.134446, 0.225086),
    (0.002093, 0.670301, 0.093999, 0.156008),
    (0.998084, 0.670440, 0.096290, 0.159052),
    (0.203282, 0.755457, 0.111121, 0.222788),
    (0.794572, 0.753880, 0.110541, 0.221525),
    (0.498897, 0.874323, 0.098530, 0.218100),
    (0.325292, 0.910353, 0.092161, 0.163350),
    (0.674127, 0.910358, 0.092201, 0.164187),
    (0.075000, 0.912000, 0.094000, 0.153000),
    (0.925000, 0.912000, 0.094000, 0.153000),
    (0.499170, 1.008728, 0.095164, 0.158498),
)


def fetch(url: str, timeout: int = 40, headers: dict | None = None) -> bytes:
    request = urllib.request.Request(url, headers=headers or UA)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


# ════════════════════════════════════════════════════════════════════════════
# §1. СТРАНИЦА ПОДАРКА
# ════════════════════════════════════════════════════════════════════════════


@dataclass
class Card:
    """Всё, что нужно для карточки, собранное со страницы t.me/nft/…"""

    slug: str
    name: str
    number: int | None
    tgs_url: str
    pattern_url: str | None
    gradient: tuple          # стопы: hex-строки или RGB-кортежи
    pattern_spots: list          # [(x, y, opacity, scale)]
    pattern_color: tuple[int, int, int]
    svg: str = ""                # SVG карточки со страницы (точный фон)
    author: str = ""             # @автор коллекции, как в приложении
    caption: str = ""            # свой текст под номером (из команды)
    pattern_layout: str = "app-square"  # calibrated square card; svg-cover is legacy
    blue: bool = True            # синий фон (как в приложении) или свой


def resolve_slug(raw: str) -> str:
    """`89402`, `t.me/nft/x-89402`, `gingercookie-89402` → slug страницы."""
    text = str(raw or "").strip()
    match = re.search(r"t\.me/nft/([A-Za-z0-9_-]+)", text)
    if match:
        return match.group(1)
    if re.fullmatch(r"\d{1,9}", text):
        return text                     # t.me/nft/<номер> тоже работает
    return text.strip("/").split("/")[-1]


def parse_card(html: str, slug: str) -> Card:
    """Разобрать страницу подарка: анимация, узор, градиент, название."""
    tgs = re.search(
        r'type="application/x-tgsticker"[^>]*srcset="([^"]+)"', html)
    if not tgs:                          # бывает без type
        tgs = re.search(r'srcset="(https://[^"]*\.tgs[^"]*)"', html)
    if not tgs:
        raise ValueError("на странице нет анимации подарка (.tgs)")

    title = re.search(r'og:title" content="([^"]+)"', html)
    name = ""
    number = None
    if title:
        full = title.group(1)
        found = re.match(r"^(.*?)\s*#(\d+)\s*$", full)
        if found:
            name, number = found.group(1).strip(), int(found.group(2))
        else:
            name = full.strip()

    pattern = re.search(r'<image id="giftPattern"[^>]*xlink:href="([^"]+)"', html)

    # Стопы из SVG правим на замеренную поправку: приложение рисует градиент
    # чуть теплее и темнее исходного (Δ ≈ -4.5 / 0 / +1 по скриншоту).
    stops = re.findall(r'<stop stop-color="(#[0-9a-fA-F]{6})"', html)
    if len(stops) >= 2:
        gradient = tuple(shift_color(hex_rgb(stop), GRAD_SHIFT)
                         for stop in stops[:2])
    else:
        gradient = (GRAD_TOP, GRAD_BOTTOM)

    flood = re.search(r'flood-color="(#[0-9a-fA-F]{6})"', html)
    pattern_rgb = (tuple(int(flood.group(1)[i:i + 2], 16)
                         for i in (1, 3, 5)) if flood else PATTERN_RGB)

    # <g opacity="0.21" transform="translate(x, y)"><use ... scale(s)></use></g>
    spots: list[tuple[float, float, float, float]] = []
    for opacity, x, y, scale in re.findall(
            r'opacity="([\d.]+)"\s+transform="translate\(([-\d.]+),\s*([-\d.]+)\)"'
            r'>\s*<use[^>]*transform="scale\(([\d.]+)\)"', html):
        spots.append((float(x), float(y), float(opacity), float(scale)))

    # фон берём ровно тот, что нарисовал Telegram (420×280, радиальный градиент)
    svg = ""
    for block in re.findall(r"<svg[\s\S]*?</svg>", html):
        if 'viewBox="0 0 420 280"' in block:
            svg = block
            break

    return Card(slug=slug, name=name, number=number, tgs_url=tgs.group(1),
                pattern_url=pattern.group(1) if pattern else None,
                gradient=gradient, pattern_spots=spots,
                pattern_color=pattern_rgb, svg=svg)


def load_card(raw: str) -> Card:
    """Страница подарка; Telegram иногда отдаёт урезанную заглушку — повторяем."""
    slug = resolve_slug(raw)
    last: Exception | None = None
    for attempt in range(5):
        headers = UA_POOL[attempt % len(UA_POOL)]
        html = fetch("https://t.me/nft/" + slug, headers=headers).decode(
            "utf-8", "replace")
        try:
            return parse_card(html, slug)
        except ValueError as exc:
            last = exc
            time.sleep(0.6 * (attempt + 1))
    raise last if last else ValueError("страница подарка не разобралась")


# ════════════════════════════════════════════════════════════════════════════
# §2. ФОН: градиент + узор
# ════════════════════════════════════════════════════════════════════════════


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def shift_color(rgb: tuple[int, int, int],
                shift: tuple[int, int, int]) -> tuple[int, int, int]:
    """Сдвиг цвета с зажимом в 0…255."""
    return tuple(max(0, min(255, c + d)) for c, d in zip(rgb, shift))


def gradient_image(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    """Радиальный градиент, близкий к SVG Telegram (по вертикали)."""
    width, height = size
    small = Image.new("RGB", (2, 64))
    top_rgb = top if isinstance(top, tuple) else hex_rgb(top)
    bottom_rgb = bottom if isinstance(bottom, tuple) else hex_rgb(bottom)
    for y in range(64):
        k = y / 63
        small.putpixel((0, y), tuple(
            int(top_rgb[i] + (bottom_rgb[i] - top_rgb[i]) * k) for i in range(3)))
        small.putpixel((1, y), small.getpixel((0, y)))
    return small.resize((width, height), Image.BILINEAR)


def card_cover(size: int) -> tuple[float, float, float, float]:
    """Transform one 420×280 pattern period into tile coordinates.

    The period is centred horizontally. This transform alone is NOT the
    pattern renderer: svg_background also draws neighbouring periods, including
    marks crossing the top/bottom seam. The radial gradient is not repeated.
    """
    k = size / CARD_H
    return k, (CARD_W * k - size) / 2.0, CARD_W * k, CARD_H * k


def shadow_silhouette(png: bytes, px: int) -> Image.Image:
    """Alpha silhouette from the WebP that Telegram embeds in the SVG."""
    source = Image.open(io.BytesIO(png)).convert("RGBA")
    alpha = source.getchannel("A")
    if alpha.getextrema()[0] == 255:          # flat frame: fall back to luminance
        alpha = source.convert("L")
    if alpha.size != (px, px):
        alpha = alpha.resize((px, px), Image.Resampling.LANCZOS)
    return alpha


def embedded_silhouette() -> Image.Image | None:
    try:
        return Image.open(io.BytesIO(_EMBEDDED_PATTERN)).convert("L")
    except Exception:
        return None


def pattern_alpha(pattern: Image.Image) -> Image.Image:
    """Альфа (или яркость) силуэта узора в режиме L — что бы ни пришло."""
    image = pattern
    if image.mode in ("RGBA", "LA", "PA"):
        alpha = image.getchannel("A")
        if alpha.getextrema()[1] > 0:
            return alpha
    if image.mode == "P":
        image = image.convert("RGBA")
        alpha = image.getchannel("A")
        if alpha.getextrema()[1] > 0:
            return alpha
    return image.convert("L")


def radial_gradient(rgb: tuple[int, int, int], size: tuple[int, int],
                    radius: float = RADIAL_R) -> Image.Image:
    """Radial spotlight as in the app: the corner value is the second stop."""
    top, bottom = rgb
    width, height = size
    small = Image.new("RGB", (48, 48))
    pixels = small.load()
    for iy in range(48):
        for ix in range(48):
            dx, dy = (ix + .5) / 48 - .5, (iy + .5) / 48 - .5
            distance = min(1.0, (dx * dx + dy * dy) ** .5 / radius)
            pixels[ix, iy] = tuple(
                int(round(top[c] + (bottom[c] - top[c]) * distance))
                for c in range(3))
    return small.resize((width, height), Image.Resampling.BICUBIC)


# numpy в зависимостях не заявлен: он есть далеко не на каждом хосте, а нужен
# только самопроверке. Поэтому он необязательный — .giftest скажет прямо.
try:
    import numpy as np
except Exception:                       # noqa: BLE001
    np = None


# ── премиум-эмодзи ─────────────────────────────────────────────────────────
# document_id взяты из живых модулей Hikka (те, что реально отдаёт Telegram):
# если подставить выдуманный id, сообщение не отправится вовсе.
PREMIUM = {
    "diamond": ("5471952986970267163", "💎"),
    "sparkles": ("5325547803936572038", "✨"),
    "check": ("5776375003280838798", "✅"),
    "cross": ("5778527486270770928", "❌"),
    "warn": ("5447644880824181073", "⚠️"),
    "info": ("6028435952299413210", "ℹ️"),
    "bang": ("5274099962655816924", "❗️"),
    "chat": ("5443038326535759644", "💬"),
    "book": ("5386596911463541476", "📚"),
    "hourglass": ("5456591761558245861", "⌛️"),
    "folder": ("5433653135799228968", "📁"),
    "bolt": ("5456140674028019486", "⚡️"),
    "person": ("5442879640379076105", "👤"),
    "globe": ("5280658777148760247", "🌐"),
    # id не подтверждён (в исходнике 16 цифр вместо 19) — обычный символ,
    # чтобы отправка сообщения не сломалась на неверном document_id
    "shield": ("", "🛡"),
    "green": ("5416081784641168838", "🟢"),
    "red": ("5328311576736833844", "🔴"),
    "note": ("5460795800101594035", "📝"),
    "lamp": ("5857158158388041525", "💡"),
    "fire": ("5204204137327111088", "🔥"),
    "rocket": ("5235575317191474172", "🚀"),
    "chart": ("5231200819986047254", "📊"),
    "gear": ("5222142557865128918", "⚙️"),
    "link": ("5870527201874546272", "🔗"),
    "inbox": ("5443127283898405358", "📥"),
    "eye": ("5447410659077661506", "🔎"),
    "star": ("5220064167356025824", "⭐️"),
    "phone": ("5407025283456835913", "📱"),
}


def _emoji(name: str) -> str:
    """{glyph} из набора премиум-эмодзи, иначе обычный символ."""
    did, glyph = PREMIUM.get(name, ("", "•"))
    return f'<emoji document_id={did}>{glyph}</emoji>' if did else glyph


def emoji(text: str) -> str:
    """`{diamond}` → премиум-эмодзи.

    Если Telegram не примет premium-эмодзи, say() повторяет отправку без
    тегов — тогда остаётся обычный символ из середины тега, а не пустота.
    """
    text = text.replace(":}", "}")
    return re.sub(r"\{([a-z_]+)\}", lambda m: _emoji(m.group(1)), text)


def parse_pattern_spots(svg: str):
    """Every <g opacity=…><use transform="scale(…)"> of the SVG pattern.

    Между translate и <use> бывает filter="url(#patternColorFilter)" и
    перенос строки, поэтому два регулярных поиска, а не один жадный.
    """
    spots = []
    for block in re.findall(r"<g opacity[\s\S]{0,220}?</g>", svg):
        opacity = re.search(r'opacity="([\d.]+)"', block)
        pos = re.search(r'translate\(([-\d.]+),\s*([-\d.]+)\)', block)
        scale = re.search(r"scale\(([\d.]+)\)", block)
        if opacity and pos and scale:
            spots.append((float(pos.group(1)), float(pos.group(2)),
                          float(opacity.group(1)), float(scale.group(1))))
    return spots


def parse_pattern_color(svg: str) -> tuple[int, int, int]:
    flood = re.search(r'flood-color="(#[0-9a-fA-F]{6})"', svg)
    if not flood:
        return PATTERN_RGB
    value = flood.group(1).lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def parse_gradient_stops(svg: str) -> tuple[str, str] | None:
    stops = re.findall(r'<stop stop-color="(#[0-9a-fA-F]{6})"', svg)
    if len(stops) < 2:
        return None
    return stops[0], stops[1]


def svg_background(card: Card, pattern: Image.Image | None,
                   size: int) -> Image.Image | None:
    """Фон ровно из SVG Telegram: радиальный градиент + узор — нативно.

    Раньше здесь звался cairosvg (libcairo, 4 лишних пакета и 285 КБ RAM на
    каждый кадр). cairosvg не умеет feFlood/feComposite и терял часть меток,
    поэтому фон всё равно приходилось пересобирать PIL-ом — теперь сразу им.
    Силуэт узора вшит в модуль; картинка с CDN нужна только как резерв.
    """
    if not card.svg:
        return None
    stops = parse_gradient_stops(card.svg)
    if card.gradient and len(card.gradient) == 2:
        top = card.gradient[0] if isinstance(card.gradient[0], tuple) else hex_rgb(card.gradient[0])
        bottom = card.gradient[1] if isinstance(card.gradient[1], tuple) else hex_rgb(card.gradient[1])
    elif stops:
        top, bottom = hex_rgb(stops[0]), hex_rgb(stops[1])
    else:
        top, bottom = GRAD_TOP, GRAD_BOTTOM
    tile = radial_gradient((top, bottom), (size, size)).convert("RGBA")
    layer = card_pattern_layer(card, pattern, size)
    if layer is not None:
        tile.alpha_composite(layer)
    return tile.convert("RGB")


def card_pattern_layer(card: Card, pattern: Image.Image | None,
                       size: int) -> Image.Image | None:
    """Узор по калиброванной раскладке app-square (замер по IMG_8851/8853).

    Раньше (1.4.5) здесь стоял пересчёт координат SVG с шагом 833 px — шаг
    совпадал с высотой плитки, метки ложились сами на себя, и низ оставался
    пустым. Теперь берём готовые позиции pattern_instances: 21 метка на всю
    плитку, включая нижний ряд.
    """
    if pattern is None:
        pattern = embedded_silhouette()
    if pattern is None:
        return None
    solid = Image.new("RGBA", (128, 128), tuple(card.pattern_color) + (255,))
    solid.putalpha(pattern_alpha(pattern))
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sprites: dict[tuple[int, float], Image.Image] = {}
    for left, top, side, opacity in pattern_instances(card, size):
        side = max(1, round(side))
        if (left >= size or top >= size
                or left + side <= 0 or top + side <= 0):
            continue
        key = (side, round(opacity, 4))
        sprite = sprites.get(key)
        if sprite is None:
            sprite = solid.resize((side, side), Image.Resampling.LANCZOS)
            sprite.putalpha(sprite.getchannel("A").point(
                lambda a, op=opacity: min(255, round(a * op * PATTERN_BOOST))))
            sprites[key] = sprite
        layer.alpha_composite(sprite, (round(left), round(top)))
    return layer


def paint_pattern(pattern: Image.Image, rgb: tuple[int, int, int]) -> Image.Image:
    """Силуэт красим в цвет Telegram: белый → цвет, альфа сохраняется."""
    rgba = pattern.convert("RGBA")
    solid = Image.new("RGBA", rgba.size, rgb + (255,))
    solid.putalpha(rgba.getchannel("A"))
    return solid


def pattern_instances(card: Card, size: int):
    """Yield left/top/side/opacity in pixels for the selected layout."""
    if card.pattern_layout == "app-square":
        for cx, cy, side, opacity in SQUARE_PATTERN_SPOTS:
            yield ((cx - side / 2) * size, (cy - side / 2) * size,
                   max(1, round(side * size * PATTERN_GAIN)), opacity)
        return
    if card.pattern_layout != "svg-cover":
        raise ValueError("Unknown pattern layout: " + card.pattern_layout)
    k, off_x, _, _ = card_cover(size)
    for ix in (-1, 0, 1):
        for iy in (-1, 0, 1):
            for x, y, opacity, scale in card.pattern_spots:
                yield (x * k - off_x + ix * CARD_W * k,
                       y * k + iy * CARD_H * k,
                       max(1, round(BASE_MARK * scale * k * PATTERN_GAIN)), opacity)


def tile_pattern(card: Card, pattern: Image.Image | None,
                 size: tuple[int, int]) -> Image.Image | None:
    """Same motif placement in the SVG-gradient and fallback-gradient paths."""
    if pattern is None:
        return None
    width, height = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    sprites = {}
    for x, y, side, opacity in pattern_instances(card, width):
        if x >= width or y >= height or x + side <= 0 or y + side <= 0:
            continue
        key = (side, opacity)
        sprite = sprites.get(key)
        if sprite is None:
            silhouette = pattern_alpha(pattern).resize(
                (side, side), Image.Resampling.LANCZOS)
            sprite = Image.new("RGBA", (side, side),
                               tuple(card.pattern_color) + (255,))
            sprite.putalpha(silhouette.point(
                lambda a, op=opacity: min(255, round(a * op * PATTERN_BOOST))))
            sprites[key] = sprite
        layer.alpha_composite(sprite, (round(x), round(y)))
    return layer


def tile_image(card: Card, pattern: Image.Image | None,
               size: int) -> Image.Image:
    """Сама «плитка»: градиент + узор, скруглённые углы."""
    exact = svg_background(card, pattern, size) if card.blue else None
    if exact is not None:
        tile = exact.convert("RGBA")
    else:
        if card.blue:
            # В SVG карточки радиальный градиент, а не линейный: проверка
            # по og:image Resistance Dog #3424 дала одинаковый цвет во всех
            # четырёх углах и светлее середину. Линейный давал тёмный низ.
            top, bottom = card.gradient
            tile = radial_gradient((top, bottom), (size, size)).convert("RGBA")
        else:
            tile = gradient_image((size, size), "#1b1b1b",
                                  "#0d0d0d").convert("RGBA")
        if pattern is not None:
            overlay = tile_pattern(card, pattern, (size, size))
            if overlay is not None:
                tile.alpha_composite(overlay)
    if card.pattern_layout == "app-square":
        # Скругление замерено по эталону IMG_8853: на y=0.005s граница плитки
        # идёт от x=0.075s, то есть inset = 0.17s против 0.40s у приложения.
        aa = 2
        extent = size * aa
        mask = Image.new("L", (extent, extent), 0)
        radius = extent / 2
        points = []
        for index in range(1024):
            theta = 2 * math.pi * index / 1024
            cx, cy = math.cos(theta), math.sin(theta)
            points.append((radius - .5 + radius * math.copysign(abs(cx)**.17, cx),
                           radius - .5 + radius * math.copysign(abs(cy)**.17, cy)))
        ImageDraw.Draw(mask).polygon(points, fill=255)
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)
    else:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, size - 1, size - 1), radius=int(CARD_RADIUS * size / CARD_W),
            fill=255)
    tile.putalpha(mask)
    return tile


def grid_page(cards: list, size: int,
              patterns: list | None = None) -> tuple[Image.Image, list, int]:
    """Одна страница с несколькими подарками: сетка плиток + подписи.

    Возвращает (фон, [(card, плитка, x, y)] , сторона плитки). Плитки лежат
    без модели: модель добавляет вызывающий, чтобы кадры шли потоком и в
    памяти не висело n полноразмерных кадров. `patterns` — узор каждого
    подарка по порядку: у Resistance Dog и Ginger Cookie силуэты разные.
    """
    count = max(1, len(cards))
    cols = 1 if count == 1 else math.ceil(math.sqrt(count))
    rows = math.ceil(count / cols)
    gap = int(round(size * GRID_GAP))
    margin = int(round(size * GRID_MARGIN))
    tile_side = (size - 2 * margin - (cols - 1) * gap) // cols
    # высота ряда = плитка + своя подпись + небольшой зазор до следующего
    row_side = tile_side + max(footer_height(tile_side, card) for card in cards) \
        + int(tile_side * 0.02)
    height = 2 * margin + rows * row_side + (rows - 1) * gap
    canvas = Image.new("RGBA", (size, height), PAGE_BG + (255,))
    spots = []
    for index, card in enumerate(cards):
        col, row = index % cols, index // cols
        # неполный последний ряд центрируем
        in_row = min(cols, count - row * cols)
        row_width = in_row * tile_side + (in_row - 1) * gap
        left = (size - row_width) // 2 + col * (tile_side + gap)
        top = margin + row * (row_side + gap)
        pattern = patterns[index] if patterns else None
        spots.append((card, tile_image(card, pattern, tile_side), left, top))
    return canvas, spots, tile_side


def grid_frame_stream(items: list, size: int = 1024, fps: int = 60):
    """Кадры сетки: все подарки анимируются одновременно, кадр за кадром.

    Длительность — по самому короткому подарку: у разных подарков разное
    число кадров, иначе последний кадр одного висел бы стоп-кадром.
    Плитки рисуются один раз на всю сборку, модель добавляется в каждом кадре.
    """
    if not items:
        raise ValueError("нечего собирать")
    from rlottie_python import LottieAnimation
    prepared = []
    for card, lottie, _pattern in items:
        meta = json.loads(lottie)
        padded = padded_lottie(lottie)
        prepared.append({
            "animation": LottieAnimation.from_data(json.dumps(padded)),
            "ip": int(meta.get("ip", 0)),
            "op": int(meta["op"]),
            "step": frame_step(int(meta.get("fr") or 60), fps),
            "ratio": padded["w"] / meta["w"],
        })
    step = min(item["step"] for item in prepared)
    canvas_base, layout, _side = grid_page(
        [card for card, _, _ in items], size, [pattern for _, _, pattern in items])
    tiles = [(card, tile, x, y) for card, tile, x, y in layout]
    total = min((item["op"] - item["ip"]) // step for item in prepared)
    try:
        for index in range(total):
            canvas = canvas_base.copy()
            for (card, tile, x, y), item in zip(tiles, prepared):
                side = tile.width
                model_side = int(side * SQUARE_MODEL_INSET)
                frame_side = round(model_side * item["ratio"])
                offset = round(side * SQUARE_MODEL_DY)
                model = render_model_frame(
                    item["animation"], item["ip"] + index * item["step"],
                    frame_side)
                frame = tile.copy()
                frame.alpha_composite(
                    model, ((side - frame_side) // 2,
                            (side - frame_side) // 2 + offset))
                canvas.alpha_composite(frame, (x, y))
                draw_footer(card, canvas, side, y, x)
            yield canvas.convert("RGB")
    finally:
        for item in prepared:
            item["animation"].lottie_animation_destroy()


# ── самопроверка ──────────────────────────────────────────────────────────
# Замеры идут по тому же кадру, что уходит в чат, поэтому проверка ловит
# именно те поломки, которые видно глазами: пустой низ плитки, обрезанную
# модель, уехавшую подпись.

SELFTEST_REFS = ("gingercookie-1", "gingercookie-2", "gingercookie-3")


def require_numpy() -> None:
    if np is None:
        raise RuntimeError(
            "для .giftest нужен numpy: pip install numpy")


def region_density(frame: Image.Image, size: int) -> dict:
    """Плотность узора по третям плитки и полосам слева/справа от модели."""
    require_numpy()
    tile_side = int(size * TILE_WIDTH)
    top = int(round(frame.height * TILE_TOP))
    tile = frame.crop(((size - tile_side) // 2, top,
                       (size - tile_side) // 2 + tile_side, top + tile_side))
    work = tile.convert("RGB")
    array = np.asarray(work).astype(float)
    # гладкий фон вычитаем — остаётся только узор
    smooth = np.stack([gaussian_blur(array[:, :, c], 25) for c in range(3)], axis=2)
    energy = np.abs(array - smooth).sum(2)
    height, width = energy.shape
    model = (((np.mgrid[0:height, 0:width][1] - width / 2) / (width * 0.36)) ** 2
             + ((np.mgrid[0:height, 0:width][0] - height * 0.52) / (height * 0.40)) ** 2) < 1
    outside = np.where(model, 0.0, energy)
    thirds = [round(float((outside[int(i * height / 3):int((i + 1) * height / 3)] > 4).mean() * 100), 1)
              for i in range(3)]
    return {"thirds": thirds, "mean": round(float(outside.mean()), 1)}


def gaussian_blur(channel, radius: float):
    """Размытие без scipy: уменьшить и вернуть обратно."""
    from PIL import ImageFilter
    return np.asarray(
        Image.fromarray(channel.astype("uint8")).filter(
            ImageFilter.GaussianBlur(radius))).astype(float)


def model_box(frame: Image.Image, size: int) -> tuple:
    """Габарит модели: доля от плитки и минимальный запас до её краёв.

    Модель ищем не по «светлее фона», а по заметно более светлым пятнам:
    печенька почти белая, а градиент и узор — синие, поэтому порог по
    сумме каналов отделяет её от фона надёжно.
    """
    require_numpy()
    tile_side = int(size * TILE_WIDTH)
    top = int(round(frame.height * TILE_TOP))
    left = (size - tile_side) // 2
    tile = np.asarray(frame.crop(
        (left, top, left + tile_side, top + tile_side)).convert("RGB")).astype(float)
    brightness = tile.sum(2)
    mask = brightness > np.percentile(brightness, 99.0)
    if mask.sum() < 50:
        return {"width": 0.0, "height": 0.0, "margin": 0.0}
    rows, cols = np.where(mask)
    box = (cols.min(), rows.min(), cols.max(), rows.max())
    margin = min(box[0], box[1], tile_side - box[2], tile_side - box[3]) / tile_side
    return {"width": round(float((box[2] - box[0]) / tile_side), 3),
            "height": round(float((box[3] - box[1]) / tile_side), 3),
            "margin": round(float(margin), 3)}


def check_frame(card: Card, lottie_bytes: bytes, pattern, size: int,
                fps: int, at: float = 0.0) -> dict:
    """Кадр на заданной секунде + его замеры (без сборки видео)."""
    total = effective_fps(lottie_bytes, fps)
    stream = frame_stream(card, lottie_bytes, pattern, size=size, fps=total)
    want = max(0, int(round(at * total)))
    frame = None
    for index, current in enumerate(stream):
        if index >= want:
            frame = current
            break
    if frame is None:
        raise ValueError("кадр не отрисовался")
    return {"frame": frame, "density": region_density(frame, size),
            "model": model_box(frame, size)}


def build_selftest(refs=SELFTEST_REFS, size: int = 512, fps: int = 30,
                   marks=(0.0, 1.5, 2.9)) -> tuple:
    """Проверить несколько подарков: замеры по кадрам + картинка для глаза.

    Гоняет анимацию один раз на подарок и снимает кадры на нужных секундах —
    без записи видео, поэтому проверка быстрая.
    """
    results, previews = [], []
    skipped = []
    for ref in refs:
        started = time.time()
        try:
            card, lottie, pattern = load_assets(ref)
        except Exception as exc:                       # noqa: BLE001
            # один недоступный подарок не должен отменять всю проверку
            skipped.append((ref, str(exc) or type(exc).__name__))
            continue
        card.pattern_layout = "app-square"
        if not card.name and not card.number:
            card.name = resolve_slug(ref)
        total = effective_fps(lottie, fps)
        wanted = {int(round(at * total)): at for at in marks}
        frames = {}
        stream = frame_stream(card, lottie, pattern, size=size, fps=total)
        for index, current in enumerate(stream):
            if index in wanted:
                frames[wanted[index]] = current
            if len(frames) == len(wanted):
                break
        middle = frames.get(marks[len(marks) // 2]) or next(iter(frames.values()))
        density = region_density(middle, size)
        box = model_box(middle, size)
        results.append({
            "ref": ref,
            "name": f"{card.name} #{card.number}" if card.number else card.name,
            "size": size,
            "fps": total,
            "build": round(time.time() - started, 1),
            "thirds": density["thirds"],
            "model": box,
            "frames_diff": int(len(frames) > 1 and
                               (np.asarray(next(iter(frames.values())))
                                != np.asarray(list(frames.values())[-1])).any()),
        })
        previews.append((results[-1]["name"], middle))
    if not results:
        raise ValueError("не удалось загрузить ни один подарок: " + "; ".join(
            "{} — {}".format(ref, reason) for ref, reason in skipped))
    if skipped:
        results[-1].setdefault("skipped", skipped)
    return results, previews


def preview_sheet(previews: list, width: int = 360) -> Image.Image:
    """Кадры проверенных подарков в одну картинку."""
    thumbs = []
    for _name, frame in previews:
        image = frame.copy()
        image.thumbnail((width, width * 3), Image.Resampling.LANCZOS)
        thumbs.append(image)
    if not thumbs:
        raise ValueError("нет кадров")
    gap = 12
    total = sum(image.width for image in thumbs) + gap * (len(thumbs) - 1)
    height = max(image.height for image in thumbs)
    sheet = Image.new("RGB", (total, height), PAGE_BG)
    x = 0
    for image in thumbs:
        sheet.paste(image, (x, 0))
        x += image.width + gap
    return sheet


def selftest_verdict(results: list) -> tuple:
    """Понятный итог: что в норме, что нет."""
    checks = []
    # 1. узор есть внизу, а не только сверху
    lows = [row["thirds"][2] for row in results]
    checks.append(("Узор в нижней трети плитки", min(lows) >= 3.0,
                   f"{min(lows):.1f}% (норма ≥ 3%)"))
    # 2. низ не пустее верха в разы — типичный баг прошлых версий
    ratios = [row["thirds"][2] / max(row["thirds"][0], 0.1) for row in results]
    checks.append(("Низ не пустее верха", min(ratios) >= 0.25,
                   f"худшее отношение {min(ratios):.2f} (норма ≥ 0.25)"))
    # 3. модель не обрезана краем плитки
    margins = [row["model"]["margin"] for row in results]
    checks.append(("Модель не обрезана", min(margins) >= 0.0,
                   f"минимальный запас {min(margins) * 100:.1f}% стороны"))
    # 4. размер модели как в приложении
    sides = [row["model"]["width"] for row in results]
    checks.append(("Ширина модели ≈ 0.475 плитки", abs(max(sides) - 0.475) < 0.10,
                   f"{min(sides):.3f}…{max(sides):.3f}"))
    # 5. анимация живая
    alive = all(row["frames_diff"] for row in results)
    checks.append(("Кадры меняются", alive, "первый и последний кадры различаются"
                   if alive else "кадры одинаковые"))
    return checks



def page(card: Card, pattern: Image.Image | None, size: int,
         footer: bool) -> tuple[Image.Image, int, int, int, int]:
    """Страница: тёмный фон, плитка сверху, место под подпись снизу.

    Пропорции взяты с эталонных роликов: плитка 81% ширины кадра и 69%
    высоты, значит кадр выше, чем шире (как карточка в приложении).
    """
    if not footer:
        canvas = Image.new("RGBA", (size, size), PAGE_BG + (255,))
        tile = tile_image(card, pattern, size)
        canvas.alpha_composite(tile, (0, 0))
        return canvas, size, 0, 0, size
    tile_side = int(size * TILE_WIDTH)
    height = int(round(size * ASPECT))
    top = int(round(height * TILE_TOP))
    canvas = Image.new("RGBA", (size, height), PAGE_BG + (255,))
    tile = tile_image(card, pattern, tile_side)
    x = (size - tile_side) // 2
    canvas.alpha_composite(tile, (x, top))
    return canvas, tile_side, x, top, height


# ════════════════════════════════════════════════════════════════════════════
# §3. РЕНДЕР КАДРОВ
# ════════════════════════════════════════════════════════════════════════════


CAP_TO_SIZE = {"medium": 0.711, "bold": 0.711,
               "regular": 0.711}      # заглавная Roboto / кегль


def emoji_source():
    """Local emoji assets first; bounded network fallback for other captions."""
    from pilmoji.source import BaseSource
    class LocalEmojiSource(BaseSource):
        def get_emoji(self, emoji, /):
            key = "-".join(f"{ord(c):x}" for c in emoji if ord(c) != 0xfe0f)
            if key in _EMBEDDED_EMOJI:
                return io.BytesIO(_EMBEDDED_EMOJI[key])
            roots = (Path(__file__).resolve().parent,
                     Path(__file__).resolve().parent.parent)
            for root in roots:
                path = root / "data" / "emoji" / (key + ".png")
                if path.is_file():
                    return io.BytesIO(path.read_bytes())
            try:
                return io.BytesIO(fetch(
                    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@16.0.1/assets/72x72/"
                    + key + ".png", timeout=3))
            except Exception:
                return None
        def get_discord_emoji(self, id, /):
            return None
    return LocalEmojiSource


def draw_text(image: Image.Image, draw: ImageDraw.ImageDraw, xy, text: str,
              face: ImageFont.FreeTypeFont, fill) -> None:
    """Draw once on a separate layer; no partial drawing on source failure."""
    label = str(text or "")
    # Ordinary strings never need pilmoji or a network request.
    if label == renderable(label, face):
        draw.text(xy, label, font=face, fill=fill)
        return
    try:
        from pilmoji import Pilmoji
        layer = Image.new("RGBA", image.size)
        with Pilmoji(layer, source=emoji_source()) as painter:
            painter.text(xy, label, font=face, fill=fill)
        image.paste(layer, (0, 0), layer)
    except Exception:
        draw.text(xy, renderable(label, face), font=face, fill=fill)


def renderable(text: str, face: ImageFont.FreeTypeFont) -> str:
    """Drop unsupported glyphs rather than drawing the font's .notdef tofu."""
    missing = face.getmask(chr(0x10ffff))
    signature = (missing.size, bytes(missing))
    out = []
    for char in str(text or ""):
        if char in "\ufe0f\ufe0e\u200d":
            continue
        try:
            mask = face.getmask(char)
            if char.isspace() or (mask.size, bytes(mask)) != signature:
                out.append(char)
        except Exception:
            continue
    return "".join(out).strip()


def font_size(cap_px: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    """Кегль так, чтобы заглавная буква была ровно cap_px высотой."""
    return font(max(6, int(round(cap_px / CAP_TO_SIZE.get(weight, 0.711)))),
                bold=(weight == "bold"))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Bundled original Roboto Medium; no font downloads or sibling files."""
    return ImageFont.truetype(io.BytesIO(_EMBEDDED_ROBOTO), size)


def ink_textbbox(draw, text: str, face):
    """Horizontal ink bounds, not advance width (which includes side bearings)."""
    box = list(draw.textbbox((0, 0), text, font=face))
    mask, offset = face.getmask2(text)
    ink = mask.getbbox()
    if ink:
        box[0], box[2] = offset[0] + ink[0], offset[0] + ink[2]
    return tuple(box)


def footer_height(tile_side: int, card: Card) -> int:
    """Сколько места нужно под подпись под плиткой (для сетки)."""
    lines = 1 if (card.name or card.number) else 0
    lines += 1 if card.author else 0
    lines += 1 if card.caption else 0
    return int(tile_side * (NAME_GAP + NAME_CAP)) + \
        int(tile_side * CAPTION_CAP * 1.45) * max(0, lines - 1)


def footer_bottom(card: Card, tile_side: int, tile_y: int,
                  canvas: Image.Image) -> int:
    """Низ подписи по фактически нарисованным строкам (для обрезки кадра).

    Одиночная карточка больше не тянет фиксированную высоту ASPECT: если
    строк меньше, кадр режется ровно по низу последней, с тем же зазором
    NAME_GAP, что и под плиткой.
    """
    gap = int(tile_side * NAME_GAP)
    styles = []
    if card.name or card.number:
        styles.append((NAME_CAP, True))          # имя + номер
    if card.author:
        styles.append((AUTHOR_CAP, False))
    if card.caption:
        styles.append((CAPTION_CAP, False))
    if not styles:
        return canvas.height
    bottom = tile_y + tile_side
    for index, (cap, _first) in enumerate(styles):
        bottom += int(tile_side * 0.034) if index else gap
        bottom += int(tile_side * cap / CAP_TO_SIZE.get("regular", 0.711))
    return min(canvas.height, bottom + gap // 2)


def draw_footer(card: Card, canvas: Image.Image, tile_side: int,
                tile_y: int, tile_x: int | None = None) -> Image.Image:
    """Название, номер, автор и свой текст под плиткой — один раз на кадр.

    tile_x — левый край плитки: в сетке подпись центрируется по своей
    плитке, в одиночной карточке (tile_x=None) — по всей странице.
    """
    draw = ImageDraw.Draw(canvas)
    width = canvas.width
    face_name = font_size(int(tile_side * NAME_CAP), weight="medium")
    face_num = font_size(int(tile_side * NUMBER_CAP), weight="regular")
    badge = f"#{card.number}" if card.number else ""
    # зазор «название → номер»: в приложении 20 px при плитке 958 (2.1%)
    pad = max(4, round(tile_side * TEXT_GAP))
    box_name = ink_textbbox(draw, card.name or "", face_name)
    box_num = (ink_textbbox(draw, badge, face_num)
               if badge else (0, 0, 0, 0))
    wide = box_name[2] - box_name[0]
    if badge:
        wide += pad + box_num[2] - box_num[0]
    if tile_x is None:
        left = (width - wide) // 2
    else:
        left = tile_x + (tile_side - wide) // 2
    cursor = tile_y + tile_side + int(tile_side * NAME_GAP)
    if card.name:
        draw_text(canvas, draw, (left - box_name[0], cursor - box_name[1]),
                  card.name, face_name, (255, 255, 255, 255))
    if badge:
        # низ названия = cursor + высота заглавной; номер садим туда же
        name_bottom = cursor + int(tile_side * NAME_CAP)
        top_num = name_bottom - (box_num[3] - box_num[1]) - box_num[1]
        draw_text(canvas, draw,
                  (left + box_name[2] - box_name[0] + pad - box_num[0],
                   top_num), badge, face_num, (0x9A, 0x9A, 0xA2, 255))
    # строки идут строго друг под другом: имя+номер, автор, свой текст
    line = cursor + int(tile_side * NAME_CAP)
    if card.author:
        face_auth = font_size(int(tile_side * AUTHOR_CAP), weight="regular")
        label = renderable(card.author, face_auth)
        box_auth = draw.textbbox((0, 0), label, font=face_auth)
        cursor_auth = line + int(tile_side * 0.030)
        auth_left = (width - (box_auth[2] - box_auth[0])) // 2 if tile_x is None \
            else tile_x + (tile_side - (box_auth[2] - box_auth[0])) // 2
        draw.text((auth_left - box_auth[0], cursor_auth - box_auth[1]),
                  label, font=face_auth, fill=(0x6B, 0x6B, 0x70, 255))
        line = cursor_auth + box_auth[3] - box_auth[1]
    if card.caption:
        face_cap = font_size(int(tile_side * CAPTION_CAP), weight="regular")
        box_cap = draw.textbbox((0, 0), renderable(card.caption, face_cap),
                                font=face_cap)
        cap_width = box_cap[2] - box_cap[0]
        try:
            from pilmoji import Pilmoji
            with Pilmoji(canvas, source=emoji_source()) as painter:
                cap_width = painter.getsize(card.caption, font=face_cap)[0]
        except Exception:
            pass
        cursor_cap = line + int(tile_side * 0.034)
        cap_left = (width - cap_width) // 2 if tile_x is None \
            else tile_x + (tile_side - cap_width) // 2
        draw_text(canvas, draw,
                  (cap_left - box_cap[0], cursor_cap - box_cap[1]),
                  card.caption, face_cap, (0xE6, 0xE6, 0xEC, 255))
    return canvas


def expand_viewbox(svg: str, pad: float) -> str:
    """Расширить viewBox кадра Lottie, чтобы модель не резалась краем холста.

    В .tgs модель на некоторых кадрах вылезает за 512×512 (замер: до +2 px
    влево и +2 px вправо). Раньше такие кадры обрезались по краю, и печенька
    выглядела «разрезанной». Расширяем область И сохраняем увеличенный
    холст. Центральный кроп обратно до 512 запрещён: он снова отрежет
    выступающие пиксели. Увеличенные viewBox И размер растра сохраняют масштаб.
    """
    head = re.search(r"<svg[^>]*>", svg)
    if not head or not pad:
        return svg
    tag = head.group(0)
    size = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', tag)
    if not size:
        return svg
    width, height = float(size.group(1)), float(size.group(2))
    k = 1 + 2 * pad
    new = re.sub(r'width="[\d.]+"', 'width="{:.2f}"'.format(width * k), tag, count=1)
    new = re.sub(r'height="[\d.]+"', 'height="{:.2f}"'.format(height * k), new, count=1)
    new = new.replace(
        'viewBox="0 0 {} {}"'.format(size.group(1), size.group(2)),
        'viewBox="{:.2f} {:.2f} {:.2f} {:.2f}"'.format(
            -width * pad, -height * pad, width * k, height * k))
    return svg.replace(tag, new, 1)


def frame_step(source: int, requested: int) -> int:
    """Choose a true divisor, rounding FPS down (25 -> 20, not 30)."""
    allowed = [n for n in range(1, source + 1) if source % n == 0]
    rate = max((n for n in allowed if n <= max(1, requested)), default=1)
    return source // rate


def effective_fps(lottie_bytes: bytes, fps: int) -> int:
    metadata = json.loads(lottie_bytes)
    source = int(metadata.get("fr") or 60)
    return source // frame_step(source, fps)


def padded_lottie(lottie_bytes: bytes, pad: float = MODEL_PAD):
    """Expand the root composition and translate its parentless layers.

    A null parent translates the whole existing parent hierarchy, not individual
    keyframes. No original-size precomposition is introduced (it would clip).
    The original JSON and all shape/dash properties stay unchanged.
    """
    data = json.loads(lottie_bytes)
    width, height = int(data["w"]), int(data["h"])
    margin_x, margin_y = math.ceil(width * pad), math.ceil(height * pad)
    index = max((layer.get("ind", 0) for layer in data["layers"]), default=0) + 1
    for layer in data["layers"]:
        if "parent" not in layer:
            layer["parent"] = index
    data["layers"].insert(0, {
        "ty": 3, "ind": index, "nm": "Render canvas padding", "st": 0,
        "ip": data.get("ip", 0), "op": data["op"],
        "ks": {"o": {"a": 0, "k": 100}, "r": {"a": 0, "k": 0},
               "p": {"a": 0, "k": [margin_x, margin_y, 0]},
               "a": {"a": 0, "k": [0, 0, 0]},
               "s": {"a": 0, "k": [100, 100, 100]}}})
    data["w"], data["h"] = width + 2 * margin_x, height + 2 * margin_y
    return data


def render_model_frame(animation, frame: int, side: int) -> Image.Image:
    """rlottie returns premultiplied BGRA; unpremultiply before compositing."""
    buffer = animation.lottie_animation_render(frame_num=frame, width=side, height=side)
    return Image.frombytes("RGBa", (side, side), buffer, "raw", "BGRa").convert("RGBA")


def frame_stream(card: Card, lottie_bytes: bytes, pattern, size: int = 512,
                 fps: int = 60, crop_tolerance: int = 2600):
    """Кадры карточки по одному: [фон + модель + имя + номер].

    Генератор, поэтому MP4 пишется потоком и 180 кадров не лежат в памяти
    одновременно (на слабом хостинге это был OOM).
    """
    try:
        from rlottie_python import LottieAnimation
    except ImportError as exc:
        raise RuntimeError("нужен нативный рендер: pip install rlottie-python==1.3.8") from exc
    metadata = json.loads(lottie_bytes)
    padded = padded_lottie(lottie_bytes)
    source_fps = int(metadata.get("fr") or 60)
    step = frame_step(source_fps, fps)
    fps = source_fps // step
    footer = bool(card.name or card.number)
    base, tile_side, tile_x, tile_y, _height = page(card, pattern, size, footer)
    model_inset = SQUARE_MODEL_INSET if card.pattern_layout == "app-square" else MODEL_INSET
    model_side = int(tile_side * model_inset)
    # рамка модели с запасом (см. MODEL_PAD) центрируется по той же точке
    frame_side = round(model_side * padded["w"] / metadata["w"])
    # Подпись одинаковая во всех кадрах — рисуем один раз и вставляем слоем.
    # Раньше pilmoji перерисовывал текст 180 раз, и сборка упиралась в это.
    if footer:
        bake = Image.new("RGB", base.size, PAGE_BG)
        draw_footer(card, bake, tile_side, tile_y)
        band_top = max(0, tile_y + tile_side)
        band = (0, band_top, base.width, footer_bottom(card, tile_side, tile_y, base))
        footer_layer = bake.crop(band)
        # Кадр обрезается по фактическому низу подписи: раньше высота была
        # фиксированной (ASPECT), и под коротким названием оставалась
        # широкая пустая полоса — на глаз «странное место снизу».
        if band[3] < base.height:
            base = base.crop((0, 0, base.width, band[3]))
    else:
        band = footer_layer = None

    model_dy = SQUARE_MODEL_DY if card.pattern_layout == "app-square" else MODEL_DY
    offset = round(tile_side * model_dy)
    model_xy = (tile_x + (tile_side - frame_side) // 2,
                tile_y + (tile_side - frame_side) // 2 + offset)
    animation = LottieAnimation.from_data(json.dumps(padded))
    try:
        # rlottie reports op+1 as totalframe on this animation. Lottie op is
        # exclusive: iterate the original [ip, op), exactly 180, not 181.
        for frame in range(int(metadata.get("ip", 0)), int(metadata["op"]), step):
            model = render_model_frame(animation, frame, frame_side)
            canvas = base.copy()
            canvas.alpha_composite(model, model_xy)
            if footer_layer is not None:
                canvas.paste(footer_layer, (0, band[1]))
            yield canvas.convert("RGB")
    finally:
        animation.lottie_animation_destroy()


def eat_halo(image: Image.Image, radius: int = 3) -> Image.Image:
    """Съесть цветной ореол по краю модели после ресайза.

    Lottie рисуется с полупрозрачной каймой, при уменьшении она становится
    видимой цветной рамкой — в приложении её нет.
    """
    from PIL import ImageFilter
    alpha = image.getchannel("A")
    for _ in range(max(1, radius)):
        alpha = alpha.filter(ImageFilter.MinFilter(3))
    out = image.copy()
    out.putalpha(alpha)
    return out


def crop_background(image: Image.Image, tolerance: int) -> Image.Image:
    """Убрать тёмный прямоугольник фона Lottie (он мешает узору)."""
    width, height = image.size
    work = image.convert("RGBA")
    pixels = work.load()
    corner = pixels[0, 0]
    if corner[3] < 8:                       # уже прозрачный — ничего не делаем
        return work
    target = corner[:3]
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a and abs(r - target[0]) + abs(g - target[1]) + abs(b - target[2]) < tolerance:
                pixels[x, y] = (0, 0, 0, 0)
    return work


# ════════════════════════════════════════════════════════════════════════════
# §4. СОХРАНЕНИЕ
# ════════════════════════════════════════════════════════════════════════════


def ffmpeg_bin() -> str:
    """ffmpeg из PATH или из пакета imageio-ffmpeg (в Heroku образа нет)."""
    from shutil import which
    found = which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise RuntimeError(
            "нужен ffmpeg: apt install ffmpeg или pip install imageio-ffmpeg"
        ) from exc


def save_gif(frames, fps: int, path: str) -> int:
    """Stream paletted frames; cumulative centisecond timing keeps duration.

    GIF cannot represent uniform 60 fps; 10/20 ms delays alternate instead.
    No RGB-frame list and no 180-frame palette list are held in memory.
    """
    from PIL import GifImagePlugin
    count = 0
    with open(path, "wb") as output:
        for index, frame in enumerate(frames):
            tile = frame.convert("RGB").quantize(colors=256)
            if index == 0:
                header, _ = GifImagePlugin.getheader(tile, info={"loop": 0})
                for block in header:
                    output.write(block)
            duration = 10 * (round((index + 1) * 100 / fps)
                             - round(index * 100 / fps))
            for block in GifImagePlugin.getdata(
                    tile, duration=duration, disposal=1,
                    include_color_table=(index > 0)):
                output.write(block)
            count += 1
        if not count:
            raise ValueError("нет кадров")
        output.write(b";")
    return os.path.getsize(path)


def save_mp4(frames, fps: int, path: str, crf: int = 14,
             animation: bool = False) -> int:
    """MP4 через ffmpeg: кадры идут потоком, без 180 PNG на диске.

    Пайп вместо временной папки: сборка быстрее и не упирается в запись
    файлов на слабом хостинге.

    animation=True — «гифка» Telegram: mp4 без звуковой дорожки. Именно так
    ходят гифки в самом Telegram, и такой файл крутится сам в чате, в том
    числе на iOS (там настоящий .gif показывается файлом со стрелкой).
    """
    frames = iter(frames)                 # список или генератор — оба годятся
    try:
        first = next(frames)
    except StopIteration:
        raise ValueError("нет кадров") from None
    width, height = first.size
    width -= width % 2
    height -= height % 2
    command = [
        ffmpeg_bin(), "-y", "-loglevel", "error", "-filter_threads", "1",
        "-thread_queue_size", "1", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "{}x{}".format(width, height), "-framerate", str(fps),
        "-i", "-",
    ]
    if not animation:
        # Пустая звуковая дорожка: без неё Telegram показывает mp4 как GIF
        # (значок GIF, маленькое превью), с ней — как обычное видео.
        command += ["-f", "lavfi", "-i",
                    "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-shortest"]
    command += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        # tune animation держит чёткие края плоской графики: без него
        # границы плитки, текст и узор «плывут» уже на среднем качестве
        "-tune", "animation",
        "-crf", str(crf), "-preset", "medium", "-threads", "2",
        "-rc-lookahead", "6", "-refs", "2",
    ]
    if not animation:
        command += ["-c:a", "aac", "-b:a", "8k", "-ac", "1", "-ar", "22050"]
    if animation:
        # у гифки Telegram звуковой дорожки нет вообще: пустая (anullsrc)
        # тоже не годится — с ней сервер видит обычное видео
        command += ["-an"]
    command += ["-movflags", "+faststart", path]

    # A file avoids stderr-pipe deadlock. Always reap the child on failure.
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL, stderr=errors)
        try:
            for frame in itertools.chain([first], frames):
                if frame.size != (width, height):
                    frame = frame.resize((width, height), Image.LANCZOS)
                try:
                    process.stdin.write(frame.convert("RGB").tobytes())
                except (BrokenPipeError, ValueError):
                    # ffmpeg упал раньше (неверные параметры, нет места на
                    # диске) — показываем его сообщение, а не «Broken pipe»
                    errors.seek(0)
                    raise RuntimeError("ffmpeg: " + errors.read(2000).decode(
                        "utf-8", "replace")) from None
            process.stdin.close()
            if process.wait() != 0:
                errors.seek(0)
                raise RuntimeError("ffmpeg: " + errors.read(2000).decode("utf-8", "replace"))
        except BaseException:
            process.kill()
            process.wait()
            process.stdin.close()
            raise

    return os.path.getsize(path)


# ════════════════════════════════════════════════════════════════════════════
# §5. ПУБЛИЧНЫЙ ВХОД
# ════════════════════════════════════════════════════════════════════════════


def load_assets(raw: str, data_dir: str | None = None):
    """Explicit offline fixture mode; never silently substitute another gift."""
    if data_dir is not None:
        folder = Path(data_dir)
        slug = resolve_slug(raw)
        if slug.lower() not in ("gingercookie-89402", "89402"):
            raise ValueError("Offline fixture is Ginger Cookie #89402 only")
        svg = (folder / "card_420x280.svg").read_text(encoding="utf-8")
        html = ('<meta property="og:title" content="Ginger Cookie #89402">'
                '<i type="application/x-tgsticker" srcset="offline">' + svg)
        card = parse_card(html, "gingercookie-89402")
        lottie = (folder / "gift_lottie.json").read_bytes()
        try:
            pattern = paint_pattern(Image.open(folder / "pattern_128.png"),
                                    card.pattern_color)
        except (OSError, ValueError):
            pattern = None
        return card, lottie, pattern
    card = load_card(raw)
    tgs = fetch(card.tgs_url)
    lottie = gzip.decompress(tgs) if tgs[:2] == b"\x1f\x8b" else tgs
    pattern = load_pattern(card)
    return card, lottie, pattern


# Узор у каждого подарка свой: страница отдаёт его картинкой (#giftPattern,
# 128×128 WebP), и он различается даже внутри одной коллекции по номерам.
# Вшитый силуэт — только запасной вариант, если CDN не ответил.
_PATTERN_CACHE: dict[str, bytes] = {}
PATTERN_CACHE_LIMIT = 32
# Кеш готовых карточек в памяти: mp4 ~1 МБ, gif на 1024/60 ~33 МБ.
# Без лимитов 10 разных подарков подряд = сотни мегабайт и OOM
# на слабом хостинге, поэтому есть границы на файл и на всё разом.
CACHE_MAX_FILE = 12 * 1024 * 1024      # 12 МБ на одну карточку
CACHE_MAX_TOTAL = 48 * 1024 * 1024     # 48 МБ на весь кеш


def load_pattern(card: Card) -> Image.Image | None:
    """Силуэт узора именно этого подарка; при сбое — вшитый запасной."""
    url = getattr(card, "pattern_url", None)
    if not url:
        return embedded_silhouette()
    blob = _PATTERN_CACHE.get(url)
    if blob is None:
        try:
            blob = fetch(url)
        except Exception:                              # noqa: BLE001
            return embedded_silhouette()
        if len(_PATTERN_CACHE) >= PATTERN_CACHE_LIMIT:
            _PATTERN_CACHE.pop(next(iter(_PATTERN_CACHE)))
        _PATTERN_CACHE[url] = blob
    try:
        with Image.open(io.BytesIO(blob)) as opened:
            return pattern_alpha(opened)
    except Exception:                                  # noqa: BLE001
        return embedded_silhouette()


def _with_ext(path: str, ext: str) -> str:
    """Сменить расширение, не теряя имя (см. ниже)."""
    """`grid.animation` → `grid.mp4`.

    Не Path.with_suffix: он считает суффиксом всё после последней точки,
    поэтому «grid.animation» превращался в «1.mp4» (имя «grid» пропадало).
    """
    base = os.path.basename(str(path))
    stem = base.rsplit(".", 1)[0] if "." in base else base
    # «gift.mp4.animation» / «gift.gif.animation» → одно расширение
    while "." in stem and stem.rsplit(".", 1)[1] in (
            "mp4", "gif", "animation", "webm", "mkv"):
        stem = stem.rsplit(".", 1)[0]
    return os.path.join(os.path.dirname(str(path)) or ".", stem + ext)


def save_animation(frames, fps: int, fmt: str, path: str) -> str:
    """Decide fallback BEFORE consuming the one-shot frame generator."""
    if fmt in ("mp4", "animation"):
        try:
            ffmpeg_bin()
        except RuntimeError:
            path = _with_ext(path, ".gif")
            fmt = "gif"
    if fmt == "animation":
        # mp4 без звука; расширение принудительно, даже если путь уже .gif
        path = _with_ext(path, ".mp4")
        # качество важнее размера: карточка плоская, артефакты на узоре и
        # тексте видно сразу, а 3 секунды при crf 10 весят считанные сотни КБ
        save_mp4(frames, fps, path, crf=10, animation=True)
    elif fmt == "mp4":
        save_mp4(frames, fps, path)
    else:
        save_gif(frames, fps, path)
    return path


def normalize_fmt(value, default: str = "gif") -> str:
    """Поле «формат» из конфига: mp4 / video / видео / gif / гифка → mp4 или gif.

    «animation» (гифка Telegram: mp4 без звуковой дорожки) проходит как есть:
    иначе он превращался в mp4 и гифка собиралась со звуком.
    """
    text = str(value or "").strip().lower()
    if text == "animation":
        return "animation"
    if text.startswith("mp4") or text.startswith("vid") or "виде" in text:
        return "mp4"
    if text.startswith("gif") or "гиф" in text:
        return "gif"
    return default


def build(raw: str, *, size: int = 1024, fps: int = 60, fmt: str = "gif",
          output: str | None = None, footer: bool | None = None,
          caption: str = "", data_dir: str | None = None,
          pattern_layout: str = "app-square") -> str:
    card, lottie, pattern = load_assets(raw, data_dir)
    card.pattern_layout = pattern_layout
    if footer is False:
        card.name, card.number, card.author = "", None, ""
    if caption:
        card.caption = caption
    # генератор: mp4 пишется потоком, кадры не лежат в памяти
    fps = effective_fps(lottie, fps)
    frames = frame_stream(card, lottie, pattern, size=size, fps=fps)
    if output is None:
        # имя и расширение по фактическому контейнеру: если mp4 не собрать
        # (нет ffmpeg), получится .gif, и подпись не должна врать
        path = "gift." + ("mp4" if fmt == "mp4" else "gif")
        return save_animation(frames, fps, fmt, path)
    return save_animation(frames, fps, fmt, output)


def build_grid(refs: list, *, size: int = 1024, fps: int = 60,
               fmt: str = "gif", output: str | None = None,
               caption: str = "", max_tiles: int = 9,
               skipped: list | None = None) -> str:
    """Одна сетка из нескольких подарков вместо отдельной карточки на каждый.

    Если один подарок не открылся, сетка всё равно собирается из остальных:
    в `skipped` уходят пары (ссылка, причина).
    """
    refs = [ref for ref in refs if ref][:max_tiles]
    if not refs:
        raise ValueError("нет подарков для сетки")
    items = []
    for ref in refs:
        try:
            card, lottie, pattern = load_assets(ref)
        except Exception as exc:                   # noqa: BLE001
            if skipped is None:
                raise
            skipped.append((ref, str(exc)))
            continue
        card.caption = caption
        # у каждой плитки свой узор — без него сетка повторила бы один на всех
        items.append((card, lottie, pattern))
    if not items:
        raise ValueError("ни один подарок не открылся")
    fps = effective_fps(items[0][1], fps)
    frames = grid_frame_stream(items, size=size, fps=fps)
    path = output or "giftgrid-{}.{}".format(len(items), fmt)
    return save_animation(frames, fps, fmt, path)

GIFHELP_TEXT = """
{diamond:} <b>GiftGif</b> — подарок Telegram в анимированную карточку
<blockquote>Фон, узор, название и номер как в приложении · 60 fps · 3 секунды</blockquote>

{sparkles:} <b>Одна карточка</b>
<code>.gif</code> — реплаем на подарок в чате
<code>.gif t.me/nft/gingercookie-89402</code> — ссылкой
<code>.gif gingercookie-89402</code> — слизгом
<code>.gif 89402</code> — реплаем на подарок + номер: любой подарок того же вида

{bolt:} <b>Настройки прямо в команде</b>
<code>.gif видео</code> или <code>.gif mp4</code> — видео (играет в чате)
<code>.gif gif</code> — гифка (тяжелее, зато без звука и везде вставляется)
<code>.gif 512</code> — сторона карточки: 256, 512, 768, 1024, максимум 1536
Можно вместе: <code>.gif 512 gif</code>

{book:} <b>Своя подпись под карточкой</b>
<code>.gifttext С Новым годом, бро! 🎄</code> — запомнить текст
<code>.gifttext убрать</code> — снять подпись
<blockquote>Эмодзи в подписи рисуются на карточке, а не остаются квадратиками</blockquote>

{chat:} <b>Пачка подарков — по карточке на каждый</b>
Реплай на сообщение, где несколько подарков, и просто:
<code>.gif</code>
Или списком ссылок:
<code>.gif t.me/nft/x-1 t.me/nft/y-2 t.me/nft/z-3</code>
<blockquote>До 10 за раз, карточки уходят по очереди с паузой в секунду — так Telegram не режет отправку</blockquote>

{chart:} <b>Сетка — все подарки в одном видео</b>
<code>.gif сетка</code> — реплай на пачку или список ссылок
<blockquote>До 9 плиток (3×3), у каждой свой узор, цвет и подпись, модели двигаются одновременно</blockquote>
Своя сетка по ссылкам: <code>.gif сетка t.me/nft/x-1 t.me/nft/y-2</code>

{gear:} <b>Постоянные настройки</b> — <code>.cfg GiftGif</code>
<code>format</code> — по умолчанию mp4 или gif
<code>size</code> — сторона карточки
<code>fps</code> — 30 легче, 60 как в приложении
<code>pattern</code> — яркость узора в процентах (100 — как в приложении)
<code>footer</code> — показывать название и номер
<code>caption</code> — своя подпись, та же, что ставит <code>.gifttext</code>
<code>cache_minutes</code> — сколько держать готовую карточку в памяти

{lamp:} <b>Мелочи, которые помогают</b>
<blockquote>• Повторный запрос того же подарка отдаётся из кеша — почти мгновенно
• Подарок берётся со страницы Telegram: нужен интернет
• Размер меньше 512 собирается в разы быстрее
• Если Telegram отдал страницу-заглушку, модуль сам повторяет запрос</blockquote>

{info:} <b>Статус и проверка</b>
<code>.gif статус</code> — что установлено и что сейчас в настройках

{eye:} <b>Проверка на печеньках</b>
<code>.giftest</code> — собрать три Ginger Cookie и показать замеры: узор по третям,
габарит модели, живая ли анимация, плюс скриншот кадра
<blockquote>Свои подарки: <code>.giftest 89402 89403</code></blockquote>

{star:} <b>С чего начать</b>
1. Перешли себе подарок в «Избранное»
2. Ответь на него: <code>.gifttext Год змеи 🐍</code>
3. Ответь ещё раз: <code>.gif</code>
4. Для пачки — ответь на сообщение с несколькими подарками: <code>.gif сетка</code>
"""


@loader.tds
class GiftGif(loader.Module):
    """Подарок Telegram в GIF или MP4 — с фоном, узором, названием и номером"""

    strings = {"name": "GiftGif"}

    # Один семафор на весь модуль: рендер жрёт память, и две одновременные
    # сборки от разных людей легко упираются в лимит dyno. Ожидающие видят
    # сообщение «в очереди», а не тишину.
    _render_slot: asyncio.Semaphore | None = None

    def __init__(self) -> None:
        if self.__class__._render_slot is None:
            self.__class__._render_slot = asyncio.Semaphore(1)
        self._render_lock = self.__class__._render_slot
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "format", "mp4",
                "Формат по умолчанию: mp4 (легче и плавнее) или gif",
                validator=loader.validators.Choice(["mp4", "gif"]),
            ),
            loader.ConfigValue(
                "size", 1024,
                "Сторона карточки в пикселях (512 / 768 / 1024)",
                validator=loader.validators.Integer(minimum=64, maximum=1536),
            ),
            loader.ConfigValue(
                "fps", 60,
                "Кадров в секунду (30 — легче, 60 — как в приложении)",
                validator=loader.validators.Integer(minimum=5, maximum=60),
            ),
            loader.ConfigValue(
                "pattern", 100,
                "Яркость узора в процентах: "
                "100 — SVG без усиления (по умолчанию), 170 — явный",
                validator=loader.validators.Integer(minimum=40, maximum=250),
            ),
            loader.ConfigValue(
                "footer", True,
                "Показывать название и номер подарка под карточкой",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "caption", "",
                "Своя подпись под названием: эмодзи тоже рисуются "
                "(пример: С Новым годом! 🎄)",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "cache_minutes", 30,
                "Сколько минут держать готовую карточку подарка в памяти "
                "(0 — не кешировать)",
                validator=loader.validators.Integer(minimum=0, maximum=1440),
            ),
        )
        self._cache: dict = {}

    async def client_ready(self, client=None, db=None) -> None:
        if client is not None:
            self.client = client

    # ---------- вывод ----------

    @staticmethod
    async def _drop(message) -> None:
        """Убрать служебное сообщение «Собираю карточку…», если вышло."""
        try:
            await message.delete()
        except Exception:                              # noqa: BLE001
            pass

    async def say(self, message, text: str) -> None:
        try:
            await utils.answer(message, text, parse_mode="html")
        except Exception:
            # Повтор без parse_mode: Telegram покажет премиум-эмодзи по
            # document_id. Раньше здесь срезались ВСЕ теги — оставался пустой
            # 🛡/◻️ вместо иконки, потому что глифа внутри тега нет.
            plain = re.sub(r"<emoji document_id=\d+>([^<]*)</emoji>", r"\1", text)
            plain = re.sub(r"<[^>]+>", "", plain)
            await utils.answer(message, plain)

    def status(self) -> str:
        import importlib.util
        try:
            _size = int(self.config["size"])
        except Exception:                              # noqa: BLE001
            _size = 1024
        # карточка растягивается клиентом до ширины чата, поэтому 256 px
        # выглядят мылом: подсказываем, что размер меняется командой
        size_note = ("\n💡 <i>{0} px мало — в чате карточка растягивается. "
                     "Крупнее: <code>.gif 1024</code></i>").format(_size) \
            if _size < 768 else ""
        have_lottie = importlib.util.find_spec("rlottie_python") is not None
        try:
            ffmpeg_bin()
            have_ffmpeg = True
        except Exception:
            have_ffmpeg = False
        return ("🎁 <b>GiftGif</b> · <code>{}</code> · {} px · {} fps\n"
                "rlottie: {} · ffmpeg: {}\n\n"
                "<b>Команды:</b> <code>.gif</code> реплаем на подарок · "
                "<code>.gif t.me/nft/gingercookie-89402</code> · "
                "<code>.gif 256</code> · <code>.gif видео</code> · "
                "<code>.gif gif</code>\n"
                "<b>Своя подпись:</b> <code>.gifttext С Новым годом! 🎄</code>\n"
                "<b>Помощь:</b> <code>.gifhelp</code> · "
                "<b>Проверка:</b> <code>.giftest</code>\n"
                "<b>Пачка:</b> {} карточек или сетка {} плиток\n"
                "<b>Сейчас подписано:</b> {}\n"
                "<b>Узор:</b> {} % от яркости приложения\n"
                "<b>Версия:</b> <code>{}</code>"
                "{}").format(
                    self.config["format"], self.config["size"],
                    self.config["fps"],
                    "✅" if have_lottie else "❌ нет",
                    "✅" if have_ffmpeg else "❌ нет",
                    MAX_BATCH, MAX_TILES,
                    esc(str(self.get("caption", "") or "")) or "—",
                    self.config["pattern"], MODULE_VERSION, size_note)

    # ---------- вход: что именно рендерить ----------

    async def gift_ref(self, message, args: str) -> str | None:
        """Первый подарок: ссылка/номер из аргументов либо из реплая."""
        refs = await self.gift_refs(message, args)
        return refs[0] if refs else None

    async def gift_refs(self, message, args: str) -> list:
        """Все подарки: список ссылок в команде и/или пачка в реплае."""
        text = args or ""
        refs = re.findall(r"t\.me/nft/[A-Za-z0-9_-]+", text)
        if not refs:
            # слова-команды («сетка», «видео», «gif») подарком не считаем
            words = [w for w in text.split()
                     if not w.isdigit()
                     and w.lower() not in COMMAND_WORDS
                     and not re.fullmatch(r"\d{1,4}", w)]
            for word in words:
                if re.fullmatch(r"[A-Za-z0-9_-]*\d[A-Za-z0-9_-]*", word) or "-" in word:
                    refs = [word]
                    break
        reply = await message.get_reply_message()
        # Число — номер подарка, только если это не размер карточки: размеры
        # живут в 64…1536, номера подарков — почти всегда вне этого окна.
        # Иначе `.gif 512` реплаем собирал подарок «slug-512» и падал, а
        # `1024 89402` брал 1024 вместо номера.
        numbers = [n for n in re.findall(r"(?<!\d)(\d{1,9})(?!\d)", text)
                   if not SIZE_MIN <= int(n) <= SIZE_MAX]
        if numbers and reply is not None:
            slug = self.slug_from_message(reply)
            if slug:
                refs.append(f"{slug}-{numbers[0]}")
        if reply is not None:
            # из сообщения может торчать несколько подарков сразу
            refs.extend(self.slugs_from_message(reply))
        unique = []
        for ref in refs:
            if ref and ref not in unique:
                unique.append(ref)
        return unique

    def slugs_from_message(self, message) -> list:
        """Все подарки из сообщения: пачка, альбом, пересланные подарки."""
        found = []
        media = getattr(message, "media", None)
        for holder in (media, getattr(message, "action", None)):
            if holder is None:
                continue
            for name in ("gift", "star_gift", "stargift", "gifts"):
                value = getattr(holder, name, None)
                if value is None:
                    continue
                for gift in (value if isinstance(value, (list, tuple)) else [value]):
                    slug = getattr(gift, "slug", None)
                    if slug and str(slug) not in found:
                        found.append(str(slug))
        raw = getattr(message, "raw_text", "") or getattr(message, "message", "") or ""
        for slug in re.findall(r"t\.me/nft/([A-Za-z0-9_-]+)", raw):
            if slug not in found:
                found.append(slug)
        if not found:
            one = self.slug_from_message(message)
            if one:
                found.append(one)
        return found

    def slug_from_message(self, message) -> str | None:
        """Достать slug подарка из служебного сообщения Telegram."""
        for attr in ("action", "media"):
            action = getattr(message, attr, None)
            for name in ("gift", "star_gift", "stargift"):
                gift = getattr(action, name, None)
                slug = getattr(gift, "slug", None) if gift else None
                if slug:
                    return str(slug)
        raw = getattr(message, "raw_text", "") or ""
        link = re.search(r"t\.me/nft/([A-Za-z0-9_-]+)", raw)
        return link.group(1) if link else None

    # ---------- команда ----------

    @loader.command()
    async def gifttext(self, message):
        """| подпись под карточкой: .gifttext С Новым годом! · .gifttext — убрать"""
        raw = (utils.get_args_raw(message) or "").strip()
        if not raw or raw.lower() in ("сброс", "убрать", "clear", "-"):
            self.set("caption", "")
            return await self.say(
                message, "🧹 Свой текст убран — будет только название и номер.")
        if len(raw) > 200:
            return await self.say(
                message, f"❌ Слишком длинно ({len(raw)} символов, максимум 200)."
                )
        self.set("caption", raw)
        return await self.say(
            message, f"✅ Подпись сохранена:\n<b>{esc(raw)}</b>\n\nОна появится на всех "
                     "следующих карточках. Убрать: <code>.gifttext убрать</code>"
            )

    @loader.command()
    async def giftest(self, message):
        """| проверка на трёх печеньках: узор, модель, подпись + скриншот"""
        refs = list(SELFTEST_REFS)
        args = (utils.get_args_raw(message) or "").strip()
        if args:
            refs = [ref for ref in re.split(r"[\s,]+", args) if ref][:MAX_TILES]
        size = 512
        for word in args.split():
            if word.isdigit() and 128 <= int(word) <= 1536:
                size = int(word)
        if np is None:
            return await self.say(
                message, emoji(
                    "{warn:} Для <code>.giftest</code> нужен numpy — "
                    "сама сборка карточек работает и без него.\n"
                    "<code>pip install numpy</code>"))
        await self.say(
            message, emoji(
                "{hourglass:} <b>Проверяю</b> {} шт. — займёт десяток секунд…"
            ).format(len(refs)))
        try:
            async with self._render_lock:
                results, previews = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: build_selftest(refs, size=size, fps=30))
        except Exception as exc:                       # noqa: BLE001
            return await self.say(
                message, emoji("❌ Проверка не прошла: <code>{}</code>").format(esc(exc)))
        checks = selftest_verdict(results)
        failed = [name for name, ok, _ in checks if not ok]
        lines = []
        for row in results:
            top, middle, bottom = row["thirds"]
            lines.append(
                "• {} — узор {} / {} / {} %, модель {:.0%} плитки".format(
                    esc(row["name"]), top, middle, bottom, row["model"]["width"]))
        skipped = results[-1].get("skipped") or []
        if skipped:
            lines.append("⚠️ не проверено: " + ", ".join(
                "{} ({})".format(esc(ref), esc(reason)) for ref, reason in skipped))
        verdict = "✅ всё в норме" if not failed else "❌ есть проблемы: " + ", ".join(failed)
        report = emoji("{chart:} <b>Проверка GiftGif</b>\n") + "\n".join(lines) + "\n\n"
        report += "\n".join(
            "{} {} — {}".format("✅" if ok else "❌", name, detail)
            for name, ok, detail in checks)
        report += "\n\n" + emoji(verdict)
        folder = tempfile.mkdtemp(prefix="giftgif-")
        sheet_path = os.path.join(folder, "check.png")
        try:
            preview_sheet(previews).save(sheet_path)
            await message.client.send_file(
                message.chat_id, sheet_path, caption=report, parse_mode="html",
                force_document=False)
        except Exception:                              # noqa: BLE001
            await self.say(message, report)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    @loader.command()
    async def gifdiag(self, message):
        """| диагностика: какой путь отправки и что вернул сервер"""
        return await self._diag(message)

    async def _diag(self, message):
        await self.say(message, "🔬 Проверяю отправку гифки…")
        folder = tempfile.mkdtemp(prefix="giftgif-")
        path = os.path.join(folder, "diag.mp4")
        lines = ["<b>GiftGif — диагностика</b>"]
        try:
            async with self._render_lock:
                # размер как у обычной карточки: на 256 px клиент растягивает
                # картинку вчетверо, и диагностика выглядит «шакальной»
                diag_size = int(self.config["size"] or 1024)
                made = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: save_animation(
                        frame_stream(*load_assets(SELFTEST_REFS[0])[:3],
                                     size=diag_size, fps=30),
                        30, "animation", path))
            width, height, duration = GiftGif._video_meta(made)
            lines.append("• файл: {}×{}, {:.1f} c".format(width or "?", height or "?", duration))
            # 1) сообщение, отправленное прямым путём
            sent = await GiftGif._send_animation(message, made, "🔬 diag")
            if sent is None:
                lines.append("❌ прямой <code>sendMedia</code> НЕ прошёл → резерв")
            else:
                attrs = GiftGif._sent_attributes_sync(sent)
                lines.append("✅ путь: <code>messages.sendMedia</code>")
                lines.append("• сервер сохранил: <code>{}</code>".format(", ".join(attrs) or "—"))
                lines.append("• <b>Animated {}</b>".format(
                    "есть" if "DocumentAttributeAnimated" in attrs else "НЕТ"))
            # 2) что клиент видит у последнего сообщения в чате
            try:
                # без chat_id — «Избранное»: не важно, куда смотреть
                last = (await message.client.get_messages(message.chat_id, limit=1))[0]
                attrs = [type(a).__name__ for a in
                         (last.media.document.attributes if last.media else [])]
                lines.append("• клиент видит: <code>{}</code>".format(
                    ", ".join(attrs) or "нет документа"))
            except Exception as exc:                   # noqa: BLE001
                lines.append("• клиентский просмотр не удался: <code>{}</code>".format(
                    esc(type(exc).__name__)))
            lines.append("")
            lines.append("<i>Сервер и клиент — разные вещи: если сервер отдал "
                         "Animated, а в чате видео, это кеш клиента или "
                         "классификация на его стороне.</i>")
        except Exception as exc:                       # noqa: BLE001
            lines.append("❌ ошибка: <code>{}</code>".format(esc(exc)))
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        await self.say(message, "\n".join(lines))

    @loader.command()
    async def gifhelp(self, message):
        """| всё по полочкам: как делать карточку, пачку и сетку"""
        await self.say(message, emoji(GIFHELP_TEXT))

    @loader.command()
    async def gif(self, message):
        """| подарок → GIF/MP4: .gif реплаем · .gif t.me/nft/… · .gif 256 · пачка → .gif сетка"""
        args = (utils.get_args_raw(message) or "").strip()
        lower = args.lower()
        if lower in ("статус", "status", "?"):
            return await self.say(message, self.status())
        if lower in ("diag", "диаг", "диагностика"):
            return await self._diag(message)

        fmt = "gif" if ("gif" in lower.split() or "гиф" in lower) else None
        if "видео" in lower or "video" in lower or "mp4" in lower:
            fmt = "mp4"
        size = None
        for word in lower.split():
            if word.isdigit() and 64 <= int(word) <= 1536:
                size = int(word)
        as_grid = "сетка" in lower or "grid" in lower or "коллаж" in lower
        # поле «format» в конфиге заполняют руками: «mp4», «видео», «GIF» —
        # любое написание сводим к mp4/gif, иначе сравнение падало на регистре
        fmt = normalize_fmt(fmt or self.config["format"], "mp4")
        # .gif собираем не настоящим .gif, а mp4-анимацией: iOS показывает
        # .gif файлом со стрелкой «скачать», а mp4 с Animated — как гифку.
        # Формат остаётся "gif", меняется только контейнер.
        build_fmt = "animation" if fmt == "gif" else fmt
        size = size or int(self.config["size"])

        # «gif» — это тоже команда-слово: без него в нормализации «gif» из
        # аргументов терялся и уходил конфиг (обычно mp4) — то есть
        # `.gif gif` молча отдавал видео
        if fmt == "gif":
            build_fmt = "animation"

        refs = await self.gift_refs(message, args)
        if not refs:
            return await self.say(
                message,
                "🎁 <b>Как пользоваться</b>\n"
                "• Реплаем на подарок в чате: <code>.gif</code>\n"
                "• Ссылкой: <code>.gif t.me/nft/gingercookie-89402</code>\n"
                "• Размер и формат: <code>.gif 256</code>, "
                "<code>.gif видео</code>\n"
                "• Всё по полочкам: <code>.gifhelp</code>\n"
                "• Диагностика отправки: <code>.gif diag</code>\n"
                "• Пачка подарков: реплай на сообщение с несколькими подарками "
                "или список ссылок\n"
                "  — по карточке на подарок (до {}), "
                "<code>.gif сетка</code> — одна сетка (до {})\n\n".format(
                    MAX_BATCH, MAX_TILES) + self.status())

        if not as_grid and len(refs) > 1:
            return await self._send_batch(message, refs, size=size, fmt=build_fmt)
        if len(refs) > 1:
            return await self._send_grid(message, refs, size=size, fmt=build_fmt)

        if not refs:
            # нечего собирать: показываем версию и подсказку, а не ошибку —
            # по номеру версии сразу видно, обновился ли модуль
            return await self.say(message, emoji(
                "{rocket:} <b>GiftGif {ver}</b>\n"
                "Подарок не нашёл: пришли <code>.gif</code> реплаем на подарок, "
                "ссылкой <code>.gif t.me/nft/…</code> или запусти "
                "<code>.gif diag</code> — диагностика отправки.").format(
                    ver=MODULE_VERSION))

        ref = refs[0]
        busy = bool(getattr(self._render_lock, "locked", lambda: False)())
        await self.say(
            message, "🎁 Собираю карточку…" + ("\n⌛ Другая сборка ещё идёт — "
                                              "стану в очередь" if busy else ""))
        try:
            # Serialize heavy renders: two commands must not double RSS or
            # race over the shared pattern intensity setting.
            async with self._render_lock:
                path = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: self.build(ref, size=size, fmt=build_fmt))
        except Exception as exc:                       # noqa: BLE001
            return await self.say(
                message, f"❌ Не получилось: <code>{esc(exc)}</code>\n\n{self.status()}"
                )

        own = str(self.get("caption", "") or "")
        message._giftgif_animation = build_fmt == "animation"
        caption = (esc(own) + "\n" if own else "") + (
            f"🎁 <b>{esc(os.path.basename(path))}</b> · {size} px · "
            f"{os.path.getsize(path) / 1024:.0f} КБ")
        try:
            # видео — как видео (играет в чате), gif — через answer_file
            await self._deliver(message, path, caption)
        except Exception as exc:                       # noqa: BLE001
            await self.say(message, f"❌ Отправка не удалась: <code>{esc(exc)}</code>"
                           )
        else:
            await self._drop(message)          # карточка ушла — убираем «Собираю…»
        finally:
            try:
                os.unlink(path)
                os.rmdir(os.path.dirname(path))
            except Exception:
                pass

    # ---------- пачка подарков ----------

    def _base_caption(self, detail: str) -> str:
        own = str(self.get("caption", "") or "")
        return (esc(own) + "\n" if own else "") + detail

    @staticmethod
    def _video_meta(path: str, fps: int = 30) -> tuple:
        """Настоящие ширина, высота и длительность mp4 (без ffprobe).

        Клиент рисует плеер вместо гифки, когда размеры в атрибутах не
        совпадают с файлом, поэтому геометрию берём из самого видео.
        """
        width = height = 0
        duration = 0.0
        try:
            with open(path, "rb") as handle:
                head = handle.read(1 << 20)
            # tkhd из moov: ширина и высота лежат в 4 последних байтах
            for tag in (b"tkhd", b"mvhd"):
                pos = head.find(tag)
                if pos < 0:
                    continue
                start = pos + 4 + 4                 # version + flags
                if head[start] == 1:                # 64-битные времена
                    scale_at, dur_at, size_at = start + 16, start + 20, start + 84
                else:
                    scale_at, dur_at, size_at = start + 8, start + 12, start + 72
                scale = int.from_bytes(head[scale_at:scale_at + 4], "big")
                raw = int.from_bytes(head[dur_at:dur_at + 4], "big")
                if tag == b"mvhd" and scale and not duration:
                    duration = raw / scale
                if tag == b"tkhd":
                    width = int.from_bytes(head[size_at:size_at + 4], "big") >> 16
                    height = int.from_bytes(head[size_at + 4:size_at + 8], "big") >> 16
                if duration and width:
                    break
        except Exception:                              # noqa: BLE001
            pass
        if not (width and height):
            width = height = 0                    # пусть клиент возьмёт из файла
        if duration <= 0:
            duration = 3.0
        return width, height, duration

    def _animation_attributes(path: str, width: int = 0, height: int = 0,
                              duration: float = 3.0):
        """Атрибуты «гифки» Telegram: video + filename + animated.

        Ни nosound в атрибуте, ни nosound_video в запросе не ставим: с ними
        клиент как раз и рисует видео с таймером и иконкой звука (1.4.18).
        Порядок как у самого Telegram: video, filename, animated.
        """
        try:
            from hikkatl.tl import types as tl
            # w/h обязательны в конструкторе; карточка почти квадратная,
            # поэтому при неудачном разборе файла берём 512×512, а не теряем
            # атрибуты (без них клиент снова нарисует плеер)
            return [tl.DocumentAttributeVideo(
                        duration=max(1, int(round(duration))),
                        w=int(width) or 512, h=int(height) or 512,
                        round_message=False, supports_streaming=True),
                    tl.DocumentAttributeFilename(os.path.basename(path)),
                    tl.DocumentAttributeAnimated()]
        except Exception:                              # noqa: BLE001
            return None

    @staticmethod
    def _gif_attributes(path: str):
        """Атрибуты, которые превращают .gif в гифку Telegram, а не в файл.

        hikkatl в get_attributes не ставит DocumentAttributeAnimated (он
        появляется только при пересылке готового документа), поэтому .gif
        уходил документом — со стрелкой «скачать» и без автоплея. Telegram
        рисует гифку, когда у документа есть Animated. Берём настоящие
        классы из hikkatl, а не самодельные.
        """
        try:
            from hikkatl.tl import types as tl
            return [tl.DocumentAttributeAnimated(),
                    tl.DocumentAttributeFilename(os.path.basename(path))]
        except Exception:                              # noqa: BLE001
            return None

    @staticmethod
    async def _send_animation(message, path: str, caption: str = None):
        """Гифка напрямую: sendMedia + InputMediaUploadedDocument.

        Собираем запрос сами, как это делает pyrogram: video + filename +
        animated, без nosound_video. Так на результат не влияют ни откаты
        send_file, ни его обработка kwargs — вплоть до 1.4.19 атрибут
        Animated до сервера не доходил, и клиент рисовал видео с таймером.
        Возвращает ответ сервера либо None, если путь недоступен.
        """
        try:
            from hikkatl import tl as tl_root
            from hikkatl.tl import types as tl
        except Exception:                              # noqa: BLE001
            return None
        width, height, duration = GiftGif._video_meta(path)
        attributes = [tl.DocumentAttributeVideo(
                          duration=max(1, int(round(duration))),
                          w=int(width) or 512, h=int(height) or 512,
                          round_message=False, supports_streaming=True),
                      tl.DocumentAttributeFilename(os.path.basename(path)),
                      tl.DocumentAttributeAnimated()]
        try:
            uploaded = await message.client.upload_file(path)
            media = tl.InputMediaUploadedDocument(
                file=uploaded, mime_type="video/mp4", attributes=attributes)
            sent = await message.client(
                tl_root.functions.messages.SendMediaRequest(
                    peer=await message.client.get_input_entity(message.chat_id),
                    media=media, message=caption or "",
                    random_id=_random_id()))
            logger.debug("gif: sendMedia ok, attrs=%s",
                         GiftGif._sent_attributes_sync(sent))
            return sent
        except Exception:                              # noqa: BLE001
            logger.exception("gif: sendMedia не удался — резервный путь")
            return None

    @staticmethod
    def _sent_attributes_sync(sent) -> list:
        """Атрибуты, которые вернул сервер (для лога: дошёл ли Animated)."""
        try:
            for update in (getattr(sent, "updates", None) or []):
                document = getattr(getattr(getattr(update, "message", None),
                                           "media", None), "document", None)
                if document is not None:
                    return [type(a).__name__ for a in document.attributes]
        except Exception:                              # noqa: BLE001
            pass
        return []

    @staticmethod
    async def _upload(message, path: str, caption: str = None,
                      attributes=None) -> None:
        """Отправка файла с подписью; если клиент не принял — без подписи.

        Откаты идут по одному признаку за раз: сначала без подписи (старые
        сборки), потом без атрибутов (клиент не знает про attributes).
        """
        extra = {"attributes": attributes} if attributes else {}
        try:
            await message.client.send_file(
                message.chat_id, path, caption=caption, parse_mode="html",
                supports_streaming=True, force_document=False, **extra)
            return
        except TypeError:
            pass
        try:
            await message.client.send_file(
                message.chat_id, path, supports_streaming=True,
                force_document=False, **extra)
        except TypeError:
            await message.client.send_file(
                message.chat_id, path, supports_streaming=True,
                force_document=False)
        if caption:
            with contextlib.suppress(Exception):
                await utils.answer(message, caption, parse_mode="html")

    @staticmethod
    async def _deliver(message, path: str, caption: str) -> None:
        """Отправить готовый файл так, как это работает в Hikka.

        `message.respond(file=…, caption=…)` уходит не в send_file, а в
        send_message — отсюда «unexpected keyword argument 'caption'».
        Гифка уходит прямым запросом sendMedia с DocumentAttributeAnimated
        (см. _send_animation): через send_file атрибут до сервера не доходил,
        и клиент рисовал видео с таймером. Видео — обычным send_file.
        """
        if path.lower().endswith(".mp4"):
            animate = bool(getattr(message, "_giftgif_animation", False))
            if animate:                    # гифка: строго без звука + animated
                sent = await GiftGif._send_animation(message, path, caption)
                if sent is not None:
                    return
                width, height, duration = GiftGif._video_meta(path)
                attributes = GiftGif._animation_attributes(
                    path, width, height, duration)
                await GiftGif._upload(message, path, caption, attributes)
                return
            await GiftGif._upload(message, path, caption)
            return
        attributes = GiftGif._gif_attributes(path)
        try:
            await GiftGif._upload(message, path, caption, attributes)
        except Exception:                              # noqa: BLE001
            # атрибуты не приняли — лучше файл, чем ничего
            await GiftGif._upload(message, path, caption)

    async def _send_file(self, message, path: str) -> None:
        """Видео — как видео (играет в чате), GIF — как GIF."""
        await self._deliver(message, path, self._base_caption(
            f"🎁 <b>{esc(os.path.basename(path))}</b> · "
            f"{os.path.getsize(path) / 1024:.0f} КБ"))

    async def _send_batch(self, message, refs: list, *, size: int, fmt: str) -> None:
        """Пачка: по карточке на подарок, отправляются по очереди."""
        # fmt помнит, что собрали: "animation" — гифка, "mp4" — обычное видео
        message._giftgif_animation = fmt == "animation"
        dropped = max(0, len(refs) - MAX_BATCH)
        refs = refs[:MAX_BATCH]
        note = (f"\n(за раз собираю {MAX_BATCH}, остальные {dropped} — "
                f"следующей командой)") if dropped else ""
        await self.say(
            message, f"🎁 Собираю {len(refs)} карточки подряд…{note}")
        failures, done = [], 0
        for number, ref in enumerate(refs, 1):
            try:
                async with self._render_lock:
                    path = await asyncio.get_running_loop().run_in_executor(
                        None, lambda ref=ref: self.build(ref, size=size, fmt=fmt))
            except Exception as exc:                   # noqa: BLE001
                failures.append(f"{esc(ref)}: {esc(exc)}")
                continue
            try:
                await self._send_file(message, path)
                done += 1
            except Exception as exc:                   # noqa: BLE001
                failures.append(f"{esc(ref)}: {esc(exc)}")
            finally:
                try:
                    os.unlink(path)
                    os.rmdir(os.path.dirname(path))
                except Exception:
                    pass
            if number < len(refs):
                await asyncio.sleep(BATCH_DELAY)
        report = f"✅ Готово: {done} из {len(refs)}"
        if failures:
            report += "\n❌ Не вышло:\n" + "\n".join(failures)
        if done > 1:
            report += "\n\nСеткой в одном видео: <code>.gif сетка</code>"
        if done and not failures:
            await self._drop(message)          # всё ушло — служебное не нужно
        else:
            await self.say(message, report)

    async def _send_grid(self, message, refs: list, *, size: int, fmt: str) -> None:
        """Пачка: одна сетка плиток с подписями в одном видео."""
        message._giftgif_animation = fmt == "animation"
        dropped = max(0, len(refs) - MAX_TILES)
        refs = refs[:MAX_TILES]
        note = (f"\n(в сетку влезает {MAX_TILES}, остальные {dropped} — "
                f"через <code>.gif</code> по очереди)") if dropped else ""
        await self.say(
            message, f"🎁 Собираю сетку из {len(refs)} подарков…{note}")
        folder = tempfile.mkdtemp(prefix="giftgif-")
        # "animation" — не суффикс файла: save_animation сам даст .mp4
        path = os.path.join(folder, "grid." + (fmt if fmt == "gif" else "mp4"))
        caption = str(self.get("caption", "") or "")
        skipped: list = []
        try:
            async with self._render_lock:
                made = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: build_grid(refs, size=size, fmt=fmt,
                                             output=path, caption=caption,
                                             skipped=skipped))
        except Exception as exc:                       # noqa: BLE001
            shutil.rmtree(folder, ignore_errors=True)
            return await self.say(
                message, f"❌ Сетка не собралась: <code>{esc(exc)}</code>")
        if skipped:
            await self.say(
                message, "⚠️ В сетку не попало: " + ", ".join(
                    "<code>{}</code>".format(esc(ref)) for ref, _why in skipped))
        try:
            await self._send_file(message, made)
            await self._drop(message)      # сетка ушла — служебное сообщение убираем
        except Exception as exc:                       # noqa: BLE001
            await self.say(message, f"❌ Отправка не удалась: <code>{esc(exc)}</code>")
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    # ---------- сборка (в потоке, чтобы не вешать петлю) ----------

    def build(self, raw: str, *, size: int = 1024, fps: int | None = None,
              fmt: str = "gif", data_dir: str | None = None) -> str:
        global PATTERN_BOOST
        try:
            PATTERN_BOOST = max(40, int(self.config["pattern"])) / 100.0
        except Exception:
            PATTERN_BOOST = 1.00
        fmt = normalize_fmt(fmt, "mp4")
        fps = int(self.config["fps"]) if fps is None else fps
        caption = str(self.get("caption", "") or "")
        footer = bool(self.config["footer"])
        key = (resolve_slug(raw), size, fps, fmt, caption, footer,
               self.config["pattern"])
        if data_dir is None:
            self._purge_cache()
            hit = self._cache.get(key)
            if hit is not None:
                folder = tempfile.mkdtemp(prefix="giftgif-")
                path = os.path.join(folder, "gift." + fmt)
                try:
                    with open(path, "wb") as handle:
                        handle.write(hit[1])
                    return path
                except OSError:
                    shutil.rmtree(folder, ignore_errors=True)
        folder = tempfile.mkdtemp(prefix="giftgif-")
        path = os.path.join(folder, "gift." + fmt)
        try:
            made = build(raw, size=size, fps=fps, fmt=fmt, output=path,
                         footer=None if footer else False,
                         caption=caption, data_dir=data_dir)
        except BaseException:
            shutil.rmtree(folder, ignore_errors=True)
            raise
        if data_dir is None:
            try:
                self._remember(key, made)
            except Exception:
                pass
        return made

    # ---------- кеш: одна сборка на подарок ----------

    def _purge_cache(self) -> None:
        """Drop entries older than cache_minutes (0 — keep nothing)."""
        try:
            limit = int(self.config["cache_minutes"]) * 60
        except Exception:
            limit = 0
        now = time.time()
        for key, (made_at, blob) in list(self._cache.items()):
            if limit <= 0 or now - made_at > limit:
                self._cache.pop(key, None)

    def _remember(self, key: tuple, path: str) -> None:
        self._purge_cache()
        try:
            limit = int(self.config["cache_minutes"]) * 60
        except Exception:
            limit = 0
        if limit <= 0:
            return
        try:                       # один mp4 ≈ 1 МБ, gif на 1024/60 ≈ 33 МБ
            too_big = os.path.getsize(path) > CACHE_MAX_FILE
        except OSError:
            return
        if too_big:                # тяжелее лимита на файл — не держим в памяти
            return
        with open(path, "rb") as handle:
            blob = handle.read()
        self._cache[key] = (time.time(), blob)
        # и общий лимит по памяти: иначе 10 подарков по 33 МБ = OOM
        while len(self._cache) > 1 and sum(
                len(item[1]) for item in self._cache.values()) > CACHE_MAX_TOTAL:
            oldest = min(self._cache.items(), key=lambda item: item[1][0])[0]
            self._cache.pop(oldest, None)
