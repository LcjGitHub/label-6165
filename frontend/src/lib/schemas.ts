import { z } from "zod";

export const LOCATION_OPTIONS = ["客厅", "阳台", "卧室", "书房", "其他"];

/** 植物表单校验 schema */
export const plantSchema = z.object({
  name: z.string().min(1, "名称不能为空"),
  variety: z.string(),
  purchase_date: z.string().min(1, "购入日期不能为空"),
  location: z
    .string()
    .refine((val) => LOCATION_OPTIONS.includes(val), {
      message: "请选择位置",
    }),
});

/** 换盆记录表单校验 schema */
export const repottingSchema = z.object({
  date: z.string().min(1, "换盆日期不能为空"),
  notes: z.string(),
});

/** 浇水记录表单校验 schema */
export const wateringSchema = z.object({
  date: z.string().min(1, "浇水日期不能为空"),
  notes: z.string(),
});

export type PlantFormValues = z.infer<typeof plantSchema>;
export type RepottingFormValues = z.infer<typeof repottingSchema>;
export type WateringFormValues = z.infer<typeof wateringSchema>;
