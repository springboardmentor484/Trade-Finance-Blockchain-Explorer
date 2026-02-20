import { Link, useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/tradesecure-logo.png";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const role = localStorage.getItem("role");
  const org = localStorage.getItem("org");

  const isActive = (path) =>
    location.pathname === path
      ? "text-blue-400 border-b-2 border-blue-400"
      : "text-gray-300 hover:text-white";

  const logout = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <nav className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="leading-tight">
            <img
              src={logo}
              alt="TradeSecure Logo"
              className="h-50 w-40 object-cover"
            />
            <span className="block text-sm/4 text-slate-400">
                Trade Finance Blockchain Explorer
            </span>
          </div>
        </div>

        {/* Links */}
        <div className="hidden md:flex items-center gap-6 text-sm font-medium">
          <Link className={isActive("/dashboard")} to="/dashboard">
            Dashboard
          </Link>
          <Link className={isActive("/documents")} to="/documents">
            Documents
          </Link>
          <Link className={isActive("/transactions")} to="/transactions">
            Transactions
          </Link>
          <Link className={isActive("/profile")} to="/profile">
            Profile
          </Link>
          

          {/* Primary CTA – role-based */}
          {(role === "buyer" || role === "seller") && (
            <Link
              to="/upload"
              className="ml-2 bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700 transition shadow"
            >
              + Upload
            </Link>
          )}

          {role === "auditor" && (
            <Link
              to="/auditor"
              className="text-yellow-400 hover:text-yellow-300 font-medium"
            >
              🕵️ Auditor Panel
            </Link>
          )}

        </div>

        {/* Right */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:block text-right">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              {role}
            </p>
            <p className="text-sm font-medium text-white">
              {org}
            </p>
          </div>

          <button
            onClick={logout}
            className="bg-red-500/90 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg text-sm transition"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
