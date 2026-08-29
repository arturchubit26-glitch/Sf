import asyncio, os, shutil, tempfile, subprocess
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

PRESETS={
 'house':('Хаус','highpass=f=35,acompressor=threshold=-18dB:ratio=3,bass=g=4,aecho=0.8:0.88:60:0.25'),
 'techno':('Техно','highpass=f=45,acompressor=threshold=-20dB:ratio=4,bass=g=6,aecho=0.8:0.9:90:0.2'),
 'jungle':('Джангл','highpass=f=45,atempo=1.08,bass=g=3,aecho=0.8:0.8:35:0.25'),
 'hiphop':('Хип-хоп','highpass=f=35,lowpass=f=15000,bass=g=5,acompressor=threshold=-16dB:ratio=3'),
 'lofi':('Лоу-фай','lowpass=f=6000,highpass=f=100,bass=g=2,aecho=0.8:0.7:80:0.35'),
 'poprock':('Поп-рок','highpass=f=40,acompressor=threshold=-18dB:ratio=2.5,treble=g=3,bass=g=3'),
 'neulovim':('Неуловимый Remix','highpass=f=35,lowpass=f=16500,bass=g=5,treble=g=3,acompressor=threshold=-18dB:ratio=3:attack=15:release=120,aecho=0.8:0.82:70:0.22'),
 'cherny_merin':('Из чёрного мерина Remix','highpass=f=38,lowpass=f=16000,bass=g=6,treble=g=2,acompressor=threshold=-19dB:ratio=3.5:attack=12:release=100,aecho=0.8:0.78:55:0.18'),
 'phonk':('Phonk','highpass=f=35,lowpass=f=15500,bass=g=8,treble=g=2,acompressor=threshold=-20dB:ratio=4:attack=8:release=100,acrusher=bits=12:mix=0.12'),
 'trap':('Trap','highpass=f=35,lowpass=f=16000,bass=g=7,treble=g=2,acompressor=threshold=-19dB:ratio=3.5:attack=10:release=110,aecho=0.8:0.82:80:0.16'),
 'drill':('Drill','highpass=f=32,lowpass=f=15000,bass=g=8,treble=g=1,acompressor=threshold=-20dB:ratio=4:attack=8:release=120,aecho=0.8:0.8:100:0.18'),
 'slap_house':('Slap House','highpass=f=38,lowpass=f=16000,bass=g=6,treble=g=3,acompressor=threshold=-18dB:ratio=4:attack=5:release=90,aecho=0.8:0.86:55:0.2'),
 'dnb':('Drum & Bass','highpass=f=40,lowpass=f=17000,bass=g=5,treble=g=3,acompressor=threshold=-19dB:ratio=4:attack=5:release=80'),
 'reggaeton':('Reggaeton','highpass=f=35,lowpass=f=16000,bass=g=6,treble=g=2,acompressor=threshold=-18dB:ratio=3:attack=12:release=100,aecho=0.8:0.84:70:0.18'),
 'amapiano':('Amapiano','highpass=f=38,lowpass=f=16000,bass=g=5,treble=g=2,acompressor=threshold=-18dB:ratio=2.5:attack=15:release=120,aecho=0.8:0.86:90:0.2'),
 'synthwave':('Synthwave','highpass=f=35,lowpass=f=16500,bass=g=4,treble=g=4,acompressor=threshold=-18dB:ratio=2.5:attack=15:release=120,aecho=0.8:0.9:120:0.25'),
 'slowed_reverb':('Slowed + Reverb','atempo=0.88,asetrate=44100*0.9,aresample=44100,aecho=0.8:0.82:140:0.35,bass=g=3'),
 'speed_up':('Sped Up','atempo=1.18,highpass=f=40,treble=g=3,acompressor=threshold=-18dB:ratio=2.5'),
 'bass_boost':('Bass Boost','highpass=f=30,lowpass=f=16000,bass=g=10,acompressor=threshold=-18dB:ratio=3'),
 'pitch_down':('Pitch Down','asetrate=44100*0.9,aresample=44100,bass=g=4,aecho=0.8:0.82:90:0.2'),
 'audio_8d':('8D Audio','highpass=f=35,stereotools=mlev=0.8,apulsator=mode=sine:hz=0.12:width=1,aecho=0.8:0.86:90:0.2'),
 'caucasus':('Кавказский Remix','highpass=f=40,lowpass=f=17000,bass=g=6,treble=g=3,acompressor=threshold=-19dB:ratio=3.5:attack=8:release=100,aecho=0.8:0.88:75:0.22,apulsator=mode=sine:hz=2:width=0.35')}


