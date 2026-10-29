"""Aggregate returned blinded Kandinsky V2A listener JSON files."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re


def aggregate(key, responses):
    if key.get("schema") != "kandinsky-v2a-listening-key-v1":
        raise ValueError("Researcher key schema is not recognized.")
    candidate_map, scene_map = key["candidates"], key["scenes"]
    seen = set()
    stats = defaultdict(lambda: {"event_fit": [], "sync": [], "audio_quality": [],
                                  "artifact_severity": [], "unwanted": 0, "would_use": defaultdict(int),
                                  "best_count": 0, "best_total": 0, "no_clear_winner": 0})
    per_scene = defaultdict(lambda: {"participants": 0, "best_candidate_counts": defaultdict(int),
                                     "no_clear_winner_count": 0})
    incomplete_fields = 0
    for response in responses:
        if response.get("schema") != "kandinsky-v2a-listening-response-v1" or response.get("study_id") != key["study_id"]:
            raise ValueError("A response belongs to a different study or schema.")
        if response.get("consent_acknowledged") is not True:
            raise ValueError("A response without participant consent cannot be included.")
        participant = response.get("participant_id", "")
        if not re.fullmatch(r"[a-f0-9]{32}", participant) or participant in seen:
            raise ValueError("Invalid or duplicate participant ID.")
        seen.add(participant)
        answers = response.get("answers")
        if not isinstance(answers, list) or len(answers) != len(scene_map) or {a.get("scene_id") for a in answers} != set(scene_map):
            raise ValueError("A response is missing a scene or repeats one.")
        for scene_answer in answers:
            sid = scene_answer["scene_id"]
            candidates = scene_answer.get("candidates", [])
            expected = {cid for cid, meta in candidate_map.items() if meta["scene_id"] == sid}
            if not isinstance(candidates, list) or len(candidates) != len(expected) or {a.get("candidate_id") for a in candidates} != expected:
                raise ValueError(f"Scene {sid} has missing or duplicate candidates.")
            best = scene_answer.get("best_candidate_id")
            if best not in expected | {"none", None}:
                raise ValueError("Invalid preferred candidate.")
            per_scene[sid]["participants"] += 1
            if best is not None and best != "none":
                per_scene[sid]["best_candidate_counts"][best] += 1
            elif best == "none":
                per_scene[sid]["no_clear_winner_count"] += 1
                for cid in expected:
                    stats[cid]["no_clear_winner"] += 1
            for answer in candidates:
                cid = answer["candidate_id"]
                score_keys = ("event_fit", "sync", "audio_quality", "artifact_severity")
                for k in score_keys:
                    value = answer.get(k)
                    if value is None:
                        incomplete_fields += 1
                    elif type(value) is not int or value not in range(1, 6):
                        raise ValueError("Scores must be integers from 1 through 5 or null when skipped.")
                unwanted = answer.get("unwanted_music_or_speech")
                if unwanted is None:
                    incomplete_fields += 1
                elif unwanted not in (True, False):
                    raise ValueError("Unwanted-sound field must be yes/no.")
                would_use = answer.get("would_use")
                if would_use is None:
                    incomplete_fields += 1
                elif would_use not in ("yes", "after_edit", "no"):
                    raise ValueError("Invalid use decision.")
                if not isinstance(answer.get("note", ""), str) or len(answer.get("note", "")) > 1000:
                    raise ValueError("Invalid note.")
                s = stats[cid]
                for k in score_keys:
                    if answer[k] is not None:
                        s[k].append(answer[k])
                if unwanted is not None:
                    s["unwanted"] += unwanted
                if would_use is not None:
                    s["would_use"][would_use] += 1
                if best is not None:
                    s["best_total"] += 1
                    s["best_count"] += best == cid

    candidate_results = {}
    for cid, values in stats.items():
        meta = candidate_map[cid]
        candidate_results[cid] = {
            **meta,
            "ratings_n_by_metric": {k: len(values[k]) for k in
                                     ("event_fit", "sync", "audio_quality", "artifact_severity")},
            "means_1_to_5": {k: (sum(values[k]) / len(values[k]) if values[k] else None) for k in
                              ("event_fit", "sync", "audio_quality", "artifact_severity")},
            "unwanted_music_or_speech_count": values["unwanted"],
            "would_use_counts": dict(values["would_use"]),
            "preferred_count": values["best_count"],
            "preference_responses": values["best_total"],
            "no_clear_winner_count": values["no_clear_winner"],
        }
    return {
        "schema": "kandinsky-v2a-listening-summary-v1", "study_id": key["study_id"],
        "participants": len(seen), "missing_rating_fields": incomplete_fields,
        "candidate_results": candidate_results,
        "scene_results": {sid: {"participants": v["participants"],
                                 "preferred_candidate_counts": dict(v["best_candidate_counts"]),
                                 "no_clear_winner_count": v["no_clear_winner_count"]}
                          for sid, v in per_scene.items()},
        "limitations": key.get("limitations", []),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("researcher_key", type=Path)
    parser.add_argument("responses_directory", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()
    paths = sorted(args.responses_directory.glob("kandinsky_answers_*.json"))
    if not paths:
        parser.error("No kandinsky_answers_*.json response files found.")
    result = aggregate(json.loads(args.researcher_key.read_text(encoding="utf-8")),
                       [json.loads(p.read_text(encoding="utf-8")) for p in paths])
    with args.output_json.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

