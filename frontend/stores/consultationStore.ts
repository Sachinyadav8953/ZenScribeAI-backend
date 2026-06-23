"use client";

import { create } from "zustand";
import { Consultation, Transcript } from "@/types";

interface ConsultationState {
  currentConsultation: Consultation | null;
  consultations: Consultation[];
  transcripts: Transcript[];
  setCurrentConsultation: (c: Consultation | null) => void;
  setConsultations: (list: Consultation[]) => void;
  addTranscript: (t: Transcript) => void;
  clearTranscripts: () => void;
  updateConsultationStatus: (uuid: string, status: Consultation["status"]) => void;
}

export const useConsultationStore = create<ConsultationState>((set) => ({
  currentConsultation: null,
  consultations: [],
  transcripts: [],

  setCurrentConsultation: (c) => set({ currentConsultation: c }),

  setConsultations: (list) => set({ consultations: list }),

  addTranscript: (t) =>
    set((state) => ({ transcripts: [...state.transcripts, t] })),

  clearTranscripts: () => set({ transcripts: [] }),

  updateConsultationStatus: (uuid, status) =>
    set((state) => ({
      consultations: state.consultations.map((c) =>
        c.uuid === uuid ? { ...c, status } : c
      ),
      currentConsultation:
        state.currentConsultation?.uuid === uuid
          ? { ...state.currentConsultation, status }
          : state.currentConsultation,
    })),
}));
