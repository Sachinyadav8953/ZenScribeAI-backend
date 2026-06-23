import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
  {
    variants: {
      variant: {
        default: "bg-slate-50 text-slate-700 ring-slate-200",
        blue: "bg-blue-50 text-blue-700 ring-blue-200",
        green: "bg-green-50 text-green-700 ring-green-200",
        red: "bg-red-50 text-red-700 ring-red-200",
        gray: "bg-slate-100 text-slate-500 ring-slate-200",
        yellow: "bg-yellow-50 text-yellow-700 ring-yellow-200",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
