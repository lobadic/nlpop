# NLPOP: a Dataset for Popularity Prediction of Promoted NLP Research on Twitter

## Abstract
Twitter has slowly but surely established itself as a forum for disseminating, analysing and promoting NLP research. The trend of researchers promoting work not yet peer-reviewed (preprints) by posting concise summaries presented itself as an opportunity to collect and combine multiple modalities of data.
In scope of this paper, we (1) construct a dataset of Twitter threads in which researchers promote NLP preprints and (2) evaluate whether it is possible to predict the popularity of a thread based on the content of the Twitter thread, paper content and user metadata. We experimentally show that it is possible to predict popularity of threads promoting research based on their content, and that predictive performance depends on modelling textual input, indicating that the dataset could present value for related areas of NLP research such as citation recommendation and abstractive summarization.

For additional details check out the [paper](https://aclanthology.org/2022.wassa-1.32.pdf).


# Instalation
```bash
# using pip
pip install -r requirements.txt

# using Conda
conda create --name nlpop --file requirements.txt
```

# Usage
Append your API_BEARER_TOKEN to the bearer_token.txt in the root directory.
```bash
conda activate nlpop
python fetch_dataset.py
```

Twitter dataset will be saved to cache folder, to load it, use:
```python
pandas.read_csv(PATH, sep=',', lineterminator='\n')
```


# Citation
```bibtex
@inproceedings{obadic-etal-2022-nlpop,
    title = "NLPOP: a Dataset for Popularity Prediction of Promoted NLP Research on Twitter",
    author = "Obadić, Leo  and
      Tutek, Martin  and
      Šnajder, Jan",
    booktitle = "Proceedings of the 12th Workshop on Computational Approaches to Subjectivity, Sentiment & Social Media Analysis",
    month = may,
    year = "2022",
    address = "Dublin, Ireland",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.wassa-1.32",
    pages = "286--292",
    abstract = "Twitter has slowly but surely established itself as a forum for disseminating, analysing and promoting NLP research. The trend of researchers promoting work not yet peer-reviewed (preprints) by posting concise summaries presented itself as an opportunity to collect and combine multiple modalities of data. In scope of this paper, we (1) construct a dataset of Twitter threads in which researchers promote NLP preprints and (2) evaluate whether it is possible to predict the popularity of a thread based on the content of the Twitter thread, paper content and user metadata. We experimentally show that it is possible to predict popularity of threads promoting research based on their content, and that predictive performance depends on modelling textual input, indicating that the dataset could present value for related areas of NLP research such as citation recommendation and abstractive summarization.",
}
```

## TODOs:
- code refactoring
- add basic model example
