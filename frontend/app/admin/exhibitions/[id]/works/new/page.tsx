"use client";

import { FormEvent, use, useState } from "react";
import { useRouter } from "next/navigation";

type NewWorkPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default function NewWorkPage({
  params,
}: NewWorkPageProps) {
  const { id: exhibitionId } = use(params);

  const router = useRouter();

  const [title, setTitle] = useState("");
  const [artist, setArtist] = useState("");
  const [description, setDescription] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [audioDescriptionUrl, setAudioDescriptionUrl] =
    useState("");
  const [librasVideoUrl, setLibrasVideoUrl] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      const response = await fetch("/api/admin/works", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          exhibition_id: exhibitionId,
          title,
          artist: artist || null,
          description,
          audio_url: audioUrl || null,
          audio_description_url:
            audioDescriptionUrl || null,
          libras_video_url: librasVideoUrl || null,
        }),
      });

      if (response.status === 401) {
        router.push("/admin/login");
        return;
      }

      if (!response.ok) {
        setError("Não foi possível cadastrar a obra.");
        return;
      }

      router.push(
        `/admin/exhibitions/${exhibitionId}/works`,
      );
      router.refresh();
    } catch {
      setError("Não foi possível cadastrar a obra.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Nova obra</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Título</label>
          <input
            id="title"
            type="text"
            maxLength={150}
            value={title}
            onChange={(event) =>
              setTitle(event.target.value)
            }
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
            onChange={(event) =>
              setArtist(event.target.value)
            }
          />
        </div>

        <div>
          <label htmlFor="description">Descrição</label>
          <textarea
            id="description"
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
            required
          />
        </div>

        <div>
          <label htmlFor="audio-url">URL do áudio</label>
          <input
            id="audio-url"
            type="url"
            value={audioUrl}
            onChange={(event) =>
              setAudioUrl(event.target.value)
            }
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

        {error && <p>{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? "Salvando..." : "Cadastrar obra"}
        </button>
      </form>
    </main>
  );
}