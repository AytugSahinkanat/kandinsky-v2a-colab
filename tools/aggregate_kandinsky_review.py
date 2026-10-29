"""Aggregate listener ratings for one generated audio per video scene."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re


def aggregate(key, responses):
    if key.get("schema") != "kandinsky-v2a-listening-key-v2":
        raise ValueError("Researcher key schema is not recognized.")
    scenes = key["scenes"]
    audio = key["audio"]
    scene_ids = set(scenes)
    audio_by_scene = {meta["scene_id"]: aid for aid, meta in audio.items()}
    if set(audio_by_scene) != scene_ids or len(audio_by_scene) != len(audio):
        raise ValueError("Researcher key must map exactly one audio to every scene.")

    seen = set()
    stats = defaultdict(lambda: {
        "participants": 0,
        "event_fit": [], "sync": [], "audio_quality": [], "artifact_severity": [],
        "unwanted_music_or_speech_count": 0, "would_use_counts": defaultdict(int),
        "notes": [],
    })
    incomplete_fields = 0
    for response in responses:
        if response.get("schema") != "kandinsky-v2a-listening-response-v2" or response.get("study_id") != key["study_id"]:
            raise ValueError("A response belongs to a different study or schema.")
        if response.get("consent_acknowledged") is not True:
            raise ValueError("A response without participant consent cannot be included.")
        participant = response.get("participant_id", "")
        if not re.fullmatch(r"[a-f0-9]{32}", participant) or participant in seen:
            raise ValueError("Invalid or duplicate participant ID.")
        seen.add(participant)
        answers = response.get("answers")
        if not isinstance(answers, list) or len(answers) != len(scene_ids) or {a.get("scene_id") for a in answers} != scene_ids:
            raise ValueError("A response is missing a scene or repeats one.")
        for scene_answer in answers:
            sid = scene_answer["scene_id"]
            if scene_answer.get("audio_id") != audio_by_scene[sid]:
                raise ValueError(f"Unexpected audio ID for scene {sid}.")
            stats[sid]["participants"] += 1
            for field in ("event_fit", "sync", "audio_quality", "artifact_severity"):
                value = scene_answer.get(field)
                if value is None:
                    incomplete_fields += 1
                elif type(value) is not int or value not in range(1, 6):
                    raise ValueError("Scores must be integers from 1 through 5 or null when skipped.")
                else:
                    stats[sid][field].append(value)
            unwanted = scene_answer.get("unwanted_music_or_speech")
            if unwanted is None:
                incomplete_fields += 1
            elif type(unwanted) is not bool:
                raise ValueError("Unwanted-sound field must be yes/no.")
            else:
                stats[sid]["unwanted_music_or_speech_count"] += unwanted
            would_use = scene_answer.get("would_use")
            if would_use is None:
                incomplete_fields += 1
            elif would_use not in ("yes", "after_edit", "no"):
                raise ValueError("Invalid use decision.")
            else:
                stats[sid]["would_use_counts"][would_use] += 1
            note = scene_answer.get("note", "")
            if not isinstance(note, str) or len(note) > 1000:
                raise ValueError("Invalid scene note.")
            if note.strip():
                stats[sid]["notes"].append({"participant_id": participant, "text": note.strip()})

    scene_results = {}
    for sid in scenes:
        values = stats[sid]
        scene_results[sid] = {
            **scenes[sid],
            "audio": audio[audio_by_scene[sid]],
            "participants_n": values["participants"],
            "ratings_n_by_metric": {k: len(values[k]) for k in ("event_fit", "sync", "audio_quality", "artifact_severity")},
            "means_1_to_5": {
                k: (sum(values[k]) / len(values[k]) if values[k] else None)
                for k in ("event_fit", "sync", "audio_quality", "artifact_severity")
            },
            "unwanted_music_or_speech_count": values["unwanted_music_or_speech_count"],
            "would_use_counts": dict(values["would_use_counts"]),
            "notes": values["notes"],
        }
    return {
        "schema": "kandinsky-v2a-listening-summary-v2",
        "study_id": key["study_id"],
        "participants": len(seen),
        "missing_rating_fields": incomplete_fields,
        "scene_results": scene_results,
        "interpretation_note": "Small-pilot listener feedback is directional; it is not a general performance rate.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("researcher_key", type=Path)
    parser.add_argument("responses_directory", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()
    key = json.loads(args.researcher_key.read_text(encoding="utf-8"))
    responses = [json.loads(path.read_text(encoding="utf-8"))
                 for path in sorted(args.responses_directory.glob("*.json"))]
    result = aggregate(key, responses)
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Aggregated {result['participants']} participants across {len(result['scene_results'])} scenes.")
    print(f"Summary: {args.output_json}")
