import { useEffect } from "react";
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
import { wateringSchema, type WateringFormValues } from "@/lib/schemas";
import type { Watering } from "@/types";

interface WateringFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  record?: Watering;
  onSubmit: (data: WateringFormValues) => Promise<void>;
}

/**
 * 浇水记录新增/编辑对话框。
 */
export function WateringFormDialog({
  open,
  onOpenChange,
  record,
  onSubmit,
}: WateringFormDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<WateringFormValues>({
    resolver: zodResolver(wateringSchema),
    defaultValues: {
      date: "",
      notes: "",
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        date: record?.date ?? "",
        notes: record?.notes ?? "",
      });
    }
  }, [open, record, reset]);

  const handleOpenChange = (next: boolean) => {
    if (!next) {
      reset({ date: "", notes: "" });
    }
    onOpenChange(next);
  };

  const submit = async (data: WateringFormValues) => {
    await onSubmit(data);
    reset({ date: "", notes: "" });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{record ? "编辑浇水记录" : "添加浇水记录"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(submit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="watering-date">浇水日期</Label>
            <Input id="watering-date" type="date" {...register("date")} />
            {errors.date && (
              <p className="text-sm text-destructive">{errors.date.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="watering-notes">备注</Label>
            <Textarea
              id="watering-notes"
              placeholder="浇水量、水质等"
              {...register("notes")}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
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
