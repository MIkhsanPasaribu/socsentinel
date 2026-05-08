/** SOCsentinel — Reports feature — Export Buttons component. */

import { useState } from "react";
import { FileDown, FileText, Loader2, AlertCircle } from "lucide-react";
import { apiClient } from "../../../shared/lib/api";

interface ExportButtonsProps {
  investigationId: string;
}

/**
 * Export buttons for downloading investigation reports.
 * Provides PDF and DOCX export functionality with error feedback.
 */
export function ExportButtons({ investigationId }: ExportButtonsProps) {
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingDocx, setLoadingDocx] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle export download.
   * Fetches the document from the API and triggers a browser download.
   */
  const handleExport = async (format: "pdf" | "docx") => {
    const setLoading = format === "pdf" ? setLoadingPdf : setLoadingDocx;
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(
        `/report-export/export/${investigationId}/${format}`,
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], {
        type:
          format === "pdf"
            ? "application/pdf"
            : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const url = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = `SOCsentinel_Report_${investigationId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      let msg = `${format.toUpperCase()} export failed`;
      if (err && typeof err === "object" && "response" in err) {
        const resp = (err as { response?: { status?: number } }).response;
        if (resp?.status === 404) {
          msg = "Investigation data expired. Run a new investigation first.";
        } else if (resp?.status === 503) {
          msg = "PDF export unavailable (Linux/Docker only)";
        }
      }
      setError(msg);
      setTimeout(() => setError(null), 4000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex flex-wrap items-center gap-1.5"
      onClick={(e) => e.stopPropagation()}
    >
      {/* PDF Export Button */}
      <button
        onClick={() => handleExport("pdf")}
        disabled={loadingPdf}
        className="flex items-center gap-1 rounded-lg bg-red-500/10 px-2 py-1 text-[11px] font-medium text-red-400 transition-colors hover:bg-red-500/20 hover:text-red-300 disabled:cursor-not-allowed disabled:opacity-50 sm:px-2.5 sm:py-1.5 sm:text-xs"
        title="Export as PDF"
      >
        {loadingPdf ? (
          <Loader2 size={12} className="animate-spin sm:h-3.5 sm:w-3.5" />
        ) : (
          <FileDown size={12} className="sm:h-3.5 sm:w-3.5" />
        )}
        <span className="hidden sm:inline">PDF</span>
      </button>

      {/* DOCX Export Button */}
      <button
        onClick={() => handleExport("docx")}
        disabled={loadingDocx}
        className="flex items-center gap-1 rounded-lg bg-blue-500/10 px-2 py-1 text-[11px] font-medium text-blue-400 transition-colors hover:bg-blue-500/20 hover:text-blue-300 disabled:cursor-not-allowed disabled:opacity-50 sm:px-2.5 sm:py-1.5 sm:text-xs"
        title="Export as Word Document"
      >
        {loadingDocx ? (
          <Loader2 size={12} className="animate-spin sm:h-3.5 sm:w-3.5" />
        ) : (
          <FileText size={12} className="sm:h-3.5 sm:w-3.5" />
        )}
        <span className="hidden sm:inline">DOCX</span>
      </button>

      {/* Error tooltip */}
      {error && (
        <div className="absolute right-0 top-full z-50 mt-1 flex items-center gap-1.5 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-[11px] text-red-400 shadow-lg backdrop-blur-sm">
          <AlertCircle size={12} />
          {error}
        </div>
      )}
    </div>
  );
}
