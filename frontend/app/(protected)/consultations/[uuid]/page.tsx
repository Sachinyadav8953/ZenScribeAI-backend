"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Calendar, Clock, FileText, User } from "lucide-react";
import { Consultation, Transcript } from "@/types";
import { consultationService } from "@/services/consultationService";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage, formatDate, formatDuration, formatSpecialization } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/consultation/status-badge";
import { ChatTranscript } from "@/components/transcript/chat-transcript";

export default function ConsultationDetailPage() {
  const params = useParams();
  const uuid = params.uuid as string;
  const { toast } = useToast();

  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [c, t] = await Promise.allSettled([
          consultationService.get(uuid),
          consultationService.getTranscripts(uuid),
        ]);
        if (c.status === "fulfilled") setConsultation(c.value);
        if (t.status === "fulfilled") setTranscripts(t.value);
      } catch (e) {
        toast({ title: "Failed to load consultation", description: getErrorMessage(e), variant: "destructive" });
      } finally {
        setLoading(false);
      }
    })();
  }, [uuid]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!consultation) return null;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back */}
      <div className="flex items-center justify-between">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="gap-1.5 text-slate-500 hover:text-slate-900 pl-0">
            <ArrowLeft className="w-4 h-4" />
            Dashboard
          </Button>
        </Link>
        {consultation.status === "in_progress" && (
          <Link href={`/consultations/${uuid}/room`}>
            <Button size="sm" className="gap-1.5">
              Return to Room
            </Button>
          </Link>
        )}
      </div>

      {/* Patient info + metadata */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">{consultation.patient_name}</CardTitle>
              <div className="flex items-center gap-2 mt-1 text-sm text-slate-500">
                {consultation.patient_age && <span>{consultation.patient_age} years</span>}
                {consultation.patient_gender && (
                  <>
                    <span>·</span>
                    <span className="capitalize">{consultation.patient_gender}</span>
                  </>
                )}
                {consultation.patient_phone && (
                  <>
                    <span>·</span>
                    <span>{consultation.patient_phone}</span>
                  </>
                )}
              </div>
            </div>
            <StatusBadge status={consultation.status} />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {consultation.chief_complaint && (
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Chief Complaint</p>
              <p className="text-sm text-slate-700 dark:text-slate-300">{consultation.chief_complaint}</p>
            </div>
          )}

          {/* Metadata grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-start gap-2">
              <Calendar className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-slate-400">Date</p>
                <p className="text-sm text-slate-700 dark:text-slate-300 font-medium">
                  {formatDate(consultation.created_at)}
                </p>
              </div>
            </div>
            {consultation.started_at && (
              <div className="flex items-start gap-2">
                <Clock className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs text-slate-400">Duration</p>
                  <p className="text-sm text-slate-700 dark:text-slate-300 font-medium">
                    {formatDuration(consultation.started_at, consultation.ended_at)}
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Transcript */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-slate-400" />
            <CardTitle className="text-base">Transcript</CardTitle>
            <span className="text-xs text-slate-400 ml-auto">{transcripts.length} segments</span>
          </div>
        </CardHeader>
        <CardContent>
          <ChatTranscript transcripts={transcripts} />
        </CardContent>
      </Card>

      {/* SOAP Note placeholder */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-slate-400" />
            <CardTitle className="text-base">SOAP Note</CardTitle>
            <span className="text-xs bg-yellow-50 text-yellow-700 ring-1 ring-yellow-200 rounded px-1.5 py-0.5 font-medium ml-auto">
              AI Processing
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-dashed border-slate-200 dark:border-slate-700 p-8 text-center">
            <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-3">
              <FileText className="w-5 h-5 text-slate-400" />
            </div>
            <p className="text-sm font-medium text-slate-500">SOAP note will appear here after AI processing</p>
            <p className="text-xs text-slate-400 mt-1">
              Subjective · Objective · Assessment · Plan
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
