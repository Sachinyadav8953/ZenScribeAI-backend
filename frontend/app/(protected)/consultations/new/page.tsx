"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useConsultation } from "@/hooks/useConsultation";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft } from "lucide-react";

const schema = z.object({
  patient_name: z.string().min(2, "Patient name is required"),
  patient_age: z.string().optional(),
  patient_gender: z.enum(["male", "female", "other", ""]).optional(),
  patient_phone: z.string().optional(),
  chief_complaint: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export default function NewConsultationPage() {
  const router = useRouter();
  const { create } = useConsultation();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, control, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const consultation = await create({
        patient_name: data.patient_name,
        patient_age: data.patient_age ? parseInt(data.patient_age) : undefined,
        patient_gender: data.patient_gender as any || undefined,
        patient_phone: data.patient_phone || undefined,
        chief_complaint: data.chief_complaint || undefined,
      });
      if (consultation) {
        router.push(`/consultations/${consultation.uuid}/room`);
      }
    } catch (e) {
      toast({ title: "Failed to create consultation", description: getErrorMessage(e), variant: "destructive" });
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Back */}
      <Link href="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to dashboard
      </Link>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">New Consultation</CardTitle>
          <CardDescription>Enter patient details to begin the session</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Patient name */}
            <div className="space-y-1.5">
              <Label htmlFor="patient_name">
                Patient full name <span className="text-red-500">*</span>
              </Label>
              <Input id="patient_name" placeholder="Ramesh Kumar" {...register("patient_name")} />
              {errors.patient_name && <p className="text-xs text-red-500">{errors.patient_name.message}</p>}
            </div>

            {/* Age + Gender row */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="patient_age">Age</Label>
                <Input id="patient_age" type="number" min="0" max="150" placeholder="45" {...register("patient_age")} />
              </div>
              <div className="space-y-1.5">
                <Label>Gender</Label>
                <Controller
                  control={control}
                  name="patient_gender"
                  render={({ field }) => (
                    <Select value={field.value ?? ""} onValueChange={field.onChange}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                />
              </div>
            </div>

            {/* Phone */}
            <div className="space-y-1.5">
              <Label htmlFor="patient_phone">Phone number</Label>
              <Input id="patient_phone" type="tel" placeholder="+91 98765 43210" {...register("patient_phone")} />
            </div>

            {/* Chief complaint */}
            <div className="space-y-1.5">
              <Label htmlFor="chief_complaint">Chief complaint</Label>
              <Textarea
                id="chief_complaint"
                placeholder="Describe the main reason for visit..."
                className="min-h-[100px]"
                {...register("chief_complaint")}
              />
            </div>

            <div className="flex gap-3 pt-2">
              <Button type="submit" className="flex-1" loading={loading}>
                Start Consultation
              </Button>
              <Link href="/dashboard" className="flex-1">
                <Button type="button" variant="outline" className="w-full">
                  Cancel
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
