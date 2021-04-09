# wiki-history-extractor
This extract ko-wiki history data from XML file.
Only support Korean Language.

---
### How to use

1. Should setup `WikiExtractor` 

2. run `wiki extractor`
``` python
python -m wikiextractir.WikiExtractor 'your wiki dump file' -o 'output path'
```

3. run `processing.py` 
 ``` python
 python processing.py --path 'output path' --write-path 'result output path'
 ```
 
---
### Dependency
- [WikiExtractor](https://github.com/attardi/wikiextractor)
