import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Mail,
  Send,
  BarChart3,
  Globe,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react';

const sidebarItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/accounts', label: 'Email Accounts', icon: Mail },
  { path: '/campaigns', label: 'Campaigns', icon: Send },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/domains', label: 'DNS Manager', icon: Globe },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-slate-950 border-r border-slate-800 transform transition-transform duration-200 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-800">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">N</span>
            </div>
            <span className="text-white font-semibold text-lg">Nexus Engine</span>
          </Link>
          <button
            className="lg:hidden text-slate-400 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon size={18} />
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
          <Link
            to="/settings"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <Settings size={18} />
            <span className="text-sm font-medium">Settings</span>
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 bg-slate-950 border-b border-slate-800 flex items-center justify-between px-4 lg:px-6">
          <button
            className="lg:hidden text-slate-400 hover:text-white"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-4 ml-auto">
            <div className="relative">
              <button
                className="flex items-center gap-2 text-sm text-slate-300 hover:text-white transition-colors"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
              >
                <div className="w-8 h-8 bg-cyan-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-xs">U</span>
                </div>
                <span className="hidden sm:inline">User</span>
                <ChevronDown size={14} />
              </button>

              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-lg border border-slate-700 shadow-xl z-50">
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
                  >
                    <LogOut size={16} />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
