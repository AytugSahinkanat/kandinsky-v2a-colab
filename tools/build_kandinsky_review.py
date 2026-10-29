"""Build a blinded, offline one-audio-per-video Kandinsky listening study."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "review_app"
SAFE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def safe_member(archive, name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise ValueError(f"Unsafe archive path: {name}")
    try:
        return archive.read(path.as_posix())
    except KeyError as exc:
        raise ValueError(f"Missing file in bundle: {name}") from exc


def build(bundle_path, output_dir):
    bundle_path = Path(bundle_path)
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise ValueError("Choose a new output folder so prior responses are not overwritten.")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Input ZIP integrity check failed.")
        manifest = json.loads(safe_member(archive, "manifest.json"))
        if manifest.get("schema") != "kandinsky-v2a-review-bundle-v2":
            raise ValueError("Expected a one-audio-per-video Kandinsky review bundle.")
        scenes = manifest.get("scenes")
        candidates = manifest.get("candidates")
        if not isinstance(scenes, list) or not 2 <= len(scenes) <= 20:
            raise ValueError("The bundle must contain 2–20 scenes.")
        if not isinstance(candidates, list) or len(candidates) != len(scenes):
            raise ValueError("Each scene must have exactly one generated audio.")
        scene_ids = [s.get("scene_id") for s in scenes]
        candidate_ids = [c.get("candidate_id") for c in candidates]
        if len(set(scene_ids)) != len(scene_ids) or len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("Scene and audio IDs must be unique.")
        if not all(isinstance(x, str) and SAFE_ID.fullmatch(x) for x in scene_ids + candidate_ids):
            raise ValueError("IDs may contain only letters, numbers, hyphens, and underscores.")

        candidate_by_scene = {}
        for candidate in candidates:
            sid = candidate.get("scene_id")
            if sid not in scene_ids or sid in candidate_by_scene:
                raise ValueError("Each scene must map to one unique generated audio.")
            candidate_by_scene[sid] = candidate
        if set(candidate_by_scene) != set(scene_ids):
            raise ValueError("A scene has no generated audio.")

        output_dir.mkdir(parents=True)
        media_dir = output_dir / "assets"
        (media_dir / "videos").mkdir(parents=True)
        (media_dir / "audio").mkdir(parents=True)
        public_scenes, private_scenes, private_audio = [], {}, {}

        for idx, scene in enumerate(scenes, start=1):
            sid = scene["scene_id"]
            video_bytes = safe_member(archive, scene["video_path"])
            if b"ftyp" not in video_bytes[:64]:
                raise ValueError(f"Scene video is not a valid MP4: {sid}")
            if scene.get("video_sha256") and hashlib.sha256(video_bytes).hexdigest() != scene["video_sha256"]:
                raise ValueError(f"Scene video SHA-256 mismatch: {sid}")
            candidate = candidate_by_scene[sid]
            audio_bytes = safe_member(archive, candidate["audio_path"])
            if not audio_bytes.startswith(b"RIFF") or audio_bytes[8:12] != b"WAVE":
                raise ValueError(f"Generated audio is not a WAV: {sid}")
            if candidate.get("audio_sha256") and hashlib.sha256(audio_bytes).hexdigest() != candidate["audio_sha256"]:
                raise ValueError(f"Generated audio SHA-256 mismatch: {sid}")
            generated_mp4 = safe_member(archive, candidate["generated_mp4_path"])
            if candidate.get("output_mp4_sha256") and hashlib.sha256(generated_mp4).hexdigest() != candidate["output_mp4_sha256"]:
                raise ValueError(f"Kandinsky output SHA-256 mismatch: {sid}")

            video_rel = f"assets/videos/scene_{idx:02d}.mp4"
            audio_rel = f"assets/audio/scene_{idx:02d}.wav"
            (output_dir / video_rel).write_bytes(video_bytes)
            (output_dir / audio_rel).write_bytes(audio_bytes)
            public_scenes.append({
                "id": sid, "audio_id": candidate["candidate_id"], "label": f"Scene {idx}",
                "video": video_rel, "audio": audio_rel,
            })
            private_scenes[sid] = {
                "label": scene.get("label", f"Scene {idx}"),
                "source_name": scene.get("source_name"),
                "source_sha256": scene.get("source_sha256"),
                "source_page": scene.get("source_page"),
                "source_license": scene.get("source_license"),
                "review_video_sha256": scene.get("video_sha256"),
                "start_seconds": scene.get("start_seconds"),
                "event_prompt": scene.get("event_prompt"),
            }
            private_audio[candidate["candidate_id"]] = {
                "scene_id": sid,
                "seed": candidate.get("seed"),
                "generation_seconds": candidate.get("generation_seconds"),
                "output_mp4_sha256": candidate.get("output_mp4_sha256"),
                "audio_sha256": candidate.get("audio_sha256"),
                "checkpoint": manifest.get("model", {}).get("checkpoint"),
                "model": manifest.get("model", {}).get("name"),
                "source_commit": manifest.get("source_commit"),
                "event_prompt": candidate.get("event_prompt", scene.get("event_prompt")),
            }

        digest = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        study_id = digest[:24]
        public = {
            "schema": "kandinsky-v2a-listening-study-v2",
            "study_id": study_id,
            "title": manifest.get("study_title", "Video-to-audio listening study"),
            "scenes": public_scenes,
        }
        page = (APP / "index.html").read_text(encoding="utf-8")
        page = page.replace("/*__STYLE__*/", (APP / "style.css").read_text(encoding="utf-8"))
        page = page.replace("/*__APP__*/", (APP / "app.js").read_text(encoding="utf-8"))
        page = page.replace("/*__STUDY__*/", json.dumps(public, ensure_ascii=True).replace("<", "\\u003c"))
        (output_dir / "Review.html").write_text(page, encoding="utf-8")

        researcher_key = {
            "schema": "kandinsky-v2a-listening-key-v2",
            "study_id": study_id,
            "bundle_sha256": digest,
            "model": manifest.get("model"),
            "source_commit": manifest.get("source_commit"),
            "scenes": private_scenes,
            "audio": private_audio,
            "limitations": [
                "This is a small directional pilot, not a general performance rate.",
                "Prompt wording is part of this pilot; the study does not isolate video-only conditioning.",
                "Listener scores are subjective and are not an automatic synchronization metric.",
                "One fixed seed is used per scene; this study does not compare seeds.",
            ],
        }
        (output_dir / "researcher_key.json").write_text(
            json.dumps(researcher_key, ensure_ascii=False, indent=2), encoding="utf-8")
        sources = ["VIDEO SOURCES AND LICENSES", "", "All listed video files are marked CC0 1.0 on their Wikimedia Commons file pages."]
        for idx, scene in enumerate(scenes, start=1):
            sources.extend(["", f"Scene {idx}: {scene.get('source_name', 'source video')}",
                            f"Source: {scene.get('source_page', '')}",
                            f"License: {scene.get('source_license', 'CC0 1.0')}"])
        (output_dir / "VIDEO_SOURCES.txt").write_text("\n".join(sources) + "\n", encoding="utf-8")
        instructions = (
            "KANDINSKY VIDEO-TO-AUDIO REVIEW\n\n"
            "1. Extract this ZIP and keep the assets folder next to Review.html.\n"
            "2. Open Review.html in Chrome, Edge, or Firefox. No account or internet is required.\n"
            "3. Watch each muted clip, listen to its generated sound, and rate the match.\n"
            "4. Download your JSON response and send that file to the study owner.\n\n"
            "Responses stay in this browser until downloaded. Nothing uploads automatically.\n"
            "The pack contains CC0 source videos and generated audio. See VIDEO_SOURCES.txt.\n"
        )
        (output_dir / "README_PARTICIPANT.txt").write_text(instructions, encoding="utf-8")
        participant_zip = output_dir / "Participant_Package.zip"
        with zipfile.ZipFile(participant_zip, "w", zipfile.ZIP_DEFLATED) as out:
            for path in [output_dir / "Review.html", output_dir / "README_PARTICIPANT.txt",
                         output_dir / "VIDEO_SOURCES.txt"]:
                out.write(path, path.relative_to(output_dir).as_posix())
            for path in media_dir.rglob("*"):
                if path.is_file():
                    out.write(path, path.relative_to(output_dir).as_posix())

    return {
        "study_id": study_id,
        "scenes": len(scenes),
        "generated_audio_files": len(candidates),
        "participant_zip": str(participant_zip.resolve()),
        "review_page": str((output_dir / "Review.html").resolve()),
        "researcher_key": str((output_dir / "researcher_key.json").resolve()),
        "participant_package_excludes_researcher_key": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_zip", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.bundle_zip, args.output_directory), ensure_ascii=False, indent=2))
