"""Build a blinded, offline listening study from a Kandinsky V2A review bundle."""
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
        raise ValueError(f"Güvensiz arşiv yolu: {name}")
    try:
        return archive.read(path.as_posix())
    except KeyError as exc:
        raise ValueError(f"Paket içinde dosya yok: {name}") from exc


def build(bundle_path, output_dir):
    bundle_path = Path(bundle_path)
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise ValueError("Mevcut yanıtların üzerine yazmamak için yeni bir çıktı klasörü seçin.")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Girdi ZIP'inin bütünlüğü doğrulanamadı.")
        manifest = json.loads(safe_member(archive, "manifest.json"))
        if manifest.get("schema") != "kandinsky-v2a-review-bundle-v1":
            raise ValueError("Beklenen Kandinsky V2A değerlendirme paketi değil.")
        scenes = manifest.get("scenes")
        candidates = manifest.get("candidates")
        if not isinstance(scenes, list) or not 2 <= len(scenes) <= 20:
            raise ValueError("2–20 arası sahne gerekli.")
        if not isinstance(candidates, list) or len(candidates) > 60:
            raise ValueError("En az bir aday ve en fazla 60 aday gerekli.")
        scene_ids = [s.get("scene_id") for s in scenes]
        candidate_ids = [c.get("candidate_id") for c in candidates]
        if len(set(scene_ids)) != len(scene_ids) or len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("Sahne ve aday kimlikleri benzersiz olmalı.")
        if not all(isinstance(x, str) and SAFE_ID.fullmatch(x) for x in scene_ids + candidate_ids):
            raise ValueError("Kimliklerde yalnızca harf, sayı, tire ve alt çizgi kullanılabilir.")

        output_dir.mkdir(parents=True)
        media_dir = output_dir / "assets"
        (media_dir / "videos").mkdir(parents=True)
        (media_dir / "audio").mkdir(parents=True)
        public_scenes, private_scenes = [], {}
        by_scene = {sid: [] for sid in scene_ids}
        used_names = set()

        for idx, scene in enumerate(scenes, start=1):
            sid = scene["scene_id"]
            if sid in used_names:
                raise ValueError("Yinelenen sahne kimliği.")
            used_names.add(sid)
            video_bytes = safe_member(archive, scene["video_path"])
            if b"ftyp" not in video_bytes[:64]:
                raise ValueError(f"Sahne {sid} için MP4 başlığı doğrulanamadı.")
            expected = scene.get("video_sha256")
            if expected and hashlib.sha256(video_bytes).hexdigest() != expected:
                raise ValueError(f"Sahne videosu SHA-256 ile eşleşmiyor: {sid}")
            video_rel = f"assets/videos/scene_{idx:02d}.mp4"
            (output_dir / video_rel).write_bytes(video_bytes)
            public_scenes.append({"id": sid, "label": f"Scene {idx}", "video": video_rel, "candidates": []})
            private_scenes[sid] = {
                "label": scene.get("label", f"Scene {idx}"),
                "source_name": scene.get("source_name"),
                "source_video_sha256": scene.get("source_sha256"),
                "review_video_sha256": expected,
                "start_seconds": scene.get("start_seconds"),
                "event_prompt": scene.get("event_prompt"),
            }

        cand_key = {}
        for idx, candidate in enumerate(candidates, start=1):
            cid, sid = candidate["candidate_id"], candidate.get("scene_id")
            if sid not in by_scene:
                raise ValueError(f"Tanımsız sahne kimliği olan aday: {cid}")
            audio = safe_member(archive, candidate["audio_path"])
            if not audio.startswith(b"RIFF") or audio[8:12] != b"WAVE":
                raise ValueError(f"Aday ses WAV değil: {cid}")
            expected = candidate.get("audio_sha256")
            if expected and hashlib.sha256(audio).hexdigest() != expected:
                raise ValueError(f"Aday ses SHA-256 ile eşleşmiyor: {cid}")
            output_mp4 = safe_member(archive, candidate["generated_mp4_path"])
            expected_mp4 = candidate.get("output_mp4_sha256")
            if expected_mp4 and hashlib.sha256(output_mp4).hexdigest() != expected_mp4:
                raise ValueError(f"Aday Kandinsky çıktısı SHA-256 ile eşleşmiyor: {cid}")
            audio_rel = f"assets/audio/candidate_{idx:03d}.wav"
            (output_dir / audio_rel).write_bytes(audio)
            candidate_public = {"id": cid, "audio": audio_rel}
            by_scene[sid].append(candidate_public)
            cand_key[cid] = {
                "scene_id": sid,
                "seed": candidate.get("seed"),
                "candidate_index": candidate.get("candidate_index"),
                "generation_seconds": candidate.get("generation_seconds"),
                "output_mp4_sha256": candidate.get("output_mp4_sha256"),
                "audio_sha256": expected,
                "checkpoint": manifest.get("model", {}).get("checkpoint"),
                "model": manifest.get("model", {}).get("name"),
                "source_commit": manifest.get("source_commit"),
                "event_prompt": candidate.get("event_prompt", private_scenes[sid]["event_prompt"]),
            }

        for scene in public_scenes:
            scene["candidates"] = by_scene[scene["id"]]
            if len(scene["candidates"]) < 2:
                raise ValueError(f"{scene['label']} için en az iki seed adayı gerekli.")

        study_digest = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        study_id = study_digest[:24]
        public = {"schema": "kandinsky-v2a-listening-study-v1", "study_id": study_id,
                  "title": manifest.get("study_title", "Video-to-audio listening study"),
                  "scenes": public_scenes}
        page = (APP / "index.html").read_text(encoding="utf-8")
        page = page.replace("/*__STYLE__*/", (APP / "style.css").read_text(encoding="utf-8"))
        page = page.replace("/*__APP__*/", (APP / "app.js").read_text(encoding="utf-8"))
        page = page.replace("/*__STUDY__*/", json.dumps(public, ensure_ascii=True).replace("<", "\\u003c"))
        (output_dir / "Review.html").write_text(page, encoding="utf-8")

        researcher_key = {
            "schema": "kandinsky-v2a-listening-key-v1", "study_id": study_id,
            "bundle_sha256": study_digest, "model": manifest.get("model"),
            "source_commit": manifest.get("source_commit"), "scenes": private_scenes,
            "candidates": cand_key,
            "limitations": [
                "Bu değerlendirme küçük bir pilot kümesidir; genel performans oranı değildir.",
                "Puanlar öznel algıyı ölçer; otomatik video-ses senkron metriği değildir.",
                "Aynı video için seed adayları bağımsız veri örnekleri değildir.",
            ],
        }
        (output_dir / "researcher_key.json").write_text(
            json.dumps(researcher_key, ensure_ascii=False, indent=2), encoding="utf-8")
        instructions = (
            "KANDINSKY VIDEO-TO-AUDIO REVIEW\n\n"
            "1. Extract this ZIP to a folder. Keep the assets folder next to Review.html.\n"
            "2. Open Review.html in Chrome, Edge, or Firefox. Internet and an account are not required.\n"
            "3. Watch the muted scene, listen to every candidate, and rate each sound.\n"
            "4. Download your JSON response and send that file to the study owner.\n"
            "Responses stay in this browser until downloaded. No automatic upload occurs.\n"
            "Do not share researcher_key.json with participants. The pack includes the video and audio files.\n"
        )
        (output_dir / "README_PARTICIPANT.txt").write_text(instructions, encoding="utf-8")
        participant_zip = output_dir / "Participant_Package.zip"
        with zipfile.ZipFile(participant_zip, "w", zipfile.ZIP_DEFLATED) as out:
            for path in [output_dir / "Review.html", output_dir / "README_PARTICIPANT.txt"]:
                out.write(path, path.relative_to(output_dir).as_posix())
            for path in media_dir.rglob("*"):
                if path.is_file():
                    out.write(path, path.relative_to(output_dir).as_posix())
    return {"study_id": study_id, "scenes": len(scenes), "candidates": len(candidates),
            "participant_zip": str(participant_zip.resolve()),
            "review_page": str((output_dir / 'Review.html').resolve()),
            "researcher_key": str((output_dir / 'researcher_key.json').resolve()),
            "participant_package_excludes_researcher_key": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_zip", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.bundle_zip, args.output_directory), ensure_ascii=False, indent=2))

