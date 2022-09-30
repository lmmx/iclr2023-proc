from __future__ import annotations

from pathlib import Path

import openreview
import pandas as pd

guest_client = openreview.Client(baseurl="https://api.openreview.net")
invitation_ref = "ICLR.cc/2023/Conference/-/Blind_Submission"

notes = guest_client.get_all_notes(invitation=invitation_ref)
note_fields = "id number".split()
content_fields = "title keywords TL;DR abstract area paperhash pdf".split()
area_alias = "Please_choose_the_closest_area_that_your_submission_falls_into"


def unpack_record(note) -> dict:
    record = {
        field: value for field, value in vars(note).items() if field in note_fields
    }
    for field in content_fields:
        accessed_field = area_alias if field == "area" else field
        content_value = note.content.get(accessed_field)
        if field == "abstract" and content_value is not None:
            content_value = content_value.replace("\n", "\\n")
        record.update({field: content_value})
    return record


df = (
    pd.DataFrame.from_records([unpack_record(note) for note in notes])
    .sort_values("number")
    .reset_index()
    .drop(columns=["index"])
)


json_path = Path("submissions.json")
if not json_path.exists():
    json_path.write_text(df.to_json())

tsv_path = Path("submissions.tsv")
if not tsv_path.exists():
    tsv_path.write_text(df.to_csv(sep="\t", index=False))

tsv_no_abs_path = Path("submissions_no_abstract.tsv")
abs_cols = ["id", "abstract", "TL;DR", "area", "keywords", "paperhash", "pdf"]
if not tsv_no_abs_path.exists():
    tsv_no_abs_path.write_text(df.drop(columns=abs_cols).to_csv(sep="\t", index=False))
