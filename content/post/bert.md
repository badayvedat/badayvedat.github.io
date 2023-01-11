---
author: Vedat Baday
title: Turkish Sentiment Analysis using Hugging Face
date: 2022-01-06
description: A brief guide to Turkish sentiment analysis with Hugging Face
summary: " "
tags: ["hugging-face", "deep-learning"]
---

In this blog post, we will do Turkish sentiment analysis using Hugging Face. Although models are frequently developed on English sources, there is no blog post in Turkish that is explained in a simple and clear language. We will explain sufficient and important details in this blog post.


These blog post consists of 10 sections:

* Sentiment analysis
* Explanation of BERT
* Setting up
* Turkish text data collection  and preprocessing
* How to select features from the text data
* Build sentiment analysis model using Hugging Face 
* Evaluation of the model before training
* Train the model
* Evaluation of the Model
* References

## Sentiment Analysis
Sentiment Analysis is one of the natural language processing techniques to identify and classify information.

Sentiment Analysis has a wide range of practical applications, some of the practical examples are; social media applications, online reviews, healthcare systems, user behaviour analysis, recommendation systems. 

The information can be analysed with the Sentiment Analysis methods are quite range, as can be predictable from the extensive number of practical areas. The analysis of the whole or each information is far beyond of the scope of this blog post. Instead, in this blog post we will focus on the most common and accessible data, in the terms of data volume, variety, and considering the GDPR (General Data Protection Regulation), that is text data.

Text data can be collected from variety of different platforms, such as social media apps, e-commerce websites, streaming services, booking services (e.g., hotel). The number of users and products (e.g., movies, tv-series for streamin services) are in millions and even billions nowadays, and the text data generated in these platforms are enormous, making these platforms a first-place in terms of data collection and scraping.

The text data scraped and collected from the various platforms can contain many sentiments. However, most of the research focuses on three distinct label when classifying the text data samples. Namely, ***positive*** to refer to samples that mostly contain positive sentiment, ***negative*** to refer to samples that contain mostly negative sentiment, and ***neutral*** to refer to samples that it is mostly do not contain positive neither negative sentiments, but as the terms explains, contain neutral sentiments.

Examples for the each sentiment type:

*   BEN BU FÄ°LME 10 YILDZ DAN DA FAZLA SI NI TAM OLARAK 100 YILDIZ VERÄ°YORUM Ã‡ÃœNKÃœ ACAYÄ°P GÃœZEL BU FÄ°LMÄ° HARÄ°KA FLÄ°MDÄ°R ğŸ‘ŒğŸ‘ŒğŸ‘ŒğŸ‘ŒğŸ‘Œ =>  **Positive**
*   Bu film ne anlatÄ±yo? HiÃ§bir ÅŸey anlamadÄ±m. => **Negative**
*   Ã‡Ã¼nkÃ¼ aranan tapÄ±nak bu bÃ¶lgededir .	=> **Neutral**

## What is BERT? [1]

 It is a new model of language representation. BERT stands for Bidirectional Transformers for Language Understanding. By concurrently conditioning on both left and right context in all layers, BERT is aimed to pretrain deep bidirectional representations from unlabeled text, in contrast to recent language representation models. BERT consists of bunch of Transformer encoders, not decoders.


There are currently two methods for applying language representations that have already been trained to downstream tasks: 
* feature-based 
* fine-tuning

In previous studies, unidirectional language modeling restricts the capabilities of pre-trained representations particularly for the fine-tuning approaches. BERT overcomes this constraint by using the **masked language model (MLM)** to enable pre-trained deep bidirectional representations. 

Additionally, they demonstrated how the application of pre-trained representation can considerably lessen the requirement for task-specific structures.

### Masked Language Modeling (MLM)

The purpose of the masked language model is to predict the original word of a masked word based on its context only after randomly masking some tokens from the input so that they pre-train the deep bidirectional Transformer.

