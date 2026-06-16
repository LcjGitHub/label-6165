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
  onConfirm: () => Promise<void> | void;
}

/**
 * 删除植物确认对话框：展示植物名称及关联换盆记录条数，用户确认后执行删除。
 */
export function DeletePlantConfirmDialog({
  open,
  onOpenChange,
  plantName,
  repottingCount,
  onConfirm,
}: DeletePlantConfirmDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleConfirm = async () => {
    setIsDeleting(true);
    setErrorMessage(null);
    try {
      await onConfirm();
      onOpenChange(false);
    } catch {
      setErrorMessage("删除失败，请稍后重试");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!isDeleting) {
      setErrorMessage(null);
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
            <p className="pt-2 text-destructive text-xs border-t">
              删除后关联换盆记录将永久清除，且无法恢复。
            </p>
          </div>
          {errorMessage && (
            <p className="text-sm text-destructive">{errorMessage}</p>
          )}
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
