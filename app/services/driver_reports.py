import mimetypes
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.supabase_client import supabase


DRIVER_AUDIO_BUCKET = "driver-audio"


def _guess_content_type(filename: str | None) -> str:
    guessed, _ = mimetypes.guess_type(filename or "")
    return guessed or "audio/wav"


def _build_storage_path(driver_id: str | None, filename: str | None) -> str:
    extension = Path(filename or "report.wav").suffix or ".wav"
    owner = driver_id or "unassigned"
    return f"{owner}/{uuid4().hex}{extension}"


def _transcribe_audio(file_bytes: bytes, filename: str | None) -> str:
    token = settings.HUGGINGFACE_API_TOKEN.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hugging Face transcription token is not configured on the backend.",
        )

    model = settings.HUGGINGFACE_ASR_MODEL.strip() or "openai/whisper-large-v3"
    endpoint = f"https://api-inference.huggingface.co/models/{model}"
    content_type = _guess_content_type(filename)

    try:
        with httpx.Client(timeout=90.0) as client:
            response = client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": content_type,
                },
                content=file_bytes,
            )
    except HTTPException:
        raise
    except Exception:
        return "Transcription pending."

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Hugging Face transcription token is invalid or expired.",
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        return "Transcription pending."

    try:
        payload = response.json()
    except ValueError:
        return "Transcription pending."

    if isinstance(payload, dict):
        text = payload.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()

        if isinstance(payload.get("error"), str):
            return "Transcription pending."

    return "Transcription pending."


def create_driver_report(
    *,
    file_bytes: bytes,
    filename: str | None,
    driver_id: str | None = None,
    task_id: str | None = None,
    lane_name: str | None = None,
    house_number: int | None = None,
    transcription: str | None = None,
):
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required.",
        )

    transcription_text = transcription or _transcribe_audio(file_bytes, filename)
    storage_path = _build_storage_path(driver_id, filename)
    content_type = _guess_content_type(filename)

    try:
        supabase.storage.from_(DRIVER_AUDIO_BUCKET).upload(
            storage_path,
            file_bytes,
            {"content-type": content_type},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload driver audio to storage.",
        ) from exc

    audio_url = supabase.storage.from_(DRIVER_AUDIO_BUCKET).get_public_url(storage_path)
    report_payload = {
        "file_name": filename or Path(storage_path).name,
        "storage_path": storage_path,
        "status": "pending",
        "transcription": transcription_text,
        "driver_id": driver_id,
        "task_id": task_id,
        "lane_name": lane_name,
        "house_number": house_number,
    }

    try:
        created = supabase.table("driver_voice_reports").insert(report_payload).execute().data or []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to store driver voice report metadata.",
        ) from exc

    report = created[0] if created else report_payload
    report["audio_url"] = audio_url

    if task_id:
        try:
            supabase.table("collection_tasks").update(
                {
                    "voice_note_url": audio_url,
                    "voice_transcript": transcription_text,
                }
            ).eq("id", task_id).execute()
        except Exception:
            # The mobile task id may be UI-only or may not match a collection_tasks row yet.
            pass

    return report


def list_driver_reports(*, driver_id: str | None = None, limit: int = 50):
    query = (
        supabase.table("driver_voice_reports")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if driver_id:
        query = query.eq("driver_id", driver_id)

    try:
        rows = query.execute().data or []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch driver voice reports.",
        ) from exc

    for row in rows:
        storage_path = row.get("storage_path")
        row["audio_url"] = (
            supabase.storage.from_(DRIVER_AUDIO_BUCKET).get_public_url(storage_path)
            if storage_path
            else None
        )

    return rows