![Mask-BERT.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfgAAABkCAIAAADlmbWkAAAACXBIWXMAAAsTAAALEwEAmpwYAAALG2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIiB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIyLTExLTA4VDE5OjM5OjI2KzAzOjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDIyLTExLTA4VDE5OjQ0OjMyKzAzOjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMi0xMS0wOFQxOTo0NDozMiswMzowMCIgcGhvdG9zaG9wOkNvbG9yTW9kZT0iMyIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6N2Y3NjI2ZjYtMmFkMC04NjRjLWE0ZWMtM2YyNGFlOGI1YjFkIiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6ZTk4YTQxM2ItZmNhMy0xMTRiLWFiMzMtZDA1NzU4NDEyNWQ1IiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6ZDA5OTBkMmItNTcxYy01NDQ2LWI0YjctYTQzNjI5NjhkZjk1IiB0aWZmOk9yaWVudGF0aW9uPSIxIiB0aWZmOlhSZXNvbHV0aW9uPSI3MjAwMDAvMTAwMDAiIHRpZmY6WVJlc29sdXRpb249IjcyMDAwMC8xMDAwMCIgdGlmZjpSZXNvbHV0aW9uVW5pdD0iMiIgZXhpZjpDb2xvclNwYWNlPSI2NTUzNSIgZXhpZjpQaXhlbFhEaW1lbnNpb249IjExODUiIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyMzQiPiA8cGhvdG9zaG9wOlRleHRMYXllcnM+IDxyZGY6QmFnPiA8cmRmOmxpIHBob3Rvc2hvcDpMYXllck5hbWU9IkJ1IGZpbG0gbmUga2FkYXIgZGEgZ8O8emVsbWnFnywgw6dvayBiZcSfZW5kaW0hIiBwaG90b3Nob3A6TGF5ZXJUZXh0PSJCdSBmaWxtIG5lIGthZGFyIGRhIGfDvHplbG1pxZ8sIMOnb2sgYmXEn2VuZGltISIvPiA8cmRmOmxpIHBob3Rvc2hvcDpMYXllck5hbWU9IkJ1IFttYXNrXSBuZSBrYWRhciBbbWFza10gZ8O8emVsbWnFnywgw6dvayBbbWFza10hIiBwaG90b3Nob3A6TGF5ZXJUZXh0PSJCdSBbbWFza10gbmUga2FkYXIgW21hc2tdIGfDvHplbG1pxZ8sIMOnb2sgW21hc2tdISIvPiA8L3JkZjpCYWc+IDwvcGhvdG9zaG9wOlRleHRMYXllcnM+IDx4bXBNTTpIaXN0b3J5PiA8cmRmOlNlcT4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNyZWF0ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZDA5OTBkMmItNTcxYy01NDQ2LWI0YjctYTQzNjI5NjhkZjk1IiBzdEV2dDp3aGVuPSIyMDIyLTExLTA4VDE5OjM5OjI2KzAzOjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOmM4ZTc2ZDU2LTQ4NWItN2Q0ZC1hZDMxLTFkZjYxM2MxNmFkNSIgc3RFdnQ6d2hlbj0iMjAyMi0xMS0wOFQxOTo0NDozMiswMzowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTggKFdpbmRvd3MpIiBzdEV2dDpjaGFuZ2VkPSIvIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjb252ZXJ0ZWQiIHN0RXZ0OnBhcmFtZXRlcnM9ImZyb20gYXBwbGljYXRpb24vdm5kLmFkb2JlLnBob3Rvc2hvcCB0byBpbWFnZS9wbmciLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImRlcml2ZWQiIHN0RXZ0OnBhcmFtZXRlcnM9ImNvbnZlcnRlZCBmcm9tIGFwcGxpY2F0aW9uL3ZuZC5hZG9iZS5waG90b3Nob3AgdG8gaW1hZ2UvcG5nIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo3Zjc2MjZmNi0yYWQwLTg2NGMtYTRlYy0zZjI0YWU4YjViMWQiIHN0RXZ0OndoZW49IjIwMjItMTEtMDhUMTk6NDQ6MzIrMDM6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8L3JkZjpTZXE+IDwveG1wTU06SGlzdG9yeT4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6YzhlNzZkNTYtNDg1Yi03ZDRkLWFkMzEtMWRmNjEzYzE2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)

## Setting up

In this section, the necessary libraries are imported.

```bash
!pip install transformers
```
```python3
from google.colab import drive
drive.mount('/content/gdrive')
```

```python3
import os
import transformers
import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
```

```python3
# import data visualization libraries
import matplotlib.pyplot as plt 
import seaborn as sns
sns.set_style("darkgrid")
```

```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

from tqdm.auto import tqdm
```


