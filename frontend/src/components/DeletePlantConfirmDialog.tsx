import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface DeletePlantConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  plantName: string;
  repottingCount: number;
  wateringCount?: number;
  onConfirm: () => Promise<void> | void;
}

export function DeletePlantConfirmDialog({
  open,
  onOpenChange,
  plantName,
  repottingCount,
  wateringCount,
  onConfirm,
}: DeletePlantConfirmDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async () => {
    setIsDeleting(true);
    try {
      await onConfirm();
    } finally {
      setIsDeleting(false);
      onOpenChange(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!isDeleting) {
      onOpenChange(open);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            确认删除植物
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-base">
            确定要删除植物{" "}
            <span className="font-semibold text-destructive">「{plantName}」</span>{" "}
            吗？
          </p>
          <div className="rounded-lg border bg-muted/50 p-4 space-y-2 text-sm">
            <p className="flex items-center justify-between">
              <span className="text-muted-foreground">关联换盆记录</span>
              <span className="font-medium">{repottingCount} 条</span>
            </p>
            {wateringCount !== undefined && (
              <p className="flex items-center justify-between">
                <span className="text-muted-foreground">关联浇水记录</span>
                <span className="font-medium">{wateringCount} 条</span>
              </p>
            )}
            <p className="pt-2 text-destructive text-xs border-t">
              删除后以上所有关联数据将永久清除，且无法恢复。
            </p>
          </div>
        </div>
        <div className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isDeleting}
          >
            取消
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? "删除中..." : "确认删除"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
