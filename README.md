# 📦 IRISP: Fine-Grained Instance-Level Image Retrieval for Industrial Spare Parts

## 🧾 Overview

We present a large-scale dataset designed for **fine-grained object identification and retrieval in industrial scenarios**. The dataset contains **17,410 objects and 141,937 images**, including both mobile phone imagery and high-resolution machine-captured images.

Objects are captured across diverse backgrounds and viewing directions, with a strong focus on **subtle inter-object differences**. This makes the dataset particularly suitable for evaluating models on **fine-grained discrimination**, **domain generalization**, and **large-scale retrieval**.

---

## 🚀 Key Features

- **Large-scale**: 17K+ objects, 140K+ images  
- **Fine-grained differences**: visually similar industrial parts (e.g., springs, cables, PCBs)  
- **Diverse conditions**: multiple backgrounds and viewpoints per object  
- **Cross-domain setup**: mobile phone vs machine imagery  
- **Two benchmarks**:
  - Binary Image Identification  
  - Object Retrieval (large-scale, single-match setting)  

---

## 📊 Dataset Composition

| Split | #Objects | #Images | Description |
|------|--------|--------|------------|
| Train | 7,395 | 67,844 | Used for model training |
| Val   | 15    | 461    | Dense validation set |
| Test  | 9,526 | 37,520 | Used for evaluation |
| Retrieval (mobile) | 10,000 | 10,000 | Query/gallery construction |
| Retrieval (machine) | 10,000 | 10,000 | Cross-domain gallery |

- Total mobile images: **131,937**  
- Machine images: **10,000**  

---

## 🧪 Benchmarks

### 1️⃣ Binary Image Identification

- Task: Predict whether two images belong to the same object  
- Data:
  - 40K training pairs  
  - 4K validation pairs  
  - 20K testing pairs  
- Balanced positive/negative samples  
- Emphasis on **fine-grained discrimination**

---

### 2️⃣ Object Retrieval

- Each query has **exactly one correct match**  

#### Gallery Settings

- **Random Gallery**: one randomly selected image per object  
- **Challenging Gallery**: one image per object with large viewpoint and background variation  

#### Metrics

- **Recall@K** (K = 1, 10, 100)  
- **MRR@K** (truncated ranking quality)

---

## ⚠️ Why This Dataset is Challenging

- Objects differ only in **subtle geometric or structural details**  
- Differences are often **hard to describe in language** and require domain knowledge  
- Many objects are **rare in pretrained datasets**, limiting prior knowledge  
- Strong **viewpoint and background variation**  
- Includes **cross-domain retrieval** (mobile → machine)

---

## 📥 Download

> TBA

- Full dataset  
- Train/Val/Test splits  
- Retrieval benchmarks  

---

## 📄 License
CC-BY-SA-4.0
---

## 📌 Citation

```bibtex
@dataset{your_dataset_2026,
  title={Industrial Spare Parts Dataset for Fine-Grained Identification and Retrieval},
  author={Your Name},
  year={2026}
}
