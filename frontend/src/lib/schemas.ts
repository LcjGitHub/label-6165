import { z } from "zod";

/** 植物表单校验 schema */
export const plantSchema = z.object({
  name: z.string().min(1, "名称不能为空"),
  variety: z.string(),
  purchase_date: z.string().min(1, "购入日期不能为空"),
});

/** 换盆记录表单校验 schema */
export const repottingSchema = z.object({
  date: z.string().min(1, "换盆日期不能为空"),
  notes: z.string(),
});

export type PlantFormValues = z.infer<typeof plantSchema>;
export type RepottingFormValues = z.infer<typeof repottingSchema>;
