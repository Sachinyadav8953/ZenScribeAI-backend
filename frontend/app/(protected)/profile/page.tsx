"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuthStore } from "@/stores/authStore";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage, formatSpecialization, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, Shield, Building2, Phone, Mail, Hash, CheckCircle2 } from "lucide-react";
import apiClient from "@/lib/axios";

const passwordSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string().min(8, "New password must be at least 8 characters"),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

type PasswordForm = z.infer<typeof passwordSchema>;

export default function ProfilePage() {
  const { user } = useAuthStore();
  const { toast } = useToast();
  const [changingPwd, setChangingPwd] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
  });

  const onChangePassword = async (data: PasswordForm) => {
    setChangingPwd(true);
    try {
      await apiClient.post("/auth/change-password", {
        current_password: data.current_password,
        new_password: data.new_password,
      });
      toast({ title: "Password changed successfully", variant: "success" });
      reset();
    } catch (e) {
      toast({ title: "Failed to change password", description: getErrorMessage(e), variant: "destructive" });
    } finally {
      setChangingPwd(false);
    }
  };

  if (!user) return null;

  const fields = [
    { icon: Mail, label: "Email", value: user.email },
    { icon: Hash, label: "License Number", value: user.license_number || "—" },
    { icon: Building2, label: "Hospital / Clinic", value: user.hospital_name || "—" },
    { icon: Phone, label: "Phone", value: user.phone_number || "—" },
    { icon: Shield, label: "Role", value: user.role.charAt(0).toUpperCase() + user.role.slice(1) },
    { icon: CheckCircle2, label: "Member since", value: formatDate(user.created_at) },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Profile</h1>
        <p className="text-sm text-slate-500 mt-0.5">Your account information</p>
      </div>

      {/* Profile card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center shrink-0">
              <User className="w-8 h-8 text-blue-600" />
            </div>
            <div className="flex-1 pt-1">
              <CardTitle className="text-xl">{user.full_name}</CardTitle>
              {user.specialization && (
                <p className="text-sm text-slate-500 mt-0.5">{formatSpecialization(user.specialization)}</p>
              )}
              <div className="flex gap-2 mt-2 flex-wrap">
                {user.license_verified && (
                  <Badge variant="green">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    License Verified
                  </Badge>
                )}
                {user.is_email_verified && (
                  <Badge variant="blue">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Email Verified
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {fields.map(({ icon: Icon, label, value }) => (
              <div key={label} className="flex items-center gap-3 py-2 border-b border-slate-50 dark:border-slate-800 last:border-0">
                <Icon className="w-4 h-4 text-slate-400 shrink-0" />
                <span className="text-xs text-slate-400 w-28 shrink-0">{label}</span>
                <span className="text-sm text-slate-700 dark:text-slate-300">{value}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Change password */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Shield className="w-4 h-4 text-slate-400" />
            Change Password
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onChangePassword)} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="current_password">Current password</Label>
              <Input id="current_password" type="password" placeholder="••••••••" {...register("current_password")} />
              {errors.current_password && <p className="text-xs text-red-500">{errors.current_password.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="new_password">New password</Label>
                <Input id="new_password" type="password" placeholder="••••••••" {...register("new_password")} />
                {errors.new_password && <p className="text-xs text-red-500">{errors.new_password.message}</p>}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="confirm_password">Confirm</Label>
                <Input id="confirm_password" type="password" placeholder="••••••••" {...register("confirm_password")} />
                {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password.message}</p>}
              </div>
            </div>
            <Button type="submit" loading={changingPwd} className="w-full sm:w-auto">
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
