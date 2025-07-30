# 🪄 bluer-algo

🪄 `@algo` carries AI algo.  

```bash
pip install bluer-algo
```

|   |
| --- |
| [`image classifier`](./bluer_algo/docs/image-classifier.md) [![image](https://github.com/kamangir/assets/raw/main/fruits-365-2025-06-27-97buak/grid.png?raw=true)](./bluer_algo/docs/image-classifier.md) an image classifier. |

```mermaid
graph LR
    image_classifier_dataset_ingest["@image_classifier<br>dataset<br>ingest<br>count=&lt;100&gt;,source=fruits_360<br>&lt;dataset-object-name&gt;"]

    image_classifier_dataset_review["@image_classifier<br>dataset<br>review -<br>&lt;dataset-object-name&gt;"]

    image_classifier_model_train["@image_classifier<br>model<br>train -<br>&lt;dataset-object-name&gt;<br>&lt;model-object-name&gt;"]

    fruits_360["🛜 fruits_360"]:::folder
    dataset_object["📂 dataset object"]:::folder
    model_object["📂 model object"]:::folder

    fruits_360 --> image_classifier_dataset_ingest
    image_classifier_dataset_ingest --> dataset_object

    dataset_object --> image_classifier_dataset_review

    dataset_object --> image_classifier_model_train
    image_classifier_model_train --> model_object

    classDef folder fill:#999,stroke:#333,stroke-width:2px;
```

---

> for the [Global South](https://github.com/kamangir/bluer-south).

---


[![pylint](https://github.com/kamangir/bluer-algo/actions/workflows/pylint.yml/badge.svg)](https://github.com/kamangir/bluer-algo/actions/workflows/pylint.yml) [![pytest](https://github.com/kamangir/bluer-algo/actions/workflows/pytest.yml/badge.svg)](https://github.com/kamangir/bluer-algo/actions/workflows/pytest.yml) [![bashtest](https://github.com/kamangir/bluer-algo/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/bluer-algo/actions/workflows/bashtest.yml) [![PyPI version](https://img.shields.io/pypi/v/bluer-algo.svg)](https://pypi.org/project/bluer-algo/) [![PyPI - Downloads](https://img.shields.io/pypi/dd/bluer-algo)](https://pypistats.org/packages/bluer-algo)

built by 🌀 [`bluer README`](https://github.com/kamangir/bluer-objects/tree/main/bluer_objects/README), based on 🪄 [`bluer_algo-4.207.1`](https://github.com/kamangir/bluer-algo).
