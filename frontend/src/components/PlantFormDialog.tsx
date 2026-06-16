import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { plantSchema, LOCATION_OPTIONS, type PlantFormValues } from "@/lib/schemas";
import type { Plant } from "@/types";

interface PlantFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  plant?: Plant;
  onSubmit: (data: PlantFormValues) => Promise<void>;
}

/**
 * 植物新增/编辑对话框。
 */
export function PlantFormDialog({
  open,
  onOpenChange,
  plant,
  onSubmit,
}: PlantFormDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PlantFormValues>({
    resolver: zodResolver(plantSchema),
    defaultValues: {
      name: plant?.name ?? "",
      variety: plant?.variety ?? "",
      purchase_date: plant?.purchase_date ?? "",
      location: plant?.location ?? "客厅",
    },
  });

  const handleOpenChange = (next: boolean) => {
    if (next) {
      reset({
        name: plant?.name ?? "",
        variety: plant?.variety ?? "",
        purchase_date: plant?.purchase_date ?? "",
        location: plant?.location ?? "客厅",
      });
    }
    onOpenChange(next);
  };

  const submit = async (data: PlantFormValues) => {
    await onSubmit(data);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{plant ? "编辑植物" : "添加植物"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(submit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">名称</Label>
            <Input id="name" placeholder="如：绿萝" {...register("name")} />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="variety">品种</Label>
            <Input
              id="variety"
              placeholder="如：黄金葛"
              {...register("variety")}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="purchase_date">购入日期</Label>
            <Input id="purchase_date" type="date" {...register("purchase_date")} />
            {errors.purchase_date && (
              <p className="text-sm text-destructive">
                {errors.purchase_date.message}
              </p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="location">摆放位置</Label>
            <Select id="location" {...register("location")}>
              {LOCATION_OPTIONS.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </Select>
            {errors.location && (
              <p className="text-sm text-destructive">
                {errors.location.message}
              </p>
            )}
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
