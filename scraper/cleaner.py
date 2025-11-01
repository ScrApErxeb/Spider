def sanitize(data):
    clean = []
    for record in data:
        if record.get("title"):
            record["title"] = record["title"].strip()
            clean.append(record)
    return clean
