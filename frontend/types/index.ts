export type UserRole = "doctor" | "admin" | "superadmin";

export type Specialization =
  | "general_physician"
  | "cardiologist"
  | "neurologist"
  | "orthopedist"
  | "dermatologist"
  | "pediatrician"
  | "gynecologist"
  | "psychiatrist"
  | "ophthalmologist"
  | "ent_specialist"
  | "urologist"
  | "gastroenterologist"
  | "endocrinologist"
  | "pulmonologist"
  | "nephrologist"
  | "oncologist"
  | "radiologist"
  | "anesthesiologist"
  | "emergency_medicine"
  | "other";

export type ConsultationStatus = "in_progress" | "completed" | "cancelled";

export type Speaker = "doctor" | "patient" | "unknown";

export type Gender = "male" | "female" | "other";

export interface User {
  id: number;
  uuid: string;
  full_name: string;
  email: string;
  role: UserRole;
  specialization?: Specialization;
  license_number?: string;
  license_verified: boolean;
  hospital_name?: string;
  phone_number?: string;
  is_email_verified: boolean;
  is_active: boolean;
  created_at: string;
}

export interface Consultation {
  id: number;
  uuid: string;
  doctor_id: number;
  patient_name: string;
  patient_age?: number;
  patient_gender?: Gender;
  patient_phone?: string;
  chief_complaint?: string;
  status: ConsultationStatus;
  started_at?: string;
  ended_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Transcript {
  id: number;
  uuid: string;
  consultation_id: number;
  speaker: Speaker;
  text: string;
  timestamp_start?: number;
  timestamp_end?: number;
  confidence?: number;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
  specialization?: Specialization;
  license_number?: string;
  hospital_name?: string;
  phone_number?: string;
}

export interface CreateConsultationRequest {
  patient_name: string;
  patient_age?: number;
  patient_gender?: Gender;
  patient_phone?: string;
  chief_complaint?: string;
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
