
# NexFace

**NexFace** is a modular face recognition library built on top of modern deep learning models. It supports face detection, embedding extraction, clustering, and identification using ONNX, FaceNet, and Scikit-learn-compatible algorithms.

---

## 🚀 Features

- ✅ **Face Detection** (YuNet with OpenCV & ONNX)
- ✅ **Face Embedding Extraction** (FaceNet `.h5`)
- ✅ **Clustering** (DBSCAN & HDBSCAN)
- ✅ **Recognition via Prototypes**
- ✅ Clean and extensible object-oriented design

---

## 🧠 How It Works

1. **Face Detection**:  
   Uses YuNet ONNX model via `cv2.FaceDetectorYN`.

2. **Embedding Extraction**:  
   FaceNet model (Keras `.h5`) extracts 128-D facial embeddings.

3. **Clustering & Prototypes**:  
   Cluster face embeddings via DBSCAN or HDBSCAN.  
   Compute cluster centers (prototypes) for recognition.

4. **Recognition**:  
   New face embeddings are compared against cluster prototypes using cosine or Euclidean similarity.

---
> You can also install using `pip install -r requirements.txt`.

---

## 📌 To Do

- [ ] Add ArcFace / InsightFace support
- [ ] Improve alignment and augmentation
- [ ] Evaluation metrics (precision, recall, etc.)

---

## 🧑‍💻 Author

**Fatih Dağdeviren**  
[fatihdagdeviren21@gmail.com](mailto:fatihdagdeviren21@gmail.com)

GitHub: [github.com/fatihdagdeviren](https://github.com/fatihdagdeviren)
