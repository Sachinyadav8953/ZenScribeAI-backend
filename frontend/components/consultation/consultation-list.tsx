"use client";

import Link from "next/link";
import { Eye, Mic, Trash2 } from "lucide-react";
import { Consultation } from "@/types";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "./status-badge";
import { formatDate } from "@/lib/utils";

interface ConsultationListProps {
  consultations: Consultation[];
  loading: boolean;
  onDelete?: (uuid: string) => void;
}

export function ConsultationList({ consultations, loading, onDelete }: ConsultationListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (consultations.length === 0) {
    return (
      <div className="text-center py-16 text-slate-400">
        <p className="text-sm">No consultations yet.</p>
        <p className="text-xs mt-1">Click <strong className="text-slate-600">New Consultation</strong> to get started.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 dark:border-slate-800">
            <th className="text-left py-3 px-4 font-medium text-slate-500 text-xs uppercase tracking-wider">Patient</th>
            <th className="text-left py-3 px-4 font-medium text-slate-500 text-xs uppercase tracking-wider hidden md:table-cell">Chief Complaint</th>
            <th className="text-left py-3 px-4 font-medium text-slate-500 text-xs uppercase tracking-wider">Status</th>
            <th className="text-left py-3 px-4 font-medium text-slate-500 text-xs uppercase tracking-wider hidden sm:table-cell">Time</th>
            <th className="text-right py-3 px-4 font-medium text-slate-500 text-xs uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
          {consultations.map((c) => (
            <tr key={c.uuid} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
              <td className="py-3 px-4">
                <div>
                  <p className="font-medium text-slate-900 dark:text-slate-100">{c.patient_name}</p>
                  {c.patient_age && (
                    <p className="text-xs text-slate-400">
                      {c.patient_age}y {c.patient_gender && `· ${c.patient_gender}`}
                    </p>
                  )}
                </div>
              </td>
              <td className="py-3 px-4 hidden md:table-cell">
                <p className="text-slate-600 dark:text-slate-400 truncate max-w-[200px]">
                  {c.chief_complaint || <span className="text-slate-300">—</span>}
                </p>
              </td>
              <td className="py-3 px-4">
                <StatusBadge status={c.status} />
              </td>
              <td className="py-3 px-4 hidden sm:table-cell text-slate-400 text-xs whitespace-nowrap">
                {formatDate(c.created_at)}
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center justify-end gap-1">
                  {c.status === "in_progress" && (
                    <Link href={`/consultations/${c.uuid}/room`}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50">
                        <Mic className="h-4 w-4" />
                      </Button>
                    </Link>
                  )}
                  <Link href={`/consultations/${c.uuid}`}>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-slate-500 hover:text-slate-900">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </Link>
                  {onDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-slate-400 hover:text-red-600 hover:bg-red-50"
                      onClick={() => onDelete(c.uuid)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
