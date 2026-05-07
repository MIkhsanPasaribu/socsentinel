/** SOCsentinel — Sidebar navigation component. */

import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Bell,
  Search,
  FileText,
  ClipboardList,
  Shield,
  Activity,
  Crosshair,
} from "lucide-react";
import { cn } from "../../lib/utils";
import { useInvestigationList } from "../../hooks/useInvestigations";

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  badge?: number;
}

const navItems: NavItem[] = [
  { label: "Dashboard", path: "/", icon: <LayoutDashboard size={20} /> },
  { label: "Alerts", path: "/alerts", icon: <Bell size={20} /> },
  { label: "Investigation", path: "/investigation", icon: <Search size={20} /> },
  { label: "Reports", path: "/reports", icon: <FileText size={20} /> },
  { label: "Threat Hunting", path: "/threat-hunting", icon: <Crosshair size={20} /> },
  { label: "Audit Trail", path: "/audit", icon: <ClipboardList size={20} /> },
];

export function Sidebar() {
  const { data: investigations } = useInvestigationList();
  
  const completedCount = investigations?.filter(i => i.status === "completed").length || 0;
  const activeCount = investigations?.filter(i => i.status !== "completed").length || 0;

  const getBadge = (path: string) => {
    if (path === "/investigation") return activeCount > 0 ? activeCount : undefined;
    if (path === "/reports") return completedCount > 0 ? completedCount : undefined;
    return undefined;
  };

  return (
    <aside
      id="sidebar-nav"
      className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-white/10 bg-navy-900/95 backdrop-blur-xl"
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-white/10 px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600">
          <Shield size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">
            SOC<span className="text-cyan-400">sentinel</span>
          </h1>
          <p className="text-[10px] font-medium uppercase tracking-widest text-gray-500">
            Multi-Agent SOC
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-cyan-500/10 text-cyan-400 glow-cyan"
                  : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
              )
            }
          >
            {item.icon}
            <span>{item.label}</span>
            {getBadge(item.path) !== undefined && (
              <span className={cn(
                "ml-auto flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-semibold",
                item.path === "/investigation" 
                  ? "bg-cyan-500/20 text-cyan-400 animate-pulse" 
                  : "bg-emerald-500/20 text-emerald-400"
              )}>
                {getBadge(item.path)}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Agent Status Footer */}
      <div className="border-t border-white/10 px-4 py-4">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Activity size={14} className="text-cyan-400" />
          <span>9 Agents Online</span>
          <span className="agent-active ml-auto" />
        </div>
      </div>
    </aside>
  );
}
