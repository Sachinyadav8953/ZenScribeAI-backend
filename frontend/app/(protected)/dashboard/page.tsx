"use client";

import { useEffect, useMemo } from "react";
import Link from "next/link";
import { Plus, Activity, CheckCircle2, Clock } from "lucide-react";
import { useConsultation } from "@/hooks/useConsultation";
import { useAuthStore } from "@/stores/authStore";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ConsultationList } from "@/components/consultation/consultation-list";
import { consultationService } from "@/services/consultationService";

function isToday(dateStr: string) {
  const d = new Date(dateStr);
  const now = new Date();
  return d.getDate() === now.getDate() &&
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear();
}

export default function DashboardPage() {
  const { consultations, loading, fetchAll, setConsultations } = useConsultation() as any;
  const { user } = useAuthStore();
  const { toast } = useToast();

  useEffect(() => { fetchAll(); }, []);

  const todayConsultations = useMemo(
    () => consultations.filter((c: any) => isToday(c.created_at)),
    [consultations]
  );

  const stats = useMemo(() => ({
    total: todayConsultations.length,
    inProgress: todayConsultations.filter((c: any) => c.status === "in_progress").length,
    completed: todayConsultations.filter((c: any) => c.status === "completed").length,
  }), [todayConsultations]);

  const handleDelete = async (uuid: string) => {
    try {
      await consultationService.delete(uuid);
      await fetchAll();
      toast({ title: "Consultation deleted", variant: "success" });
    } catch (e) {
      toast({ title: "Delete failed", description: getErrorMessage(e), variant: "destructive" });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 17 ? "afternoon" : "evening"},{" "}
            {user?.full_name?.split(" ")[0] ?? "Doctor"}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}
          </p>
        </div>
        <Link href="/consultations/new">
          <Button className="gap-2">
            <Plus className="w-4 h-4" />
            New Consultation
          </Button>
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Today Total</p>
                <p className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{stats.total}</p>
              </div>
              <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-slate-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">In Progress</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{stats.inProgress}</p>
              </div>
              <div className="w-10 h-10 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Completed</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.completed}</p>
              </div>
              <div className="w-10 h-10 bg-green-50 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Consultation list */}
      <Card>
        <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800">
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">Recent Consultations</h2>
          <p className="text-xs text-slate-400 mt-0.5">All your consultations, newest first</p>
        </div>
        <ConsultationList
          consultations={[...consultations].sort(
            (a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )}
          loading={loading}
          onDelete={handleDelete}
        />
      </Card>
    </div>
  );
}
