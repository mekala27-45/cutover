from datetime import date
import json
import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError
from packages.core import Feature, Prediction, Thresholds, Decision, Complaint, Label, digest
from packages.intake import parse_line, Quarantine, group_rows, split_name
from packages.cascade import decide
from packages.llm import parse_answer
from packages.evaluation import verdict, bh, grade, paired_difference
from packages.release import is_canary, alarms, restore

T=Thresholds(routing=.8,safety=.1,out_of_scope=.2,selected_on="development",registration_digest="a"*64)
def feature(text="The steering became difficult while parking the vehicle."):
    return Feature(narrative=text)
def pred(p=.9,safety=.01):
    return Prediction(scores={"STEERING":float(p),"OTHER":.01},safety_probability=float(safety),
                      arm="fixture",version_digest="b"*64,compute_ms=1.)
def line(n=49):
    f=[""]*n
    for i,v in {1:"123456",3:"TEST",4:"MODEL",5:"2020",6:"N",8:"N",9:"0",10:"0",
                11:"STEERING:LINKAGE",16:"20240101",19:feature().narrative,45:"V"}.items(): f[i]=v
    # Values must never survive the first parser call.
    for i in [12,14,40,41,42,43,44]+([50] if n==51 else []): f[i]="PRIVATE_SENTINEL"
    return "\t".join(f)

@pytest.mark.parametrize("layout",[49,51])
def test_parse_and_drop(layout):
    row=parse_line(line(layout))
    assert "PRIVATE_SENTINEL" not in row.model_dump_json()
    assert row.layout==layout and row.label.groups==("STEERING",)
    assert split_name(row)=="development"
@pytest.mark.parametrize("n",[0,1,48,50,52])
def test_invalid_layout_refuses(n):
    with pytest.raises(Quarantine): parse_line("\t".join([""]*n))
def test_unknown_safety_is_not_negative():
    fields=line().split("\t"); fields[6]=""
    with pytest.raises(Quarantine): parse_line("\t".join(fields))
def test_group_rows_and_conflict():
    a=parse_line(line())
    b=a.model_copy(update={"label":Label(groups=("BRAKES",),safety=False)})
    rows,drops=group_rows([a,b])
    assert rows[0].label.groups==("BRAKES","STEERING")
    assert drops["component_rows_grouped"]==1
    assert not group_rows([a,a.model_copy(update={"text_digest":"0"*64})])[0]
@pytest.mark.parametrize("d,expected",[("2023-12-31","train"),("2024-01-01","development"),
    ("2024-06-30","development"),("2024-07-01","test"),("2026-01-01","shadow")])
def test_time_boundaries(d,expected):
    assert split_name(parse_line(line()).model_copy(update={"received":date.fromisoformat(d)}))==expected
@pytest.mark.parametrize("word",["fire","crashed","smoking","injured","hospitalized","killed"])
def test_safety_guard_overrides_model(word):
    d=decide(feature("The vehicle "+word+" while being driven on the road."),pred(),T)
    assert d.action=="send_to_analyst" and d.reason=="safety_keyword"
def test_live_uncertainty_reaches_person():
    assert decide(feature(),pred(.6),T).reason=="incumbent_required"
@given(st.floats(min_value=0,max_value=1,allow_nan=False),st.floats(min_value=0,max_value=1,allow_nan=False))
def test_no_close(p,safety):
    assert decide(feature(),pred(p,safety),T).action in {"route","send_to_analyst"}
def test_labels_cannot_enter_feature():
    with pytest.raises(ValidationError):
        Feature(narrative=feature().narrative,label={"safety":False})
@pytest.mark.parametrize("text",['{"scores":{},"safety_probability":NaN}',
    '{"scores":{"STEERING":0.4},"safety_probability":0.1,"action":"route"}',
    '{"scores":{"STEERING":0.4,"STEERING":0.9},"safety_probability":0.1}','nonsense'])
def test_strict_model_parser(text):
    with pytest.raises((ValueError,ValidationError)):
        parse_answer(text,["STEERING"],"small","a"*64,1.)
def test_model_parser_valid():
    p=parse_answer('{"scores":{"STEERING":0.4},"safety_probability":0.1}',["STEERING"],"small","a"*64,1.)
    assert p.scores["STEERING"]==.4
def test_verdict_boundaries():
    assert verdict(None,.98,"gte")=="not_shown"
    assert verdict(.99,.98,"gte",.97,1.)=="not_shown"
    assert verdict(.98,.98,"gte",.98,.99)=="met"
    assert verdict(.95,.98,"gte",.94,.96)=="not_met"
def test_missing_attempt_stays_in_denominator():
    result=grade([parse_line(line())],{})
    assert result["queue_hit_rate"]=={"value":0.,"numerator":0,"denominator":1}
def test_unpaired_comparison_refuses():
    with pytest.raises(ValueError): paired_difference({"a":1.},{"b":0.})
def test_bh_known_family():
    assert bh({"a":.01,"b":.04,"c":.03})==pytest.approx({"a":.03,"b":.04,"c":.04})
def test_canary_extremes_and_stability():
    assert is_canary("case",1) and not is_canary("case",0)
    assert is_canary("case",.1)==is_canary("case",.1)
def test_monitor_good_and_bad():
    rules={"safety_recall_min":.98,"agreement_min":.9,"review_share_delta":.15,
           "safety_flag_delta":.1,"psi_max":.25}
    good={"safety_recall":1.,"agreement":1.,"review_share_delta":0.,
          "safety_flag_delta":0.,"psi":0.}
    assert not alarms(good,rules)["trip"]
    for change in [{"safety_recall":.9},{"agreement":.5,"psi":.8},
                   {"review_share_delta":.4,"safety_flag_delta":.4}]:
        assert alarms(good|change,rules)["trip"]
    assert alarms({},rules)["state"]=="insufficient"
def test_rollback_bytes(tmp_path):
    import hashlib
    data=b"artifact-v1"
    sha=hashlib.sha256(data).hexdigest()
    (tmp_path/sha).write_bytes(data)
    restore(tmp_path,sha,tmp_path/"restored")
    assert (tmp_path/"restored").read_bytes()==data
    (tmp_path/sha).write_bytes(b"corrupted")
    with pytest.raises(ValueError): restore(tmp_path,sha,tmp_path/"restored")
