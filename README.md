# 📦 IRISP: Fine-Grained Instance-Level Image Retrieval for Industrial Spare Parts
## 🧾 Overview

We present a large-scale dataset designed for **fine-grained object identification and retrieval in industrial scenarios**. The dataset contains **17,410 objects and 141,937 images**, including both mobile phone imagery and high-resolution machine-captured images.

Objects are captured across diverse backgrounds and viewing directions, with a strong focus on **subtle inter-object differences**. This makes the dataset particularly suitable for evaluating models on **fine-grained discrimination**, **domain generalization**, and **large-scale retrieval**.

[Paper](https://openaccess.thecvf.com/content/CVPR2026W/FGVC13/papers/Liu_Efficient_Fine-grained_Image_Retrieval_with_Vision_Foundation_Models_for_Industrial_CVPRW_2026_paper.pdf)


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
| Mobile Phone Query | 10,000 | 10,000 | Query construction |
| Mobile Phone Gallery | 10,000 | 10,000 | Gallery construction |
| Studio (Photo Machine) Gallery | 10,000 | 10,000 | Cross-domain gallery |

- Total mobile phone images: **131,937**  
- Studio (Photo Machine) images: **10,000**  

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
- Includes **cross-domain retrieval** (mobile phone → photo machine)

---

## 📥 Download

> [Link](https://data.dws.informatik.uni-mannheim.de/machinelearning/yushi_segment_any_repeated_object/) to download 

- All_Files.zip: training/validation/testing images
- All_Files_2.zip: Gallery and query images

---

## 📄 License

This dataset is licensed under the
Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

See the LICENSE file for details.
---

## 📌 Citation

```bibtex
@inproceedings{liu2026efficientfinegrained84,
  title = {{Efficient Fine-grained Image Retrieval with Vision Foundation Models for Industrial Objects}},
  author = {Yushi Liu and Christian Graf and Markus Spies and Margret Keuper},
  booktitle = {FGVC13 workshop Efficient Fine-grained Image Retrieval with Vision Foundation Models for Industrial Objects at CVPR 2026},
  year = {2026},
  url = {https://openaccess.thecvf.com/content/CVPR2026W/FGVC13/html/Liu_Efficient_Fine-grained_Image_Retrieval_with_Vision_Foundation_Models_for_Industrial_CVPRW_2026_paper.html}
}
