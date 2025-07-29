import json
from glob import glob
from pathlib import Path
from .extract_parts import generate_line_annos, get_units

class FlatTeiSeparateLoader:
    def __init__(self, txt_path, anno_path):
        self.txt_path = txt_path
        self.anno_path = anno_path

    def load_flat_tei(self, document_name):
        annos = []
        text = ""
        path_text = Path(self.txt_path) / Path(document_name)
        path_anno = Path(self.anno_path) / Path(document_name).with_suffix(".json")
        text = path_text.open().read()
        annos = json.load(path_anno.open())
        return dict(text=text, annotations=annos)


class FlatTeiLoader:
    def __init__(self, doc_path):
        self.doc_path = Path(doc_path)
        self.fns_docs = glob(f"{self.doc_path}/*.json")

    def load_docs(self):
        for fn_doc in self.fns_docs:
            fn_doc = Path(fn_doc)
            filename = fn_doc.name
            with fn_doc.open() as f:
                doc = json.load(f)
                assert "filename" not in doc
                doc["filename"] = filename
                yield doc

    def get_units(self, unit_type, doc_id_key, enrich_container=[], doc_limit=None, annotator_key=None):
        """
        unit_type: e.g. Sentence, Scholarly, Paragraph
        """
        all_units = []
        for idx, doc in enumerate(self.load_docs()):
            if doc_limit is not None and idx >= doc_limit:
                break
            doc_id = doc[doc_id_key] if doc_id_key is not None else None
            doc_units = get_units(
                unit_type, doc, doc_id=doc_id, enrich_container=enrich_container, annotator=None
            )
            all_units.extend(doc_units)
        return all_units

    def load_doc(self, document_name):
        """
        parameters: document_name identifier of document
        """
        file_path = self.doc_path / Path(document_name).with_suffix(".json")
        doc = json.load(file_path.open())
        doc["annotations"]["Line"] = generate_line_annos(doc["text"])
        assert "document_name" not in doc
        doc["document_name"] = document_name
        return doc
