/** SOCsentinel — Top navigation bar component. */

import { Menu, User, Zap } from "lucide-react";

interface NavbarProps {
  /** Callback to toggle the mobile sidebar. */
  onMenuToggle: () => void;
}

export function Navbar({ onMenuToggle }: NavbarProps) {
  return (
    <header
      id="top-navbar"
      className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-white/10 bg-navy-900/80 px-3 backdrop-blur-xl sm:h-16 sm:px-6"
    >
      {/* Left — Hamburger + badge */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Hamburger — mobile only */}
        <button
          onClick={onMenuToggle}
          className="rounded-lg p-2 text-gray-400 hover:bg-white/10 hover:text-white md:hidden"
          aria-label="Toggle sidebar"
        >
          <Menu size={22} />
        </button>

        <div className="hidden items-center gap-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-2.5 py-1 sm:flex sm:px-3 sm:py-1.5">
          <Zap size={14} className="text-cyan-400" />
          <span className="text-[11px] font-medium text-cyan-400 sm:text-xs">
            AMD MI300X · ROCm
          </span>
        </div>
      </div>

      {/* Right — Actions */}
      <div className="flex items-center gap-1 sm:gap-2">
        {/* User avatar */}
        <button
          id="btn-user-menu"
          className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-gray-400 transition-colors hover:bg-white/5 hover:text-white sm:gap-2 sm:px-3"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 sm:h-8 sm:w-8">
            <User size={14} className="text-white sm:h-4 sm:w-4" />
          </div>
          <span className="hidden text-sm font-medium sm:inline">Analyst</span>
        </button>
      </div>
    </header>
  );
}
