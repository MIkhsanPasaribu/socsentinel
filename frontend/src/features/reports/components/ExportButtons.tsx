/** SOCsentinel — Reports feature — Export Buttons component. */

import { useState } from "react";
import { FileDown, FileText, Loader2 } from "lucide-react";
import { apiClient } from "../../../shared/lib/api";

interface ExportButtonsProps {
  investigationId: string;
}

/**
 * Export buttons for downloading investigation reports.
 * Provides PDF and DOCX export functionality.
 */
export function ExportButtons({ investigationId }: ExportButtonsProps) {
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingDocx, setLoadingDocx] = useState(false);

  /**
   * Handle export download.
   * Fetches the document from the API and triggers a browser download.
   */
  const handleExport = async (format: "pdf" | "docx") => {
    const setLoading = format === "pdf" ? setLoadingPdf : setLoadingDocx;
    setLoading(true);

    try {
      const response = await apiClient.get(
        `/report-export/export/${investigationId}/${format}`,
        { responseType: "blob" }
      );

      // Create blob URL and trigger download
      const blob = new Blob([response.data], {
        type: format === "pdf"
          ? "application/pdf"
          : "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      });
      const url = URL.createObjectURL(blob);

      // Create temporary link element
      const link = document.createElement("a");
      link.href = url;
      link.download = `SOCsentinel_Report_${investigationId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Failed to export ${format}:`, error);
      // Could add toast notification here
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex items-center gap-1.5"
      onClick={(e) => e.stopPropagation()}
    >
      {/* PDF Export Button */}
      <button
        onClick={() => handleExport("pdf")}
        disabled={loadingPdf}
        className="flex items-center gap-1 rounded-lg bg-red-500/10 px-2.5 py-1.5 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/20 hover:text-red-300 disabled:cursor-not-allowed disabled:opacity-50"
        title="Export as PDF"
      >
        {loadingPdf ? (
          <Loader2 size={14} className="animate-spin" />
        ) : (
          <FileDown size={14} />
        )}
        PDF
      </button>

      {/* DOCX Export Button */}
      <button
        onClick={() => handleExport("docx")}
        disabled={loadingDocx}
        className="flex items-center gap-1 rounded-lg bg-blue-500/10 px-2.5 py-1.5 text-xs font-medium text-blue-400 transition-colors hover:bg-blue-500/20 hover:text-blue-300 disabled:cursor-not-allowed disabled:opacity-50"
        title="Export as Word Document"
      >
        {loadingDocx ? (
          <Loader2 size={14} className="animate-spin" />
        ) : (
          <FileText size={14} />
        )}
        DOCX
      </button>
    </div>
  );
}
