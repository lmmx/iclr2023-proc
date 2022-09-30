from __future__ import annotations

from pathlib import Path

import openreview
import pandas as pd

guest_client = openreview.Client(baseurl="https://api.openreview.net")
invitation_ref = "ICLR.cc/2023/Conference/-/Blind_Submission"

notes = guest_client.get_all_notes(invitation=invitation_ref)
note_fields = "id original number".split()
content_fields = "title keywords TL;DR abstract Please_choose_the_closest_area_that_your_submission_falls_into paperhash pdf".split()


def unpack_record(note) -> dict:
    record = {
        field: value for field, value in vars(note).items() if field in note_fields
    }
    for field in content_fields:
        record.update({field: note.content.get(field)})
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
if not csv_path.exists():
    tsv_path.write_text(df.to_csv(sep="\t"))
