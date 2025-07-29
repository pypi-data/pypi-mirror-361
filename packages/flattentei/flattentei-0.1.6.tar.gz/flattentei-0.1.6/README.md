# Flatten Tei

## Reformat tei-xml files to raw text + standoff annotations in json (flatdoc)

 * `flatdoc` is not a standardized format
 * `flatdoc` is a json file containing the whole text of a document in the `text`field
   * All span annotations are in 'annotations' in form of an object.
   * e.g. `{"Sentence": [{'begin':0, 'end': 13}, ...], ..}` 

## Access content of `flatdoc` files

### Use Case: Get all Sentences of a document in `flatdoc`-format

  * Assuming there are Sentence annotation.

```python

from flattentei import get_units

fn = <filename of flatdoc json file>

with open(fn) as f:
    flatdoc = json.load(f)
    sentences = get_units("Sentence", flatdoc)
```

### Use Case: Get all Entities of a document in `flatdoc`-format
  * Assuming the entities are stored as `Entity` in the `annotations` field
  * (In the GSAP project `ScholarlyEntitiy`)
  * enrich each entity with `Sentence`-texts
    * They can be found in the `container` field for each entity

```python

from flattentei import get_units

fn = <filename of flatdoc json file>

with open(fn) as f:
    flatdoc = json.load(f)
    entities = get_units("Entity", flatdoc, enrich_container="Sentence")


for ent in entities:
    print(f'The entity span: {ent["text"]}')
    sentence_text = ent['containers']['Sentence']['text']
```
