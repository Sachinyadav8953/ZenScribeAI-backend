import apiClient from "@/lib/axios";
import { Consultation, CreateConsultationRequest, Transcript } from "@/types";

export const consultationService = {
  async create(data: CreateConsultationRequest): Promise<Consultation> {
    const res = await apiClient.post<Consultation>("/consultations/", data);
    return res.data;
  },

  async list(): Promise<Consultation[]> {
    const res = await apiClient.get<Consultation[]>("/consultations/");
    return res.data;
  },

  async get(uuid: string): Promise<Consultation> {
    const res = await apiClient.get<Consultation>(`/consultations/${uuid}`);
    return res.data;
  },

  async update(uuid: string, data: Partial<CreateConsultationRequest>): Promise<Consultation> {
    const res = await apiClient.patch<Consultation>(`/consultations/${uuid}`, data);
    return res.data;
  },

  async end(uuid: string): Promise<Consultation> {
    const res = await apiClient.patch<Consultation>(`/consultations/${uuid}/end`);
    return res.data;
  },

  async delete(uuid: string): Promise<void> {
    await apiClient.delete(`/consultations/${uuid}`);
  },

  async getTranscripts(uuid: string): Promise<Transcript[]> {
    const res = await apiClient.get<Transcript[]>(`/consultations/${uuid}/transcripts`);
    return res.data;
  },
};
