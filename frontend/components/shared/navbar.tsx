"use client";

import Link from "next/link";
import { LogOut, User, Stethoscope } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { useAuth } from "@/hooks/useAuth";
import { formatSpecialization } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const { user } = useAuthStore();
  const { logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-slate-100 shadow-sm dark:bg-slate-950 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2.5 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Stethoscope className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-slate-900 dark:text-white tracking-tight">
            Doctor<span className="text-blue-600">_zenZ</span>
          </span>
        </Link>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {user && (
            <Link href="/profile" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center group-hover:bg-slate-200 transition-colors dark:bg-slate-800">
                <User className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              </div>
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-slate-900 dark:text-white leading-tight">
                  {user.full_name}
                </p>
                {user.specialization && (
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {formatSpecialization(user.specialization)}
                  </p>
                )}
              </div>
            </Link>
          )}
          <Button variant="ghost" size="sm" onClick={logout} className="gap-1.5 text-slate-500 hover:text-slate-900">
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
