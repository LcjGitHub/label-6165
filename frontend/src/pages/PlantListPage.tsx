import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus, Leaf, Calendar, Pencil, Trash2, BarChart3, MapPin, AlertTriangle } from "lucide-react";
import { fetchPlants, createPlant, updatePlant, deletePlant } from "@/api/plants";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PlantFormDialog } from "@/components/PlantFormDialog";
import { LOCATION_OPTIONS } from "@/lib/schemas";
import type { Plant } from "@/types";
import type { PlantFormValues } from "@/lib/schemas";

/**
 * 植物列表页：展示所有盆栽及换盆次数，支持 CRUD。
 */
export function PlantListPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPlant, setEditingPlant] = useState<Plant | undefined>();
  const [locationFilter, setLocationFilter] = useState<string>("");

  const { data: plants, isLoading, error } = useQuery({
    queryKey: ["plants", locationFilter],
    queryFn: () => fetchPlants(locationFilter || undefined),
  });

  const invalidatePlantsAndOverview = () => {
    queryClient.invalidateQueries({ queryKey: ["plants"] });
    queryClient.invalidateQueries({ queryKey: ["overview"] });
  };

  const createMutation = useMutation({
    mutationFn: createPlant,
    onSuccess: invalidatePlantsAndOverview,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: PlantFormValues }) =>
      updatePlant(id, data),
    onSuccess: invalidatePlantsAndOverview,
  });

  const deleteMutation = useMutation({
    mutationFn: deletePlant,
    onSuccess: invalidatePlantsAndOverview,
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
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <Select
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="w-32"
            >
              <option value="">全部位置</option>
              {LOCATION_OPTIONS.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </Select>
          </div>
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
          网络连接失败，请确认后端服务已启动
        </p>
      )}

      {plants && plants.length === 0 && !locationFilter && (
        <p className="text-center text-muted-foreground py-12">
          暂无植物，点击上方按钮添加
        </p>
      )}

      {plants && plants.length === 0 && locationFilter && (
        <p className="text-center text-muted-foreground py-12">
          当前位置暂无植物
        </p>
      )}

      {plants && plants.length > 0 && (
        <div className="grid gap-4">
          {plants.map((plant) => (
            <Card
              key={plant.id}
              className={`transition-shadow hover:shadow-md ${
                plant.is_overdue
                  ? "border-destructive border-2"
                  : ""
              }`}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <Link to={`/plants/${plant.id}`} className="group flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <CardTitle className="group-hover:text-primary transition-colors">
                        <Leaf className="inline h-5 w-5 mr-2 text-primary" />
                        {plant.name}
                      </CardTitle>
                      {plant.is_overdue && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-destructive text-destructive-foreground">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          换盆超期
                        </span>
                      )}
                    </div>
                    {plant.variety && (
                      <CardDescription className="mt-1">
                        品种：{plant.variety}
                      </CardDescription>
                    )}
                    {plant.location && (
                      <span className="inline-flex items-center mt-2 px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                        <MapPin className="h-3 w-3 mr-1" />
                        {plant.location}
                      </span>
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
                <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    购入：{plant.purchase_date}
                  </span>
                  <span>换盆 {plant.repotting_count ?? 0} 次</span>
                  {plant.next_repotting_date && (
                    <span
                      className={`flex items-center gap-1 ${
                        plant.is_overdue ? "text-destructive font-medium" : ""
                      }`}
                    >
                      下次换盆：{plant.next_repotting_date}
                    </span>
                  )}
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
