"use client";

import { useEffect, useRef } from "react";
import { Transcript } from "@/types";
import { FileText } from "lucide-react";

interface LiveTranscriptProps {
  transcripts: Transcript[];
  isRecording: boolean;
}

function formatTs(seconds?: number): string {
  if (seconds === undefined) return "";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function LiveTranscript({ transcripts, isRecording }: LiveTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcripts]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-400" />
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">Live Transcript</h2>
        </div>
        {isRecording && (
          <div className="flex items-center gap-1.5 text-xs text-red-600 font-medium">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            Recording
          </div>
        )}
      </div>

      {/* Transcript area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
        {transcripts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center py-16">
            <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-3">
              <FileText className="w-5 h-5 text-slate-400" />
            </div>
            <p className="text-sm font-medium text-slate-500">Start recording to see live transcript</p>
            <p className="text-xs text-slate-400 mt-1">Speech will appear here in real time</p>
          </div>
        ) : (
          transcripts.map((t) => (
            <div key={t.uuid || t.id} className="group">
              <div className="flex items-start gap-3">
                {/* Speaker tag */}
                <span
                  className={`mt-0.5 shrink-0 inline-flex items-center rounded px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${
                    t.speaker === "doctor"
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      : t.speaker === "patient"
                      ? "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                      : "bg-yellow-50 text-yellow-700"
                  }`}
                >
                  {t.speaker}
                </span>
                {/* Text */}
                <div className="flex-1">
                  <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">{t.text}</p>
                  {(t.timestamp_start !== undefined || t.created_at) && (
                    <p className="text-xs text-slate-400 mt-0.5">
                      {t.timestamp_start !== undefined
                        ? formatTs(t.timestamp_start)
                        : new Date(t.created_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
