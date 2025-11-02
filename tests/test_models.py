from storage.models import PageModel, to_dict, from_dict

def test_page_model_roundtrip():
    page = PageModel("t", "u", "c")
    d = to_dict(page)
    restored = from_dict(d)
    assert restored.title == "t"
    assert restored.url == "u"
    assert restored.content == "c"
