
# 📚 Momo Library Documentation

The **`momo`** library provides a unified interface for semantic search over **text**, **audio**, and **image** data using `chromadb` as the backend. It supports default and custom-trained embedding models and allows both single and batch file indexing.

---

## 📦 Installation

Install the library via pip:

```bash

pip install momo

```


## 🔧 Initialization

Start by initializing a `chromadb` client:

```python
import chromadb

client = chromadb.PersistentClient(path="path_to_save")
```

> ✅ **You can use any `chromadb` client (e.g., `EphemeralClient`, `HttpClient`, etc.), not just `PersistentClient`.**

> ⚠️ **Collection Name Constraint:**
> Each of `momo_document`, `momo_audio`, and `momo_image` **must use unique collection names**.
> You can reuse a collection name across default and custom models.

---

## 📝 Text Search: `momo_document`

### 1. Initialize Document Handler

```python
momo_docs = momo_document(client, "unique_text_collection")
```

### 2. Text Splitting and Mounting

```python
text = """Your long text block here..."""
docs = momo_docs.text_splitter(text, (150, 200), 20, False)

for id, doc in enumerate(docs):
    momo_docs.mount_document(doc, str(id))
```

* `(150, 200)`: Min/max character chunk size
* `20`: Overlap in characters
* `False`: If `True`, will retain sentence boundaries (optional feature)

### 3. Semantic Search

```python
result = momo_docs.find_similar_documents("search query here", k=3)
print(result)
```

---

## 🔊 Audio Search: `momo_audio`

### 1. Initialize Audio Handler

```python
momo_aud = momo_audio(client, "unique_audio_collection")
```

### 2. Mount Audio Files

```python
momo_aud.mount_audio("path/to/audio1.mp3")
momo_aud.mount_audio("path/to/audio2.mp3")
```

### 3. Batch Mounting

```python
momo_aud.mount_audio_batch("path/to/audio_directory")
```

### 4. Find Similar Audio

```python
result = momo_aud.find_similar_audio("path/to/query.mp3", k=3)
print(result)
```

---

### ✅ With Custom Audio Model

#### 1. Train Custom Audio Model

```python
x = "path/to/reference_audio"
y = "path/to/target_audio"
momo_aud.create_audio_model(directory_x=x, directory_y=y)
```

#### 2. Mount and Search with Custom Model

```python
model_path = "custom_trained_audio_embedding_model/audio_model.keras"

momo_aud.mount_audio("audio.mp3", model_path=model_path)
momo_aud.mount_audio_batch("audio_directory", model_path=model_path)

result = momo_aud.find_similar_audio("query.mp3", k=2, model_path=model_path)
print(result)
```

---

## 🖼️ Image Search: `momo_image`

### 1. Initialize Image Handler

```python
momo_img = momo_image(client, "unique_image_collection")
```

### 2. Mount Images

```python
momo_img.mount_image("path/to/image.jpg")
```

### 3. Batch Mounting

```python
momo_img.mount_image_batch("path/to/image_directory")
```

### 4. Find Similar Images

```python
result = momo_img.find_similar_image("path/to/query_image.jpg", k=3)
print(result)
```

---

### ✅ With Custom Image Model

#### 1. Train Custom Image Model

```python
x = "path/to/reference_images"
y = "path/to/target_images"
momo_img.create_image_model(directory_x=x, directory_y=y)
```

#### 2. Mount and Search with Custom Model

```python
model = "/path/to/custom_trained_image_embedding_model/image_model.keras"

momo_img.mount_image_batch("image_directory", model_path=model)

result = momo_img.find_similar_image("query.jpg", k=3, model_path=model)
print(result)
```

---

---

## ✅ Summary of Key Functions

| Operation          | Document                 | Audio                | Image                |
| ------------------ | ------------------------ | -------------------- | -------------------- |
| Mount file         | `mount_document`         | `mount_audio`        | `mount_image`        |
| Mount batch        | —                        | `mount_audio_batch`  | `mount_image_batch`  |
| Similarity search  | `find_similar_documents` | `find_similar_audio` | `find_similar_image` |
| Train custom model | —                        | `create_audio_model` | `create_image_model` |
| Use custom model   | —                        | via `model_path`     | via `model_path`     |

---

