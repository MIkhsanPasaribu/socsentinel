/** SOCsentinel — Top navigation bar component. */

import { Bell, Settings, User, Zap } from "lucide-react";

export function Navbar() {
  return (
    <header
      id="top-navbar"
      className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/10 bg-navy-900/80 px-6 backdrop-blur-xl"
    >
      {/* Left — Page context */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-3 py-1.5">
          <Zap size={14} className="text-cyan-400" />
          <span className="text-xs font-medium text-cyan-400">
            AMD MI300X · ROCm
          </span>
        </div>
      </div>

      {/* Right — Actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <button
          id="btn-notifications"
          className="relative rounded-lg p-2 text-gray-400 transition-colors hover:bg-white/5 hover:text-white"
          title="Notifications"
        >
          <Bell size={20} />
          <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-alert-orange text-[10px] font-bold text-white">
            3
          </span>
        </button>

        {/* Settings */}
        <button
          id="btn-settings"
          className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-white/5 hover:text-white"
          title="Settings"
        >
          <Settings size={20} />
        </button>

        {/* User avatar */}
        <button
          id="btn-user-menu"
          className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-gray-400 transition-colors hover:bg-white/5 hover:text-white"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-blue-600">
            <User size={16} className="text-white" />
          </div>
          <span className="text-sm font-medium">Analyst</span>
        </button>
      </div>
    </header>
  );
}
