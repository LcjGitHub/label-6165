import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Plus,
  Calendar,
  Pencil,
  Trash2,
  Sprout,
} from "lucide-react";
import {
  fetchPlant,
  updatePlant,
  deletePlant,
  createRepotting,
  updateRepotting,
  deleteRepotting,
  createWatering,
  updateWatering,
  deleteWatering,
} from "@/api/plants";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PlantFormDialog } from "@/components/PlantFormDialog";
import { RepottingFormDialog } from "@/components/RepottingFormDialog";
import { WateringFormDialog } from "@/components/WateringFormDialog";
import type { Repotting, Watering } from "@/types";
import type {
  PlantFormValues,
  RepottingFormValues,
  WateringFormValues,
} from "@/lib/schemas";

export function PlantDetailPage() {
  const { id } = useParams<{ id: string }>();
  const plantId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [plantDialogOpen, setPlantDialogOpen] = useState(false);
  const [repotDialogOpen, setRepotDialogOpen] = useState(false);
  const [editingRepot, setEditingRepot] = useState<Repotting | undefined>();
  const [waterDialogOpen, setWaterDialogOpen] = useState(false);
  const [editingWater, setEditingWater] = useState<Watering | undefined>();

  const { data: plant, isLoading, error } = useQuery({
    queryKey: ["plant", plantId],
    queryFn: () => fetchPlant(plantId),
    enabled: !Number.isNaN(plantId),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["plant", plantId] });
    queryClient.invalidateQueries({ queryKey: ["plants"] });
  };

  const updatePlantMutation = useMutation({
    mutationFn: (data: PlantFormValues) => updatePlant(plantId, data),
    onSuccess: invalidate,
  });

  const deletePlantMutation = useMutation({
    mutationFn: () => deletePlant(plantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      navigate("/");
    },
  });

  const createRepotMutation = useMutation({
    mutationFn: (data: RepottingFormValues) => createRepotting(plantId, data),
    onSuccess: invalidate,
  });

  const updateRepotMutation = useMutation({
    mutationFn: ({
      repotId,
      data,
    }: {
      repotId: number;
      data: RepottingFormValues;
    }) => updateRepotting(plantId, repotId, data),
    onSuccess: invalidate,
  });

  const deleteRepotMutation = useMutation({
    mutationFn: (repotId: number) => deleteRepotting(plantId, repotId),
    onSuccess: invalidate,
  });

  const createWaterMutation = useMutation({
    mutationFn: (data: WateringFormValues) => createWatering(plantId, data),
    onSuccess: invalidate,
  });

  const updateWaterMutation = useMutation({
    mutationFn: ({
      wateringId,
      data,
    }: {
      wateringId: number;
      data: WateringFormValues;
    }) => updateWatering(plantId, wateringId, data),
    onSuccess: invalidate,
  });

  const deleteWaterMutation = useMutation({
    mutationFn: (wateringId: number) => deleteWatering(plantId, wateringId),
    onSuccess: invalidate,
  });

  const handlePlantSubmit = async (data: PlantFormValues) => {
    await updatePlantMutation.mutateAsync(data);
  };

  const handleRepotSubmit = async (data: RepottingFormValues) => {
    if (editingRepot) {
      await updateRepotMutation.mutateAsync({
        repotId: editingRepot.id,
        data,
      });
    } else {
      await createRepotMutation.mutateAsync(data);
    }
  };

  const handleWaterSubmit = async (data: WateringFormValues) => {
    if (editingWater) {
      await updateWaterMutation.mutateAsync({
        wateringId: editingWater.id,
        data,
      });
    } else {
      await createWaterMutation.mutateAsync(data);
    }
  };

  const openCreateRepot = () => {
    setEditingRepot(undefined);
    setRepotDialogOpen(true);
  };

  const openEditRepot = (record: Repotting) => {
    setEditingRepot(record);
    setRepotDialogOpen(true);
  };

  const handleDeleteRepot = async (record: Repotting) => {
    if (!confirm(`确定删除 ${record.date} 的换盆记录？`)) return;
    await deleteRepotMutation.mutateAsync(record.id);
  };

  const openCreateWater = () => {
    setEditingWater(undefined);
    setWaterDialogOpen(true);
  };

  const openEditWater = (record: Watering) => {
    setEditingWater(record);
    setWaterDialogOpen(true);
  };

  const handleDeleteWater = async (record: Watering) => {
    if (!confirm(`确定删除 ${record.date} 的浇水记录？`)) return;
    await deleteWaterMutation.mutateAsync(record.id);
  };

  const handleDeletePlant = async () => {
    if (!plant || !confirm(`确定删除「${plant.name}」？`)) return;
    await deletePlantMutation.mutateAsync();
  };

  if (isLoading) {
    return (
      <p className="text-center text-muted-foreground py-12">加载中…</p>
    );
  }

  if (error || !plant) {
    return (
      <div className="mx-auto max-w-3xl p-6 text-center">
        <p className="text-destructive mb-4">
          {error?.message ?? "植物不存在"}
        </p>
        <Button variant="outline" asChild>
          <Link to="/">返回列表</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/" aria-label="返回">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold tracking-tight">{plant.name}</h1>
          {plant.variety && (
            <p className="text-sm text-muted-foreground">{plant.variety}</p>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={() => setPlantDialogOpen(true)}>
          <Pencil className="h-4 w-4" />
          编辑
        </Button>
        <Button variant="outline" size="sm" onClick={handleDeletePlant}>
          <Trash2 className="h-4 w-4 text-destructive" />
          删除
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Sprout className="h-4 w-4 text-primary" />
            基本信息
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-1">
          <p>
            <span className="text-muted-foreground">品种：</span>
            {plant.variety || "—"}
          </p>
          <p>
            <span className="text-muted-foreground">购入日期：</span>
            {plant.purchase_date}
          </p>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">换盆时间线</h2>
        <Button size="sm" onClick={openCreateRepot}>
          <Plus className="h-4 w-4" />
          添加换盆
        </Button>
      </div>

      {plant.repotting.length === 0 && (
        <p className="text-center text-muted-foreground py-8">
          暂无换盆记录
        </p>
      )}

      {plant.repotting.length > 0 && (
        <div className="relative space-y-0">
          {plant.repotting.map((record, index) => (
            <div key={record.id} className="relative flex gap-4 pb-6">
              {index < plant.repotting.length - 1 && (
                <div
                  className="absolute left-[11px] top-6 bottom-0 w-0.5 bg-border"
                  aria-hidden
                />
              )}
              <div
                className="mt-1 h-[22px] w-[22px] shrink-0 rounded-full border-2 border-primary bg-background flex items-center justify-center"
                aria-hidden
              >
                <div className="h-2 w-2 rounded-full bg-primary" />
              </div>
              <Card className="flex-1">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {record.date}
                      </CardTitle>
                      {record.notes && (
                        <CardDescription className="mt-2 text-foreground/80">
                          {record.notes}
                        </CardDescription>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openEditRepot(record)}
                        aria-label="编辑"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteRepot(record)}
                        aria-label="删除"
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">浇水记录</h2>
        <Button size="sm" onClick={openCreateWater}>
          <Plus className="h-4 w-4" />
          添加浇水
        </Button>
      </div>

      {plant.watering.length === 0 && (
        <p className="text-center text-muted-foreground py-8">
          暂无浇水记录
        </p>
      )}

      {plant.watering.length > 0 && (
        <div className="relative space-y-0">
          {plant.watering.map((record, index) => (
            <div key={record.id} className="relative flex gap-4 pb-6">
              {index < plant.watering.length - 1 && (
                <div
                  className="absolute left-[11px] top-6 bottom-0 w-0.5 bg-border"
                  aria-hidden
                />
              )}
              <div
                className="mt-1 h-[22px] w-[22px] shrink-0 rounded-full border-2 border-primary bg-background flex items-center justify-center"
                aria-hidden
              >
                <div className="h-2 w-2 rounded-full bg-primary" />
              </div>
              <Card className="flex-1">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {record.date}
                      </CardTitle>
                      {record.notes && (
                        <CardDescription className="mt-2 text-foreground/80">
                          {record.notes}
                        </CardDescription>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openEditWater(record)}
                        aria-label="编辑"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteWater(record)}
                        aria-label="删除"
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </div>
          ))}
        </div>
      )}

      <PlantFormDialog
        open={plantDialogOpen}
        onOpenChange={setPlantDialogOpen}
        plant={plant}
        onSubmit={handlePlantSubmit}
      />

      <RepottingFormDialog
        open={repotDialogOpen}
        onOpenChange={setRepotDialogOpen}
        record={editingRepot}
        onSubmit={handleRepotSubmit}
      />

      <WateringFormDialog
        open={waterDialogOpen}
        onOpenChange={setWaterDialogOpen}
        record={editingWater}
        onSubmit={handleWaterSubmit}
      />
    </div>
  );
}
