import type {
  Plant,
  PlantDetail,
  PlantInput,
  Repotting,
  RepottingInput,
} from "@/types";

const API_BASE = "http://localhost:7000/api";

/**
 * 统一请求封装，解析 JSON 并处理错误。
 */
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message =
      body.errors?.join("、") || body.error || `请求失败 (${res.status})`;
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

/** 获取植物列表 */
export function fetchPlants(): Promise<Plant[]> {
  return request(`${API_BASE}/plants`);
}

/** 获取植物详情（含换盆时间线） */
export function fetchPlant(id: number): Promise<PlantDetail> {
  return request(`${API_BASE}/plants/${id}`);
}

/** 创建植物 */
export function createPlant(data: PlantInput): Promise<Plant> {
  return request(`${API_BASE}/plants`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** 更新植物 */
export function updatePlant(id: number, data: PlantInput): Promise<Plant> {
  return request(`${API_BASE}/plants/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/** 删除植物 */
export function deletePlant(id: number): Promise<{ ok: boolean }> {
  return request(`${API_BASE}/plants/${id}`, { method: "DELETE" });
}

/** 添加换盆记录 */
export function createRepotting(
  plantId: number,
  data: RepottingInput
): Promise<Repotting> {
  return request(`${API_BASE}/plants/${plantId}/repotting`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** 更新换盆记录 */
export function updateRepotting(
  plantId: number,
  repotId: number,
  data: RepottingInput
): Promise<Repotting> {
  return request(`${API_BASE}/plants/${plantId}/repotting/${repotId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/** 删除换盆记录 */
export function deleteRepotting(
  plantId: number,
  repotId: number
): Promise<{ ok: boolean }> {
  return request(`${API_BASE}/plants/${plantId}/repotting/${repotId}`, {
    method: "DELETE",
  });
}