```python
# set random seed
RANDOM_SEED = 12
np.random.seed(RANDOM_SEED)
_ = torch.manual_seed(RANDOM_SEED)
```

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```
```python
DATA_ROOT = "/content/gdrive/MyDrive/BBM467/BPP/Dataset"
```

## Turkish Text Data Collection  and Preprocessing

You can access the dataset we use [here](https://huggingface.co/datasets/winvoker/turkish-sentiment-analysis-dataset)

This dataset is combination of other datasets which includes:


*   wiki: Turkish wikipedia dataset.
*   urun_yorumlari: Product reviews dataset
* HUMIR : The dataset that is created by Hacettepe University, Multimedia Information Retrieval Laboratory.
* tweet_pn: Twitter dataset
* magaza_yorumlari: Store reviews dataset
* random: Random text inputs such as "Lorem ipsum dolor sit amet."



```python
df = pd.read_csv(os.path.join(DATA_ROOT ,"train.csv"))
df.head()
```

As you can see below, we have about 441k samples. There are no missing values in the dataset. """
```python3
df.info()
```
```python3
plt.figure(figsize =(5,5))
plt.xticks(rotation=45, ha="right")
sns.countplot(df.dataset)
```

The dataset mostly consists of product reviews and wikipedia texts."""

```python3
plt.figure(figsize =(5,5))
plt.xticks(rotation=45, ha="right")
sns.countplot(x=df.label)
plt.show()
```

We can say that the number of positive data is very high compared to the negative data. In this respect, the balance is not preserved in the data. Positive labeled data predominates."""

```python3
df.groupby(['dataset', 'label']).size()
```

As expected, the data from wikipedia contains only neutral data. Wikipedia usually contains scientific, provable and objective information. This information does not reflect any sentiment."""

```python3
SENTIMENT_TO_LABEL = {
    "Negative": 0,
    "Notr": 1,
    "Positive": 2,
}

LABEL_TO_SENTIMENT = {
    label: sentiment
    for (sentiment, label) in SENTIMENT_TO_LABEL.items()
}
```

```python3
df['label'] = df['label'].replace(SENTIMENT_TO_LABEL)
df.head()
```

Split the dataset into training and testing sets.

```python3
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=RANDOM_SEED)

X_train[:3]
```

## How to select features from the text data

There are a few ways you can select features from text data:

1. Bag-of-words: One simple way to represent text data is to use the bag-of-words model, which involves creating a vocabulary of all the unique words in the text data and encoding each document as a numerical feature vector where each element denotes the frequency of a specific word's occurrence in the document.

2. Term frequency-inverse document frequency (TF-IDF): which considers a word's frequency in a document as well as its rarity across all documents, is another way to represent text data.  This can be useful when you want to give more weight to rare words that may be more indicative of the content of a document.

3. Word embeddings: You can use word embeddings, which are dense, continuous-valued vector representations of words, as a substitute for numerical feature vectors to represent text data. These embeddings are helpful for tasks like language translation and text classification because they can capture the context and meaning of words in the text data.

## Build Turkish Sentiment Classifier using Hugging Face

Select a transformer model that has been pre-trained on a large dataset and fine-tuned for sentiment analysis from the Hugging Face library. RoBERTa, XLNet, and BERT are a few options.

```python3
from transformers import BertTokenizer, AutoTokenizer, BertForSequenceClassification

# Choose a tokenizer
tokenizer = AutoTokenizer.from_pretrained('dbmdz/bert-base-turkish-cased', use_fast=True)
```

Create a SentimentDataset class.

```python3
class SentimentDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, device='cpu'):
        self.texts = texts
        self.labels = labels

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        return text, label

    def __len__(self):
        return len(self.labels)
 ```

Maximum length is used later in training and evaluation step in the tokenizer."""

```python3
text_lengths = np.array([len(text) for text in X_train])
max_length = int(np.percentile(text_lengths, 95))
print(f"p95 for text length is: {max_length}")
print(f"Max length is set to: {max_length}")
```

```python3
train_dataset = SentimentDataset(
    texts=X_train.values,
    labels=y_train.values,
)

test_dataset = SentimentDataset(
    texts=X_test.values,
    labels=y_test.values,
)
```

Create a dataloader for the training data
```python3
TRAIN_BATCH_SIZE = 256
TEST_BATCH_SIZE = 512  
```

```python3
train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=TEST_BATCH_SIZE, shuffle=True)
``
```python3
sample_batch = next(iter(train_dataloader))
print(sample_batch[0][0])
print(sample_batch[1][0])
```

To fine-tune, use a model from the Transformers library in Hugging Face on the training set.

