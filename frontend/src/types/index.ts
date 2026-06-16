/** API 类型定义 */

export interface OverviewStats {
  plant_count: number;
  total_repotting_count: number;
  last_repotting_date: string | null;
  last_repotting_plant_name: string | null;
}

export interface Plant {
  id: number;
  name: string;
  variety: string;
  purchase_date: string;
  created_at: string;
  repotting_count?: number;
}

export interface Repotting {
  id: number;
  plant_id: number;
  date: string;
  notes: string;
  created_at: string;
}

export interface Watering {
  id: number;
  plant_id: number;
  date: string;
  notes: string;
  created_at: string;
}

export interface PlantDetail extends Plant {
  repotting: Repotting[];
  watering: Watering[];
}

export interface PlantInput {
  name: string;
  variety: string;
  purchase_date: string;
}

export interface RepottingInput {
  date: string;
  notes: string;
}

export interface WateringInput {
  date: string;
  notes: string;
}
