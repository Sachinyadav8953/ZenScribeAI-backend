import { Badge } from "@/components/ui/badge";
import { ConsultationStatus } from "@/types";

interface StatusBadgeProps {
  status: ConsultationStatus;
}

const statusConfig: Record<ConsultationStatus, { label: string; variant: "blue" | "green" | "gray" }> = {
  in_progress: { label: "In Progress", variant: "blue" },
  completed: { label: "Completed", variant: "green" },
  cancelled: { label: "Cancelled", variant: "gray" },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const { label, variant } = statusConfig[status] ?? { label: status, variant: "gray" };
  return <Badge variant={variant}>{label}</Badge>;
}