```python3
class SentimentClassificationModel(nn.Module):
    def __init__(self, pretrained_model_name:str='dbmdz/bert-base-turkish-cased', 
                 num_classes:int=3, freeze_base_model:bool=True, device='cpu'):
        super(SentimentClassificationModel, self).__init__()
        self.model = BertForSequenceClassification.from_pretrained(pretrained_model_name, num_labels=num_classes)
        self.device = device
        self.model = self.model.to(device)

        if freeze_base_model:
            self.__freeze_base_model()

    def __freeze_base_model(self):
        for param in self.model.base_model.parameters():
            param.requires_grad = False

    def forward(self, *args, **kwargs):
        return self.model.forward(*args, **kwargs)
```

```python3
model = SentimentClassificationModel(device=device)
```

## Evaluation of the Model Before Training

We showed accuracy, f1, precision, recall metrics using sklearn. You can see from the function below:

```python3
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def compute_metrics(true, preds):
    precision, recall, f1, _ = precision_recall_fscore_support(true, preds, average='micro')
    acc = accuracy_score(true, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }
```

```python3
from torch.nn import CrossEntropyLoss


def evaluation_step(dataloader):
    loss_function = CrossEntropyLoss()
    eval_loss = 0.0

    true = []
    preds = []
    
    with torch.no_grad():
        model.eval()

        with tqdm(dataloader) as tepoch:
            tepoch.set_description(f"Epoch {tepoch}")

            for (texts, labels) in tepoch:
                text_encodings = tokenizer(
                    texts,
                    return_tensors='pt',
                    truncation=True,
                    padding="max_length",
                    max_length=max_length,
                ).to(device)


                outputs = model(**text_encodings)
                logits = outputs.logits
                loss = loss_function(logits.to(labels.device), labels)
                eval_loss += loss

                batch_pred = outputs.logits.argmax(-1).cpu()
                preds.extend(batch_pred.tolist())
                true.extend(labels.tolist())

                metrics = {
                    "Loss": loss.item(),
                }

                tepoch.set_postfix(**metrics)


    # Normalize loss
    eval_loss = eval_loss / len(dataloader)

    return true, preds, eval_loss
```

Evaluate the pretrained model using test data."""

```python3
true, preds, eval_loss = evaluation_step(test_dataloader)

compute_metrics(true, preds)
```

## Train the Model

Weight decay is a way to prevent overfitting and reduce the complexity of a model in machine learning. It has been found to help machine learning models, including deep neural networks, perform better on new data. This technique is known as regularization.  

Below you can see how to apply regularization:

```python3
EPOCHS = 5
LEARNING_RATE = 2e-5
```

```python3
NO_DECAY = ['bias', 'LayerNorm.weight']
OPTIMIZER_GROUPED_PARAMETERS = [
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in NO_DECAY)], 'weight_decay': 0.01},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in NO_DECAY)], 'weight_decay': 0.0}
]
```

```python3
from torch.optim import AdamW

# Set up the optimizer
optimizer = AdamW(OPTIMIZER_GROUPED_PARAMETERS, lr=LEARNING_RATE)
```

```python3
model = model.train()

losses = []

for epoch in range(EPOCHS):
    with tqdm(train_dataloader) as tepoch:
        tepoch.set_description(f"Epoch {epoch}")

        for (texts, labels) in tepoch:
            optimizer.zero_grad()
            
            text_encodings = tokenizer(
                texts,
                return_tensors='pt',
                truncation=True,
                padding="max_length",
                max_length=max_length,
            ).to(device)

            labels = labels.to(device)
            outputs = model(**text_encodings, labels=labels)

            loss = outputs.loss
            loss.backward()
            optimizer.step()

            losses.append(loss.item())
            metrics = {
                "Loss": loss.item()
            }

            tepoch.set_postfix(**metrics)
```

## Evaluation
To evaluate the model you can use *evaluation_step* function. Then you can see results using *compute_metrics* function. It shows accuracy, f1, precision, recall metrics.

```python3
true, preds, eval_loss = evaluation_step(test_dataloader)

compute_metrics(true, preds)
```

It is done! We have implemented a Turkish sentiment analysis model using Hugging Face. You can implement it yourself! It is not as difficult as it seems.

## References
[1] Devlin, J., Chang, M. W., Lee, K., and Toutanova, K. (2018). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, NAACL-HLT 2019 (pp. 4171-4186). Stroudsburg, PA: Association for Computational Linguistics.  
[2] https://huggingface.co/transformers/v3.3.1/training.html  
[3] https://huggingface.co/docs/transformers/main_classes/tokenizer  
[4] https://huggingface.co/docs/transformers/model_doc/bert  
[5] https://huggingface.co/datasets/winvoker/turkish-sentiment-analysis-dataset
"""
