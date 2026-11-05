"""Only aggregate evidence may leave the runner."""
import json
from pathlib import Path
def publish(root: Path) -> None:
    out=root/"public_results"; out.mkdir(exist_ok=True)
    intake=root/"results/intake.json"
    if intake.exists():
        source=json.loads(intake.read_text())
        allowed=["mode","sources","layout_document_sha256","layouts_seen","counts","dropped",
                 "duplicate_count","label_mapping_digest","split_digests"]
        (out/"intake.json").write_text(json.dumps({k:source[k] for k in allowed},indent=2)+"\n")
    floor=root/"results/floor.json"
    if floor.exists():
        source=json.loads(floor.read_text())
        # No case-level records, sample IDs, narrative or prediction rows are exported.
        for split,report in source.get("reports",{}).items():
            report["missing_count"]=len(report.pop("missing",[]))
        (out/"floor.json").write_text(json.dumps(source,indent=2)+"\n")
if __name__=="__main__": publish(Path(__file__).resolve().parents[1])
