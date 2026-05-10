import { useState, useRef, useEffect } from "react";
import {
  Share2,
  ChevronDown,
  Download,
  X,
  Copy,
  CheckCircle2,
  Loader2,
  Zap,
  ShieldCheck,
  Cpu,
  Layout,
} from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse } from "../../../shared/types";
import { cn } from "../../../shared/lib/utils";

interface SoarExportButtonProps {
  investigationId: string;
}

interface SoarPlatform {
  id: string;
  label: string;
  color: string;
  bgColor: string;
  icon: React.ReactNode;
}

const SOAR_PLATFORMS: SoarPlatform[] = [
  {
    id: "splunk",
    label: "Splunk SOAR",
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    icon: <Zap size={14} />,
  },
  {
    id: "xsoar",
    label: "Cortex XSOAR",
    color: "text-orange-400",
    bgColor: "bg-orange-500/10",
    icon: <ShieldCheck size={14} />,
  },
  {
    id: "sentinel",
    label: "Microsoft Sentinel",
    color: "text-cyan-400",
    bgColor: "bg-cyan-500/10",
    icon: <Cpu size={14} />,
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
      setError("Export failed. Investigation data may have expired.");
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
          className="group flex items-center gap-1.5 rounded-lg bg-purple-500/10 px-2 py-1 text-[11px] font-semibold text-purple-400 transition-all hover:bg-purple-500/20 hover:text-purple-300 disabled:opacity-50 sm:px-3 sm:py-1.5 sm:text-xs"
          title="Export to SOAR automation platforms"
        >
          {loading ? (
            <Loader2 size={12} className="animate-spin sm:h-3.5 sm:w-3.5" />
          ) : (
            <Layout size={12} className="sm:h-3.5 sm:w-3.5" />
          )}
          <span className="hidden sm:inline">SOAR</span>
          <ChevronDown 
            size={10} 
            className={cn("transition-transform duration-200", dropdownOpen && "rotate-180")} 
          />
        </button>

        {/* Dropdown menu */}
        {dropdownOpen && (
          <div className="absolute right-0 top-full z-50 mt-1.5 w-52 overflow-hidden rounded-xl border border-white/10 bg-[#0d1b2a]/95 p-1 shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-100">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-gray-500">
              Select Platform
            </div>
            {SOAR_PLATFORMS.map((platform) => (
              <button
                key={platform.id}
                onClick={(e) => {
                  e.stopPropagation();
                  handleExport(platform);
                }}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-gray-300 transition-all hover:bg-white/10 hover:text-white"
              >
                <div className={cn("flex h-6 w-6 items-center justify-center rounded-md bg-white/5", platform.color)}>
                  {platform.icon}
                </div>
                <div className="flex flex-col items-start">
                  <span className="font-medium">{platform.label}</span>
                  <span className="text-[9px] text-gray-500">JSON Blueprint</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {error && (
          <div className="absolute right-0 top-full z-50 mt-1.5 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-[11px] text-red-400 shadow-lg backdrop-blur-sm whitespace-nowrap">
            <CheckCircle2 size={12} className="rotate-180" />
            {error}
          </div>
        )}
      </div>

      {/* JSON Preview Modal */}
      {previewOpen && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-md transition-all animate-in fade-in duration-300"
          onClick={() => setPreviewOpen(false)}
        >
          <div
            className="mx-4 w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-[#0a1628] shadow-[0_0_50px_rgba(168,85,247,0.15)] transition-all animate-in zoom-in-95 duration-300"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="relative flex items-center justify-between border-b border-white/10 bg-gradient-to-r from-purple-500/5 to-transparent px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/20 text-purple-400 shadow-lg shadow-purple-500/10">
                  <Share2 size={20} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    {previewPlatform}
                  </h3>
                  <p className="text-xs text-gray-400">SOCsentinel Automation Export</p>
                </div>
                <span className="ml-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-2 py-0.5 text-[10px] font-bold text-purple-400 glow-purple">
                  JSON
                </span>
              </div>
              <button
                onClick={() => setPreviewOpen(false)}
                className="group rounded-full p-2 text-gray-400 transition-all hover:bg-white/10 hover:text-white"
              >
                <X size={20} className="transition-transform group-hover:rotate-90" />
              </button>
            </div>

            {/* JSON preview */}
            <div className="relative bg-[#020617]/50 p-6">
              <div className="absolute right-4 top-4 flex gap-2">
                <span className="flex h-3 w-3 rounded-full bg-red-500/20" />
                <span className="flex h-3 w-3 rounded-full bg-yellow-500/20" />
                <span className="flex h-3 w-3 rounded-full bg-green-500/20" />
              </div>
              <div className="max-h-[400px] overflow-auto custom-scrollbar">
                <pre className="whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-purple-200/80">
                  {previewData}
                </pre>
              </div>
            </div>

            {/* Modal footer */}
            <div className="flex items-center justify-between border-t border-white/10 bg-black/20 px-6 py-4">
              <p className="text-[10px] text-gray-500 italic">
                * Import this JSON directly into your SOAR playbook as a structured incident artifact.
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold text-gray-300 transition-all hover:bg-white/10 hover:text-white active:scale-95"
                >
                  {copied ? (
                    <CheckCircle2 size={16} className="text-green-400" />
                  ) : (
                    <Copy size={16} />
                  )}
                  {copied ? "Copied!" : "Copy Payload"}
                </button>
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-purple-500/20 transition-all hover:scale-[1.02] hover:shadow-purple-500/40 active:scale-95"
                >
                  <Download size={16} />
                  Download File
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

