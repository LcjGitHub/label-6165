import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Leaf, RefreshCw, Calendar, ArrowLeft } from "lucide-react";
import { fetchOverview } from "@/api/plants";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

/**
 * 养护概览统计页：展示植物总数、换盆总次数、最近换盆信息。
 */
export function OverviewPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["overview"],
    queryFn: fetchOverview,
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">养护概览</h1>
          <p className="text-sm text-muted-foreground">盆栽养护数据统计</p>
        </div>
        <Button variant="outline" asChild>
          <Link to="/">
            <ArrowLeft className="h-4 w-4" />
            返回列表
          </Link>
        </Button>
      </header>

      {isLoading && (
        <p className="text-center text-muted-foreground py-12">加载中…</p>
      )}

      {error && (
        <p className="text-center text-destructive py-12">
          加载失败：{error.message}
        </p>
      )}

      {stats && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="transition-shadow hover:shadow-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Leaf className="h-5 w-5 text-primary" />
                植物总数
              </CardTitle>
              <CardDescription>当前养护的盆栽数量</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-primary">
                {stats.plant_count}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {stats.plant_count === 0 ? "暂无植物" : `共 ${stats.plant_count} 盆`}
              </div>
            </CardContent>
          </Card>

          <Card className="transition-shadow hover:shadow-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <RefreshCw className="h-5 w-5 text-primary" />
                换盆总次数
              </CardTitle>
              <CardDescription>历史累计换盆记录</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-primary">
                {stats.total_repotting_count}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {stats.total_repotting_count === 0
                  ? "暂无换盆记录"
                  : `累计 ${stats.total_repotting_count} 次`}
              </div>
            </CardContent>
          </Card>

          <Card className="md:col-span-2 transition-shadow hover:shadow-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="h-5 w-5 text-primary" />
                最近换盆
              </CardTitle>
              <CardDescription>最新一次换盆记录</CardDescription>
            </CardHeader>
            <CardContent>
              {stats.last_repotting_date && stats.last_repotting_plant_name ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl font-bold text-primary">
                      {stats.last_repotting_date}
                    </span>
                    <span className="text-lg text-muted-foreground">
                      「{stats.last_repotting_plant_name}」
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {stats.last_repotting_plant_name} 最近一次换盆时间
                  </p>
                </div>
              ) : (
                <div className="text-muted-foreground">
                  暂无换盆记录
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