def kb():
 return InlineKeyboardMarkup([
  [InlineKeyboardButton('Хаус',callback_data='house'),InlineKeyboardButton('Техно',callback_data='techno')],
  [InlineKeyboardButton('Джангл',callback_data='jungle'),InlineKeyboardButton('Хип-хоп',callback_data='hiphop')],
  [InlineKeyboardButton('Лоу-фай',callback_data='lofi'),InlineKeyboardButton('Поп-рок',callback_data='poprock')],
  [InlineKeyboardButton('Неуловимый Remix',callback_data='neulovim')],
  [InlineKeyboardButton('Из чёрного мерина Remix',callback_data='cherny_merin')],
  [InlineKeyboardButton('Phonk',callback_data='phonk'),InlineKeyboardButton('Trap',callback_data='trap')],
  [InlineKeyboardButton('Drill',callback_data='drill'),InlineKeyboardButton('Slap House',callback_data='slap_house')],
  [InlineKeyboardButton('Drum & Bass',callback_data='dnb'),InlineKeyboardButton('Reggaeton',callback_data='reggaeton')],
  [InlineKeyboardButton('Amapiano',callback_data='amapiano'),InlineKeyboardButton('Synthwave',callback_data='synthwave')],
  [InlineKeyboardButton('Slowed + Reverb',callback_data='slowed_reverb')],
  [InlineKeyboardButton('Sped Up',callback_data='speed_up'),InlineKeyboardButton('Bass Boost',callback_data='bass_boost')],
  [InlineKeyboardButton('Pitch Down',callback_data='pitch_down'),InlineKeyboardButton('8D Audio',callback_data='audio_8d')],
  [InlineKeyboardButton('Кавказский Remix',callback_data='caucasus')]
 ])
async def start(u:Update,c:ContextTypes.DEFAULT_TYPE): await u.message.reply_text('Отправьте музыку MP3/WAV/M4A, затем выберите стиль.',reply_markup=kb())
async def choose(u:Update,c:ContextTypes.DEFAULT_TYPE):
 q=u.callback_query; await q.answer(); c.user_data['preset']=q.data; await q.message.reply_text(f'Выбран стиль: {PRESETS[q.data][0]}. Теперь отправьте аудиофайл.')
async def audio(u:Update,c:ContextTypes.DEFAULT_TYPE):
 d=u.message.audio or u.message.document; name=getattr(d,'file_name',None) or 'input.mp3'; ext=Path(name).suffix.lower()
 if getattr(d,'file_size',0) > 20*1024*1024: return await u.message.reply_text('Файл слишком большой. Telegram Bot API позволяет боту скачивать файлы до 20 МБ.')
 if ext not in {'.mp3','.wav','.m4a','.ogg','.flac'}: return await u.message.reply_text('Поддерживаются MP3, WAV, M4A, OGG и FLAC.')
 work=Path(tempfile.mkdtemp(prefix='remix-')); src=work/Path(name).name; out=work/'remix.mp3'
 try:
  await (await c.bot.get_file(d.file_id)).download_to_drive(src); label,af=PRESETS.get(c.user_data.get('preset','house'),PRESETS['house'])
  p=await asyncio.create_subprocess_exec('ffmpeg','-y','-i',str(src),'-af',af,'-codec:a','libmp3lame','-b:a','192k',str(out),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  await asyncio.wait_for(p.communicate(),timeout=120)
  if p.returncode!=0 or not out.exists(): return await u.message.reply_text('Не удалось обработать аудио.')
  await u.message.reply_audio(out.open('rb'),caption=f'Готово: {label}')
 except asyncio.TimeoutError: await u.message.reply_text('Обработка заняла больше 120 секунд.')
 except Exception as e: await u.message.reply_text(f'Ошибка: {e}')
 finally: shutil.rmtree(work,ignore_errors=True)
app=Application.builder().token(os.environ['BOT_TOKEN']).build(); app.add_handler(CommandHandler('start',start)); app.add_handler(CallbackQueryHandler(choose)); app.add_handler(MessageHandler(filters.AUDIO|filters.Document.ALL,audio))
app.run_polling()
