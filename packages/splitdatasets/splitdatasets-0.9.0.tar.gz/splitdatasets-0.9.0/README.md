
# SplitDatasets

**SplitDatasets** — это CLI-инструмент на Python для работы с изображениями и разметками: выбор случайных изображений, разбиение на обучающую/валидационную/тестовую выборки как в локальной файловой системе, так и в S3.

## 📦 Установка

### 🔹 Установка с помощью [uv](https://github.com/astral-sh/uv)

```bash
uv pip install -e .
```

> Установит проект в режиме разработки (editable).

### 🔹 Установка глобально с помощью [pipx](https://github.com/pypa/pipx)

```bash
pipx install .
```

> Если пакет уже установлен, но вы внесли изменения в код — переустановите:

```bash
pipx uninstall splitdatasets
pipx install .
```

---

## 🚀 Использование

### 1. Случайный выбор изображений

Копирует случайные изображения из `source_dir` в `target_dir`, с возможным переименованием.

```bash
random-move SOURCE_DIR TARGET_DIR [--count 100] [--prefix PREFIX] [--extensions .jpg .jpeg .png] [--seed 42]
```

**Пример:**

```bash
random-move ./images ./sample --count 50 --prefix selected --seed 123
```

---

### 2. Разделение локального датасета

Разбивает изображения на поддиректории `images/train`, `images/val`, `images/test` и `labels/...`

```bash
split-dataset-local SOURCE_DIR TARGET_DIR [--labels_dir LABELS_DIR] [--train_ratio 0.7] [--val_ratio 0.2] [--test_ratio 0.1] [--seed 42]
```

**Пример:**

```bash
split-dataset-local ./dataset/images ./dataset_split --labels_dir ./dataset/labels --seed 42
```

---

### 3. Разделение датасета в S3 (MinIO)

Разделяет изображения и метки, находящиеся в хранилище S3, по тем же правилам.

```bash
split-dataset-s3 --bucket BUCKET \
                 --source_prefix SOURCE_PREFIX \
                 --target_prefix TARGET_PREFIX \
                 --endpoint http://IP:PORT \
                 --access_key ACCESS \
                 --secret_key SECRET \
                 [--labels_prefix LABELS_PREFIX] \
                 [--train_ratio 0.7] \
                 [--val_ratio 0.2] \
                 [--test_ratio 0.1] \ 
                 [--seed 42]
```

**Пример:**

```bash
split-dataset-s3 --bucket mybucket \
                 --source_prefix raw/images \
                 --target_prefix splits \
                 --endpoint http://localhost:9000 \
                 --access_key myaccesskey \
                 --secret_key mysecretkey \
                 --labels_prefix raw/labels \
                 --seed 123
```

---

## 🧱 Структура проекта

```
splitdatasets/
├── split_dataset/
│   ├── select_and_move_images.py
│   ├── split_dataset.py
│   ├── split_dataset_s3.py
│   └── utils.py
├── pyproject.toml
└── README.md
```

## 🛠 Зависимости

- Python >= 3.12
- `boto3` для работы с S3
- `uv` и `pipx` (для удобства установки)

---

## 📝 Лицензия

[MIT License](LICENSE) © 2025