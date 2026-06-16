import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { repottingSchema, type RepottingFormValues } from "@/lib/schemas";
import type { Repotting } from "@/types";

interface RepottingFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  record?: Repotting;
  onSubmit: (data: RepottingFormValues) => Promise<void>;
}

/**
 * 换盆记录新增/编辑对话框。
 */
export function RepottingFormDialog({
  open,
  onOpenChange,
  record,
  onSubmit,
}: RepottingFormDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RepottingFormValues>({
    resolver: zodResolver(repottingSchema),
    defaultValues: {
      date: record?.date ?? "",
      notes: record?.notes ?? "",
    },
  });

  const handleOpenChange = (next: boolean) => {
    if (next) {
      reset({
        date: record?.date ?? "",
        notes: record?.notes ?? "",
      });
    }
    onOpenChange(next);
  };

  const submit = async (data: RepottingFormValues) => {
    await onSubmit(data);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{record ? "编辑换盆记录" : "添加换盆记录"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(submit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="date">换盆日期</Label>
            <Input id="date" type="date" {...register("date")} />
            {errors.date && (
              <p className="text-sm text-destructive">{errors.date.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">备注</Label>
            <Textarea
              id="notes"
              placeholder="换盆详情、土壤配方等"
              {...register("notes")}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              取消
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "保存中…" : "保存"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
