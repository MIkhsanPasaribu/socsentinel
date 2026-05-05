/* eslint-disable react-refresh/only-export-components */
/** SOCsentinel — Toast Notification System. */

import { useState, useEffect, createContext, useContext, useCallback } from "react";
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from "lucide-react";
import { cn } from "../lib/utils";

export type ToastType = "success" | "error" | "warning" | "info";

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  addToast: (toast: Omit<ToastMessage, "id">) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback((toast: Omit<ToastMessage, "id">) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = { ...toast, id, duration: toast.duration || 3000 };
    setToasts((prev) => [...prev, newToast]);

    setTimeout(() => {
      removeToast(id);
    }, newToast.duration);
  }, [removeToast]);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-96 flex-col gap-2">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: ToastMessage; onDismiss: () => void }) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
    }, (toast.duration || 3000) - 300); // Start exit animation before unmount

    return () => clearTimeout(timer);
  }, [toast.duration]);

  const icons = {
    success: <CheckCircle2 className="text-green-400" size={18} />,
    error: <XCircle className="text-red-400" size={18} />,
    warning: <AlertTriangle className="text-orange-400" size={18} />,
    info: <Info className="text-blue-400" size={18} />,
  };

  const colors = {
    success: "border-green-500/20 bg-green-500/10",
    error: "border-red-500/20 bg-red-500/10",
    warning: "border-orange-500/20 bg-orange-500/10",
    info: "border-blue-500/20 bg-blue-500/10",
  };

  return (
    <div
      className={cn(
        "pointer-events-auto flex w-full items-start gap-3 rounded-lg border p-4 shadow-lg backdrop-blur-md transition-all duration-300",
        colors[toast.type],
        isExiting ? "translate-y-2 opacity-0" : "animate-slide-up"
      )}
    >
      <div className="shrink-0 mt-0.5">{icons[toast.type]}</div>
      <div className="flex-1">
        <h4 className="text-sm font-medium text-white">{toast.title}</h4>
        {toast.message && (
          <p className="mt-1 text-xs text-gray-300">{toast.message}</p>
        )}
      </div>
      <button
        onClick={() => {
          setIsExiting(true);
          setTimeout(onDismiss, 300);
        }}
        className="shrink-0 rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white"
      >
        <X size={14} />
      </button>
    </div>
  );
}
