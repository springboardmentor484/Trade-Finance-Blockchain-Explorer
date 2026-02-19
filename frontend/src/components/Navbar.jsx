import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [showMenu, setShowMenu] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-gray-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/documents" className="flex items-center space-x-2 font-bold text-xl hover:text-blue-400">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span>⚡</span>
            </div>
            <span>TF Explorer</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              to="/documents"
              className={`px-3 py-2 rounded ${
                isActive("/documents") ? "bg-blue-600" : "hover:bg-gray-800"
              }`}
            >
              📄 Documents
            </Link>
            <Link
              to="/transactions"
              className={`px-3 py-2 rounded ${
                isActive("/transactions") ? "bg-blue-600" : "hover:bg-gray-800"
              }`}
            >
              💱 Transactions
            </Link>
            <Link
              to="/analytics"
              className={`px-3 py-2 rounded ${
                isActive("/analytics") ? "bg-blue-600" : "hover:bg-gray-800"
              }`}
            >
              📊 Analytics
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="text-2xl hover:text-blue-400"
            >
              ☰
            </button>

            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded shadow-lg z-10">
                <Link
                  to="/documents"
                  className="block px-4 py-2 hover:bg-blue-600 rounded-t"
                  onClick={() => setShowMenu(false)}
                >
                  📄 Documents
                </Link>
                <Link
                  to="/transactions"
                  className="block px-4 py-2 hover:bg-blue-600"
                  onClick={() => setShowMenu(false)}
                >
                  💱 Transactions
                </Link>
                <Link
                  to="/analytics"
                  className="block px-4 py-2 hover:bg-blue-600"
                  onClick={() => setShowMenu(false)}
                >
                  📊 Analytics
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setShowMenu(false);
                  }}
                  className="block w-full text-left px-4 py-2 hover:bg-red-600 rounded-b"
                >
                  🚪 Logout
                </button>
              </div>
            )}
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="hidden md:block bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-semibold transition"
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
