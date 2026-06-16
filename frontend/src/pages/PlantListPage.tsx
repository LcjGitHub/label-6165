import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus, Leaf, Calendar, Pencil, Trash2, BarChart3 } from "lucide-react";
import { fetchPlants, createPlant, updatePlant, deletePlant } from "@/api/plants";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PlantFormDialog } from "@/components/PlantFormDialog";
import type { Plant } from "@/types";
import type { PlantFormValues } from "@/lib/schemas";

/**
 * 植物列表页：展示所有盆栽及换盆次数，支持 CRUD。
 */
export function PlantListPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPlant, setEditingPlant] = useState<Plant | undefined>();

  const { data: plants, isLoading, error } = useQuery({
    queryKey: ["plants"],
    queryFn: fetchPlants,
  });

  const createMutation = useMutation({
    mutationFn: createPlant,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["plants"] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: PlantFormValues }) =>
      updatePlant(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["plants"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: deletePlant,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["plants"] }),
  });

  const handleSubmit = async (data: PlantFormValues) => {
    if (editingPlant) {
      await updateMutation.mutateAsync({ id: editingPlant.id, data });
    } else {
      await createMutation.mutateAsync(data);
    }
  };

  const openCreate = () => {
    setEditingPlant(undefined);
    setDialogOpen(true);
  };

  const openEdit = (plant: Plant) => {
    setEditingPlant(plant);
    setDialogOpen(true);
  };

  const handleDelete = async (plant: Plant) => {
    if (!confirm(`确定删除「${plant.name}」及其所有换盆记录？`)) return;
    await deleteMutation.mutateAsync(plant.id);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">家庭盆栽</h1>
          <p className="text-sm text-muted-foreground">换盆历史记录</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/overview">
              <BarChart3 className="h-4 w-4" />
              养护概览
            </Link>
          </Button>
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" />
            添加植物
          </Button>
        </div>
      </header>

      {isLoading && (
        <p className="text-center text-muted-foreground py-12">加载中…</p>
      )}

      {error && (
        <p className="text-center text-destructive py-12">
          加载失败：{error.message}
        </p>
      )}

      {plants && plants.length === 0 && (
        <p className="text-center text-muted-foreground py-12">
          暂无植物，点击上方按钮添加
        </p>
      )}

      {plants && plants.length > 0 && (
        <div className="grid gap-4">
          {plants.map((plant) => (
            <Card key={plant.id} className="transition-shadow hover:shadow-md">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <Link to={`/plants/${plant.id}`} className="group">
                    <CardTitle className="group-hover:text-primary transition-colors">
                      <Leaf className="inline h-5 w-5 mr-2 text-primary" />
                      {plant.name}
                    </CardTitle>
                    {plant.variety && (
                      <CardDescription className="mt-1">
                        品种：{plant.variety}
                      </CardDescription>
                    )}
                  </Link>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEdit(plant)}
                      aria-label="编辑"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(plant)}
                      aria-label="删除"
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    购入：{plant.purchase_date}
                  </span>
                  <span>换盆 {plant.repotting_count ?? 0} 次</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <PlantFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        plant={editingPlant}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
