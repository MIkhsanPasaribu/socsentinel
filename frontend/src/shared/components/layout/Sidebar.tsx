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
} from "lucide-react";
import { cn } from "../../lib/utils";

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
  { label: "Audit Trail", path: "/audit", icon: <ClipboardList size={20} /> },
];

export function Sidebar() {
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
            {item.badge !== undefined && item.badge > 0 && (
              <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-alert-orange/20 px-1.5 text-xs font-semibold text-alert-orange">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Agent Status Footer */}
      <div className="border-t border-white/10 px-4 py-4">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Activity size={14} className="text-cyan-400" />
          <span>5 Agents Online</span>
          <span className="agent-active ml-auto" />
        </div>
      </div>
    </aside>
  );
}
