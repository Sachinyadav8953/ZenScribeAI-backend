"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useSearchParams, useRouter } from "next/navigation";
import { authService } from "@/services/authService";
import { useToast } from "@/components/ui/toaster";
import { getErrorMessage } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const schema = z.object({
  new_password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

type FormData = z.infer<typeof schema>;

export default function ResetPasswordPage() {
  const { toast } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    if (!token) {
      toast({ title: "Invalid link", description: "Reset token is missing.", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      await authService.resetPassword(token, data.new_password);
      toast({ title: "Password reset!", description: "You can now sign in with your new password.", variant: "success" });
      router.push("/login");
    } catch (e) {
      toast({ title: "Reset failed", description: getErrorMessage(e), variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-2">
        <CardTitle className="text-2xl">New password</CardTitle>
        <CardDescription>Set a new password for your account</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="new_password">New password</Label>
            <Input id="new_password" type="password" placeholder="••••••••" {...register("new_password")} />
            {errors.new_password && <p className="text-xs text-red-500">{errors.new_password.message}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="confirm_password">Confirm password</Label>
            <Input id="confirm_password" type="password" placeholder="••••••••" {...register("confirm_password")} />
            {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password.message}</p>}
          </div>
          <Button type="submit" className="w-full" loading={loading}>
            Set new password
          </Button>
          <p className="text-center text-sm text-slate-500">
            <Link href="/login" className="text-blue-600 hover:underline">Back to sign in</Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
