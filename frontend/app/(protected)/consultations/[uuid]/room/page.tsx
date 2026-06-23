"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { Mic, MicOff, Square, Edit2, Check, X, WifiOff } from "lucide-react";
import { useConsultation } from "@/hooks/useConsultation";
import { useAudioStream } from "@/hooks/useAudioStream";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage, formatSpecialization } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/consultation/status-badge";
import { LiveTranscript } from "@/components/transcript/live-transcript";
import { consultationService } from "@/services/consultationService";
import { Consultation } from "@/types";

function ConsultationTimer({ startedAt }: { startedAt?: string }) {
  const [elapsed, setElapsed] = useState("00:00");

  useEffect(() => {
    if (!startedAt) return;
    const tick = () => {
      const start = new Date(startedAt).getTime();
      const diff = Date.now() - start;
      const mins = Math.floor(diff / 60000);
      const secs = Math.floor((diff % 60000) / 1000);
      setElapsed(`${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [startedAt]);

  return (
    <div className="text-center">
      <p className="text-4xl font-mono font-light text-slate-900 dark:text-white tracking-widest">{elapsed}</p>
      <p className="text-xs text-slate-400 mt-1">Duration</p>
    </div>
  );
}

export default function ConsultationRoomPage() {
  const params = useParams();
  const uuid = params.uuid as string;
  const router = useRouter();
  const { toast } = useToast();

  const { fetchOne, endConsultation } = useConsultation();
  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [pageLoading, setPageLoading] = useState(true);
  const [ending, setEnding] = useState(false);

  // Inline edit state
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editComplaint, setEditComplaint] = useState("");
  const [savingEdit, setSavingEdit] = useState(false);

  const { startRecording, stopRecording, transcripts, isRecording, isConnected, error: wsError } = useAudioStream(uuid);

  // Load consultation
  useEffect(() => {
    (async () => {
      try {
        const data = await consultationService.get(uuid);
        setConsultation(data);
        setEditName(data.patient_name);
        setEditComplaint(data.chief_complaint ?? "");
      } catch (e) {
        toast({ title: "Failed to load consultation", description: getErrorMessage(e), variant: "destructive" });
      } finally {
        setPageLoading(false);
      }
    })();
  }, [uuid]);

  // Show WS errors as toast
  useEffect(() => {
    if (wsError) {
      toast({ title: "Recording issue", description: wsError, variant: "destructive" });
    }
  }, [wsError]);

  const handleStartRecording = async () => {
    try {
      await startRecording();
    } catch (e) {
      toast({ title: "Could not start recording", description: getErrorMessage(e), variant: "destructive" });
    }
  };

  const handleSaveEdit = async () => {
    if (!consultation) return;
    setSavingEdit(true);
    try {
      const updated = await consultationService.update(uuid, {
        patient_name: editName,
        chief_complaint: editComplaint,
      });
      setConsultation(updated);
      setIsEditing(false);
      toast({ title: "Patient info updated", variant: "success" });
    } catch (e) {
      toast({ title: "Update failed", description: getErrorMessage(e), variant: "destructive" });
    } finally {
      setSavingEdit(false);
    }
  };

  const handleEndConsultation = async () => {
    if (isRecording) stopRecording();
    setEnding(true);
    try {
      await endConsultation(uuid);
      toast({ title: "Consultation ended", variant: "success" });
      router.push(`/consultations/${uuid}`);
    } catch (e) {
      toast({ title: "Failed to end consultation", description: getErrorMessage(e), variant: "destructive" });
      setEnding(false);
    }
  };

  if (pageLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-2">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-slate-500">Loading consultation...</p>
        </div>
      </div>
    );
  }

  if (!consultation) return null;

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col lg:flex-row gap-4 overflow-hidden">
      {/* ═══════════════ LEFT PANEL (40%) ═══════════════ */}
      <div className="w-full lg:w-2/5 flex flex-col gap-4 overflow-y-auto lg:overflow-hidden">
        {/* Patient info card */}
        <Card className="p-5">
          <div className="flex items-start justify-between mb-3">
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-1">Patient</p>
              {isEditing ? (
                <Input
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="text-lg font-semibold h-9 mb-2"
                  placeholder="Patient name"
                />
              ) : (
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">{consultation.patient_name}</h2>
              )}
              <div className="flex items-center gap-2 mt-1 text-sm text-slate-500">
                {consultation.patient_age && <span>{consultation.patient_age}y</span>}
                {consultation.patient_age && consultation.patient_gender && <span>·</span>}
                {consultation.patient_gender && (
                  <span className="capitalize">{consultation.patient_gender}</span>
                )}
                {consultation.patient_phone && (
                  <>
                    <span>·</span>
                    <span>{consultation.patient_phone}</span>
                  </>
                )}
              </div>
            </div>
            {!isEditing ? (
              <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)} className="h-8 w-8 p-0">
                <Edit2 className="w-4 h-4 text-slate-400" />
              </Button>
            ) : (
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" onClick={handleSaveEdit} loading={savingEdit} className="h-8 w-8 p-0">
                  <Check className="w-4 h-4 text-green-600" />
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setIsEditing(false)} className="h-8 w-8 p-0">
                  <X className="w-4 h-4 text-slate-400" />
                </Button>
              </div>
            )}
          </div>

          {/* Chief complaint */}
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-1.5">Chief Complaint</p>
            {isEditing ? (
              <Textarea
                value={editComplaint}
                onChange={(e) => setEditComplaint(e.target.value)}
                placeholder="Chief complaint..."
                className="text-sm min-h-[70px]"
              />
            ) : (
              <p className="text-sm text-slate-700 dark:text-slate-300">
                {consultation.chief_complaint || <span className="text-slate-300 italic">Not specified</span>}
              </p>
            )}
          </div>
        </Card>

        {/* Status + Timer */}
        <Card className="p-5 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">Status</p>
            <StatusBadge status={consultation.status} />
          </div>
          <ConsultationTimer startedAt={consultation.started_at ?? consultation.created_at} />
        </Card>

        {/* Recording controls */}
        <Card className="p-5 space-y-5">
          <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">Recording</p>

          {/* Mic button */}
          <div className="flex flex-col items-center gap-4">
            <button
              onClick={isRecording ? stopRecording : handleStartRecording}
              className={`w-20 h-20 rounded-full flex items-center justify-center shadow-md transition-all focus:outline-none focus:ring-4 ${
                isRecording
                  ? "bg-red-500 hover:bg-red-600 focus:ring-red-200 scale-105"
                  : "bg-slate-100 hover:bg-slate-200 focus:ring-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700"
              }`}
            >
              {isRecording ? (
                <MicOff className="w-8 h-8 text-white" />
              ) : (
                <Mic className="w-8 h-8 text-slate-600 dark:text-slate-300" />
              )}
            </button>

            {/* Status indicator */}
            <div className="flex items-center gap-2 text-sm">
              {isRecording ? (
                <>
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
                  <span className="text-red-600 font-medium">Recording — tap to stop</span>
                </>
              ) : wsError ? (
                <>
                  <WifiOff className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-500 text-xs">Disconnected</span>
                </>
              ) : (
                <>
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-300 dark:bg-slate-600" />
                  <span className="text-slate-500">Tap microphone to start</span>
                </>
              )}
            </div>
          </div>
        </Card>

        {/* End consultation */}
        <Button
          variant="destructive"
          className="w-full h-12 text-base"
          onClick={handleEndConsultation}
          loading={ending}
          disabled={consultation.status !== "in_progress"}
        >
          <Square className="w-4 h-4 mr-2" />
          End Consultation
        </Button>
      </div>

      {/* ═══════════════ RIGHT PANEL (60%) ═══════════════ */}
      <div className="w-full lg:w-3/5 flex flex-col min-h-[400px] lg:min-h-0">
        <Card className="flex-1 flex flex-col overflow-hidden">
          <LiveTranscript transcripts={transcripts} isRecording={isRecording} />
        </Card>
      </div>
    </div>
  );
}
