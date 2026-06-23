import { Transcript } from "@/types";

interface ChatTranscriptProps {
  transcripts: Transcript[];
}

function formatTime(dateString: string): string {
  return new Date(dateString).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ChatTranscript({ transcripts }: ChatTranscriptProps) {
  if (transcripts.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p className="text-sm">No transcript available for this consultation.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {transcripts.map((t) => {
        const isDoctor = t.speaker === "doctor";
        return (
          <div
            key={t.uuid || t.id}
            className={`flex ${isDoctor ? "justify-start" : "justify-end"}`}
          >
            <div className={`max-w-[75%] ${isDoctor ? "order-2" : "order-1"}`}>
              {/* Speaker label */}
              <p className={`text-xs font-semibold uppercase tracking-wide mb-1 ${isDoctor ? "text-blue-600" : "text-slate-400"}`}>
                {t.speaker}
              </p>
              {/* Bubble */}
              <div
                className={`rounded-2xl px-4 py-2.5 ${
                  isDoctor
                    ? "bg-blue-50 text-slate-800 rounded-tl-sm dark:bg-blue-900/20 dark:text-slate-200"
                    : "bg-slate-100 text-slate-800 rounded-tr-sm dark:bg-slate-800 dark:text-slate-200"
                }`}
              >
                <p className="text-sm leading-relaxed">{t.text}</p>
              </div>
              {/* Timestamp */}
              <p className={`text-xs text-slate-400 mt-1 ${isDoctor ? "text-left" : "text-right"}`}>
                {formatTime(t.created_at)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
