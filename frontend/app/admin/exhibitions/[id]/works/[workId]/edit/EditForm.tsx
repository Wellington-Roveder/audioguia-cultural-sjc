"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

type Work = {
  id: string;
  exhibition_id: string;
  title: string;
  artist: string | null;
  description: string;
  audio_url: string | null;
  audio_description_url: string | null;
  libras_video_url: string | null;
  public_slug: string;
  is_active: boolean;
};

type EditFormProps = {
  work: Work;
  exhibitionId: string;
};

export default function EditForm({
  work,
  exhibitionId,
}: EditFormProps) {
  const router = useRouter();

  const [title, setTitle] = useState(work.title);
  const [artist, setArtist] = useState(work.artist ?? "");
  const [description, setDescription] = useState(work.description);
  const [audioUrl, setAudioUrl] = useState(work.audio_url ?? "");
  const [audioDescriptionUrl, setAudioDescriptionUrl] = useState(
    work.audio_description_url ?? "",
  );
  const [librasVideoUrl, setLibrasVideoUrl] = useState(
    work.libras_video_url ?? "",
  );
  const [isActive, setIsActive] = useState(work.is_active);

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      const response = await fetch(
        `/api/admin/works/${work.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title,
            artist: artist || null,
            description,
            audio_url: audioUrl || null,
            audio_description_url:
              audioDescriptionUrl || null,
            libras_video_url: librasVideoUrl || null,
            is_active: isActive,
          }),
        },
      );

      if (response.status === 401) {
        router.push("/admin/login");
        return;
      }

      if (!response.ok) {
        setError("Não foi possível atualizar a obra.");
        return;
      }

      router.push(
        `/admin/exhibitions/${exhibitionId}/works`,
      );
      router.refresh();
    } catch {
      setError("Não foi possível atualizar a obra.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="title">Título</label>
        <input
          id="title"
          type="text"
          maxLength={150}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="artist">Artista</label>
        <input
          id="artist"
          type="text"
          maxLength={150}
          value={artist}
          onChange={(event) => setArtist(event.target.value)}
        />
      </div>

      <div>
        <label htmlFor="description">Descrição</label>
        <textarea
          id="description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="audio-url">URL do áudio</label>
        <input
          id="audio-url"
          type="url"
          value={audioUrl}
          onChange={(event) => setAudioUrl(event.target.value)}
        />
      </div>

      <div>
        <label htmlFor="audio-description-url">
          URL da audiodescrição
        </label>
        <input
          id="audio-description-url"
          type="url"
          value={audioDescriptionUrl}
          onChange={(event) =>
            setAudioDescriptionUrl(event.target.value)
          }
        />
      </div>

      <div>
        <label htmlFor="libras-video-url">
          URL do vídeo em Libras
        </label>
        <input
          id="libras-video-url"
          type="url"
          value={librasVideoUrl}
          onChange={(event) =>
            setLibrasVideoUrl(event.target.value)
          }
        />
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={isActive}
            onChange={(event) =>
              setIsActive(event.target.checked)
            }
          />
          Obra ativa
        </label>
      </div>

      {error && <p>{error}</p>}

      <button type="submit" disabled={submitting}>
        {submitting ? "Salvando..." : "Salvar alterações"}
      </button>
    </form>
  );
}