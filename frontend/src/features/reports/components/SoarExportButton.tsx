/** SOCsentinel — SOAR Export Button with platform dropdown and JSON preview.
 *
 * Provides one-click export to Splunk SOAR, Cortex XSOAR, or Microsoft Sentinel.
 * Calls the existing /api/v1/soar/export/{investigation_id} endpoint.
 */

import { useState, useRef, useEffect } from "react";
import {
  Share2,
  ChevronDown,
  Download,
  X,
  Copy,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse } from "../../../shared/types";

interface SoarExportButtonProps {
  investigationId: string;
}

interface SoarPlatform {
  id: string;
  label: string;
  color: string;
  bgColor: string;
}

const SOAR_PLATFORMS: SoarPlatform[] = [
  {
    id: "splunk",
    label: "Splunk SOAR",
    color: "text-green-400",
    bgColor: "bg-green-500/10",
  },
  {
    id: "xsoar",
    label: "Cortex XSOAR",
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
  },
  {
    id: "sentinel",
    label: "Microsoft Sentinel",
    color: "text-cyan-400",
    bgColor: "bg-cyan-500/10",
  },
];

export function SoarExportButton({ investigationId }: SoarExportButtonProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewData, setPreviewData] = useState<string>("");
  const [previewPlatform, setPreviewPlatform] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleExport = async (platform: SoarPlatform) => {
    setDropdownOpen(false);
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post<APIResponse>(
        `/soar/export/${investigationId}?platform=${platform.id}`,
      );
      const exportPayload = (res.data.data as Record<string, unknown>)
        ?.export_payload;
      const formatted = JSON.stringify(exportPayload, null, 2);
      setPreviewData(formatted);
      setPreviewPlatform(platform.label);
      setPreviewOpen(true);
    } catch {
      setError("Export failed. Investigation may have expired.");
      setTimeout(() => setError(null), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([previewData], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `soar_export_${previewPlatform.replace(/\s+/g, "_").toLowerCase()}_${investigationId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(previewData);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      {/* Dropdown trigger */}
      <div ref={dropdownRef} className="relative">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setDropdownOpen(!dropdownOpen);
          }}
          disabled={loading}
          className="flex items-center gap-1 rounded-lg bg-purple-500/10 px-2 py-1 text-[11px] font-medium text-purple-400 transition-colors hover:bg-purple-500/20 hover:text-purple-300 disabled:opacity-50 sm:px-2.5 sm:py-1.5 sm:text-xs"
          title="Export to SOAR platform"
        >
          {loading ? (
            <Loader2 size={12} className="animate-spin sm:h-3.5 sm:w-3.5" />
          ) : (
            <Share2 size={12} className="sm:h-3.5 sm:w-3.5" />
          )}
          <span className="hidden sm:inline">SOAR</span>
          <ChevronDown size={10} />
        </button>

        {/* Dropdown menu */}
        {dropdownOpen && (
          <div className="absolute right-0 top-full z-50 mt-1 w-48 rounded-lg border border-white/10 bg-[#0d1b2a] p-1 shadow-xl backdrop-blur-md">
            {SOAR_PLATFORMS.map((platform) => (
              <button
                key={platform.id}
                onClick={(e) => {
                  e.stopPropagation();
                  handleExport(platform);
                }}
                className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-gray-300 transition-colors hover:bg-white/10 hover:text-white"
              >
                <div
                  className={`h-2 w-2 rounded-full ${platform.bgColor} ring-1 ring-white/10`}
                />
                {platform.label}
              </button>
            ))}
          </div>
        )}

        {error && (
          <div className="absolute right-0 top-full z-50 mt-1 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-[11px] text-red-400 shadow-lg backdrop-blur-sm whitespace-nowrap">
            {error}
          </div>
        )}
      </div>

      {/* JSON Preview Modal */}
      {previewOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setPreviewOpen(false)}
        >
          <div
            className="mx-4 w-full max-w-2xl rounded-xl border border-white/10 bg-[#0a1628] shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-3">
              <div className="flex items-center gap-2">
                <Share2 size={16} className="text-purple-400" />
                <h3 className="text-sm font-semibold text-white">
                  {previewPlatform} Export
                </h3>
                <span className="rounded bg-purple-500/20 px-1.5 py-0.5 text-[10px] font-medium text-purple-400">
                  JSON
                </span>
              </div>
              <button
                onClick={() => setPreviewOpen(false)}
                className="rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>

            {/* JSON preview */}
            <div className="max-h-96 overflow-auto p-5">
              <pre className="whitespace-pre-wrap break-words font-mono text-xs leading-relaxed text-gray-300">
                {previewData}
              </pre>
            </div>

            {/* Modal footer */}
            <div className="flex items-center justify-end gap-2 border-t border-white/10 px-5 py-3">
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:bg-white/10 hover:text-white"
              >
                {copied ? (
                  <CheckCircle2 size={14} className="text-green-400" />
                ) : (
                  <Copy size={14} />
                )}
                {copied ? "Copied!" : "Copy JSON"}
              </button>
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 rounded-lg bg-purple-500/20 px-3 py-1.5 text-xs font-medium text-purple-400 transition-colors hover:bg-purple-500/30 hover:text-purple-300"
              >
                <Download size={14} />
                Download .json
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
