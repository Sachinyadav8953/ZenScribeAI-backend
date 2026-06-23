"use client";

import { useCallback, useState } from "react";
import { useConsultationStore } from "@/stores/consultationStore";
import { consultationService } from "@/services/consultationService";
import { CreateConsultationRequest } from "@/types";

export function useConsultation() {
  const {
    consultations,
    currentConsultation,
    setConsultations,
    setCurrentConsultation,
    updateConsultationStatus,
  } = useConsultationStore();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const data = await consultationService.list();
      setConsultations(data);
    } catch (e) {
      setError("Failed to load consultations");
    } finally {
      setLoading(false);
    }
  }, [setConsultations]);

  const fetchOne = useCallback(
    async (uuid: string) => {
      setLoading(true);
      try {
        const data = await consultationService.get(uuid);
        setCurrentConsultation(data);
        return data;
      } catch (e) {
        setError("Failed to load consultation");
      } finally {
        setLoading(false);
      }
    },
    [setCurrentConsultation]
  );

  const create = useCallback(
    async (data: CreateConsultationRequest) => {
      setLoading(true);
      try {
        const created = await consultationService.create(data);
        setCurrentConsultation(created);
        return created;
      } finally {
        setLoading(false);
      }
    },
    [setCurrentConsultation]
  );

  const endConsultation = useCallback(
    async (uuid: string) => {
      setLoading(true);
      try {
        const updated = await consultationService.end(uuid);
        setCurrentConsultation(updated);
        updateConsultationStatus(uuid, "completed");
        return updated;
      } finally {
        setLoading(false);
      }
    },
    [setCurrentConsultation, updateConsultationStatus]
  );

  return {
    consultations,
    currentConsultation,
    loading,
    error,
    fetchAll,
    fetchOne,
    create,
    endConsultation,
  };
}
