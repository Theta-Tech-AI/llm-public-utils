"""Export a report for download."""


def export_report(rows, path: str, as_pdf: bool = False, include_headers: bool = True) -> str:
    """PLANTED: two parameters select two different write paths (flag arguments)."""
    if as_pdf:
        return _write_pdf(rows, path, include_headers)
    return _write_csv(rows, path, include_headers)


def _write_csv(rows, path, include_headers):
    with open(path, "w", encoding="utf-8") as fh:
        if include_headers:
            fh.write(",".join(rows[0]._fields) + "\n")
        for row in rows:
            fh.write(",".join(map(str, row)) + "\n")
    return path


def _write_pdf(rows, path, include_headers):
    body = "\n".join(",".join(map(str, row)) for row in rows)
    with open(path, "wb") as fh:
        fh.write(b"%PDF-1.4\n" + body.encode())   # stand-in for a real writer
    return path
