# Terminal YouTube Player (Python3)

Aplikasi pemutar musik/video YouTube berbasis terminal dengan Python3.

## Prasyarat

- Python 3.8+
- `yt-dlp`
- `mpv`

## Instalasi

Pilih salah satu cara di bawah sesuai OS.

### Python (venv + pip)

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

### Ubuntu/Debian

```
sudo apt update
sudo apt install -y mpv
python3 -m pip install -r requirements.txt
```

### Arch Linux

```
sudo pacman -S --noconfirm mpv yt-dlp
```

### macOS (Homebrew)

```
brew install mpv
python3 -m pip install -r requirements.txt
```

### Windows (winget)

```
winget install --id=mpv.mpv -e
py -m pip install -r requirements.txt
```

## Menjalankan

Mode interaktif:
```
./yt_player.py
```

Cari saja:
```
./yt_player.py search "kata kunci"
```

Putar hasil pertama (audio):
```
./yt_player.py play --search "kata kunci"
```

Putar video dari URL:
```
./yt_player.py play --video "https://www.youtube.com/watch?v=..."
```

## Catatan

- Jika `yt-dlp`/`mpv` tidak ditemukan, pastikan PATH sudah benar.
- Gunakan `--video` bila ingin menampilkan video, tanpa itu defaultnya audio.
# musikyutubcli
