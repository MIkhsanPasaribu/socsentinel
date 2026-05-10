import { useState, useRef, useEffect } from "react";
import { ChevronDown, Layout, Zap, ShieldCheck, Cpu, Loader2 } from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import { cn } from "../../../shared/lib/utils";

interface SoarExportButtonProps {
  investigationId: string;
  onExportSuccess: (platform: string, data: string) => void;
}

export function SoarExportButton({ investigationId, onExportSuccess }: SoarExportButtonProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleExport = async (platformId: string, platformLabel: string) => {
    setDropdownOpen(false);
    setLoading(true);
    try {
      const res = await apiClient.post(`/soar/export/${investigationId}?platform=${platformId}`);
      const payload = res.data.data?.export_payload;
      onExportSuccess(platformLabel, JSON.stringify(payload, null, 2));
    } catch (err) {
      console.error("SOAR Export failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={(e) => { e.stopPropagation(); setDropdownOpen(!dropdownOpen); }}
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
          <button
            onClick={(e) => { e.stopPropagation(); handleExport("splunk", "Splunk SOAR"); }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-gray-300 transition-all hover:bg-white/10 hover:text-white"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-white/5 text-green-400">
              <Zap size={14} />
            </div>
            <div className="flex flex-col items-start">
              <span className="font-medium">Splunk SOAR</span>
              <span className="text-[9px] text-gray-500">JSON Blueprint</span>
            </div>
          </button>
          
          <button
            onClick={(e) => { e.stopPropagation(); handleExport("xsoar", "Cortex XSOAR"); }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-gray-300 transition-all hover:bg-white/10 hover:text-white"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-white/5 text-orange-400">
              <ShieldCheck size={14} />
            </div>
            <div className="flex flex-col items-start">
              <span className="font-medium">Cortex XSOAR</span>
              <span className="text-[9px] text-gray-500">JSON Blueprint</span>
            </div>
          </button>

          <button
            onClick={(e) => { e.stopPropagation(); handleExport("sentinel", "Microsoft Sentinel"); }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-gray-300 transition-all hover:bg-white/10 hover:text-white"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-white/5 text-cyan-400">
              <Cpu size={14} />
            </div>
            <div className="flex flex-col items-start">
              <span className="font-medium">Microsoft Sentinel</span>
              <span className="text-[9px] text-gray-500">JSON Blueprint</span>
            </div>
          </button>
        </div>
      )}
    </div>
  );
}


