"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

type DeleteWorkButtonProps = {
  workId: string;
  workTitle: string;
};

export default function DeleteWorkButton({
  workId,
  workTitle,
}: DeleteWorkButtonProps) {
  const router = useRouter();

  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  async function handleDelete() {
    const confirmed = window.confirm(
      `Deseja realmente excluir a obra "${workTitle}"?`,
    );

    if (!confirmed) {
      return;
    }

    setDeleting(true);
    setError("");

    try {
      const response = await fetch(
        `/api/admin/works/${workId}`,
        {
          method: "DELETE",
        },
      );

      if (response.status === 401) {
        router.push("/admin/login");
        return;
      }

      if (!response.ok) {
        setError("Não foi possível excluir a obra.");
        return;
      }

      router.refresh();
    } catch {
      setError("Não foi possível excluir a obra.");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={handleDelete}
        disabled={deleting}
      >
        {deleting ? "Excluindo..." : "Excluir"}
      </button>

      {error && <p>{error}</p>}
    </>
  );
}