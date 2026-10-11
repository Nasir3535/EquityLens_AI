from document_parser import assign_source_ids

def test_assign_source_ids_are_sequential():
    docs = [
        {"filename": "one.txt", "location": "text file", "text": "A"},
        {"filename": "two.txt", "location": "text file", "text": "B"},
    ]
    result = assign_source_ids(docs)
    assert [d["source_id"] for d in result] == ["D01", "D02"]

def test_assign_source_ids_empty_list():
    assert assign_source_ids([]) == []
