"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const SPECIALIZATIONS = [
  { value: "general_physician", label: "General Physician" },
  { value: "cardiologist", label: "Cardiologist" },
  { value: "neurologist", label: "Neurologist" },
  { value: "orthopedist", label: "Orthopedist" },
  { value: "dermatologist", label: "Dermatologist" },
  { value: "pediatrician", label: "Pediatrician" },
  { value: "gynecologist", label: "Gynecologist" },
  { value: "psychiatrist", label: "Psychiatrist" },
  { value: "ophthalmologist", label: "Ophthalmologist" },
  { value: "ent_specialist", label: "ENT Specialist" },
  { value: "urologist", label: "Urologist" },
  { value: "gastroenterologist", label: "Gastroenterologist" },
  { value: "endocrinologist", label: "Endocrinologist" },
  { value: "pulmonologist", label: "Pulmonologist" },
  { value: "nephrologist", label: "Nephrologist" },
  { value: "oncologist", label: "Oncologist" },
  { value: "emergency_medicine", label: "Emergency Medicine" },
  { value: "other", label: "Other" },
];

const schema = z.object({
  full_name: z.string().min(2, "Full name is required"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters").max(72, "Password cannot exceed 72 characters"),
  confirm_password: z.string().max(72, "Password cannot exceed 72 characters"),
  role: z.enum(["doctor", "admin"]),
  specialization: z.string().optional(),
  license_number: z.string().optional(),
  hospital_name: z.string().optional(),
  phone_number: z.string().optional(),
}).refine((d) => d.password === d.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const { register: authRegister } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, control, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: "doctor" },
  });

  const role = watch("role");

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      await authRegister(data);
      toast({ title: "Account created!", description: "Please sign in to continue.", variant: "success" });
    } catch (e) {
      toast({ title: "Registration failed", description: getErrorMessage(e), variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-lg my-8">
      <CardHeader className="pb-2">
        <CardTitle className="text-2xl">Create account</CardTitle>
        <CardDescription>Join Doctor_zenZ as a medical professional</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Full name */}
          <div className="space-y-1.5">
            <Label htmlFor="full_name">Full name</Label>
            <Input id="full_name" placeholder="Dr. Arjun Sharma" {...register("full_name")} />
            {errors.full_name && <p className="text-xs text-red-500">{errors.full_name.message}</p>}
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="doctor@hospital.com" {...register("email")} />
            {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
          </div>

          {/* Password row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="••••••••" {...register("password")} />
              {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm_password">Confirm</Label>
              <Input id="confirm_password" type="password" placeholder="••••••••" {...register("confirm_password")} />
              {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password.message}</p>}
            </div>
          </div>

          {/* Role */}
          <div className="space-y-1.5">
            <Label>Role</Label>
            <Controller
              control={control}
              name="role"
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="doctor">Doctor</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          {/* Specialization — only if doctor */}
          {role === "doctor" && (
            <div className="space-y-1.5">
              <Label>Specialization</Label>
              <Controller
                control={control}
                name="specialization"
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select specialization" />
                    </SelectTrigger>
                    <SelectContent>
                      {SPECIALIZATIONS.map((s) => (
                        <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
          )}

          {/* License + Hospital row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="license_number">License No.</Label>
              <Input id="license_number" placeholder="MCI-123456" {...register("license_number")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="phone_number">Phone</Label>
              <Input id="phone_number" placeholder="+91 98765 43210" {...register("phone_number")} />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="hospital_name">Hospital / Clinic</Label>
            <Input id="hospital_name" placeholder="AIIMS, New Delhi" {...register("hospital_name")} />
          </div>

          <Button type="submit" className="w-full" loading={loading}>
            Create account
          </Button>

          <p className="text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link href="/login" className="text-blue-600 hover:underline font-medium">Sign in</Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
