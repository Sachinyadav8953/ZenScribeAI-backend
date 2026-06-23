import { Stethoscope } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">
      {/* Top bar */}
      <div className="flex items-center gap-2.5 p-6">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <Stethoscope className="w-4 h-4 text-white" />
        </div>
        <span className="font-bold text-slate-900 dark:text-white tracking-tight">
          Doctor<span className="text-blue-600">_zenZ</span>
        </span>
      </div>

      {/* Center content */}
      <div className="flex-1 flex items-center justify-center px-4 pb-12">
        {children}
      </div>
    </div>
  );
}
