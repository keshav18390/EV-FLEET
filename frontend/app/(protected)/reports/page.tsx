"use client";

import { FileSpreadsheet, FileText, Download } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card } from "@/components/ui";
import { api } from "@/lib/api";

async function downloadFile(url: string, filename: string) {
  const resp = await api.get(url, { responseType: "blob" });
  const blobUrl = window.URL.createObjectURL(new Blob([resp.data]));
  const a = document.createElement("a");
  a.href = blobUrl;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(blobUrl);
}

export default function ReportsPage() {
  return (
    <>
      <Topbar title="Reports" />
      <main className="p-4 lg:p-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
          <Card className="p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center mb-4">
              <FileSpreadsheet className="text-emerald-600 dark:text-emerald-400" size={20} />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-white mb-1">Vehicles CSV Export</h3>
            <p className="text-sm text-slate-500 mb-4">Full vehicle fleet data including battery and health metrics.</p>
            <button
              onClick={() => downloadFile("/api/reports/vehicles/csv", "vehicles_report.csv")}
              className="flex items-center gap-2 text-sm font-medium text-brand-700 dark:text-brand-400 hover:underline"
            >
              <Download size={15} /> Download CSV
            </button>
          </Card>

          <Card className="p-6">
            <div className="w-11 h-11 rounded-xl bg-sky-50 dark:bg-sky-950 flex items-center justify-center mb-4">
              <FileText className="text-sky-600 dark:text-sky-400" size={20} />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-white mb-1">Fleet Summary PDF</h3>
            <p className="text-sm text-slate-500 mb-4">Executive summary with key fleet-wide KPIs, ready to share.</p>
            <button
              onClick={() => downloadFile("/api/reports/fleet-summary/pdf", "fleet_summary_report.pdf")}
              className="flex items-center gap-2 text-sm font-medium text-brand-700 dark:text-brand-400 hover:underline"
            >
              <Download size={15} /> Download PDF
            </button>
          </Card>
        </div>
      </main>
    </>
  );
}
