import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PlantListPage } from "@/pages/PlantListPage";
import { PlantDetailPage } from "@/pages/PlantDetailPage";
import { OverviewPage } from "@/pages/OverviewPage";

/**
 * 应用路由配置。
 */
export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PlantListPage />} />
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/plants/:id" element={<PlantDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
