# 🖼️ ExtractedFrames

**ExtractedFrames** — это CLI-инструмент для нарезки видео на кадры с возможностью параллельной обработки, настройки шага, интервала времени, задания префикса и выбора выходной директории.

---

## 📦 Установка

### 🔹 Установка с помощью [uv](https://github.com/astral-sh/uv)

```bash
uv pip install -e .
```

> Это установит проект в режиме разработки (editable).

### 🔹 Установка глобально с помощью [pipx](https://github.com/pypa/pipx)

```bash
pipx install .
```

> Если пакет уже установлен, но вы внесли изменения в код — переустановите:

```bash
pipx uninstall extractedframes
pipx install .
```

---

## 🚀 Использование

После установки команда будет доступна как:

```bash
extract-frames --videos VIDEO1.mp4 VIDEO2.mp4 \
               --output ./frames \
               --prefix tool_frames \
               --step 30 \
               --start 5 \
               --end 60
```

### 🔧 Аргументы:

| Аргумент          | Тип       | Описание                                                                 |
|-------------------|-----------|--------------------------------------------------------------------------|
| `--videos`        | list path | Пути до одного или нескольких видеофайлов (обязательно)                 |
| `--output`        | path      | Путь к директории для сохранения кадров (обязательно)                   |
| `--prefix`        | str       | Префикс для имен кадров (по умолчанию: `frame`)                         |
| `--step`          | int       | Шаг между кадрами (по умолчанию: `10`)                                  |
| `--start`         | int       | Время начала в секундах (по умолчанию: `0`)                             |
| `--end`           | int       | Время конца в секундах (0 = до конца; по умолчанию: `0`)                |
| `--reserve`       | int       | Кол-во логических ядер, которые нужно оставить системе (по умолчанию: `1`) |

---

## 🔄 Обновление

Если вы вносите изменения и хотите, чтобы они применились:

```bash
pipx install . --force
```

Или для полной переустановки:

```bash
pipx uninstall extractedframes
pipx install .
```

---

## 🧪 Пример

```bash
extract-frames \
  --videos "/videos/sample1.mp4" "/videos/sample2.mp4" \
  --output "./extracted" \
  --prefix session1 \
  --step 15 \
  --start 2 \
  --end 60
```

---

## 🛠 Разработка

Запуск напрямую через `uv`:

```bash
uv run extract-frames --videos ... --output ...
```

---

## 📁 Структура проекта

```text
extracted_frames/
│   ├── __init__.py
│   └── main.py          ← основная точка входа
pyproject.toml           ← зависимости и конфигурация CLI
README.md                ← этот файл
```

---

## 📃 Лицензия

[MIT License](LICENSE) © 2025 Daniel Robotics