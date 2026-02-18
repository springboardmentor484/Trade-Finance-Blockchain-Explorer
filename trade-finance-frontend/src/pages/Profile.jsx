import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut } from 'lucide-react';

export const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile</h1>

          <div className="grid md:grid-cols-2 gap-8">
            {/* User Information */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6">Account Information</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-600">Full Name</label>
                  <p className="text-lg font-medium text-gray-900">{user.name}</p>
                </div>

                <div>
                  <label className="text-sm text-gray-600">Email</label>
                  <p className="text-lg font-medium text-gray-900">{user.email}</p>
                </div>

                <div>
                  <label className="text-sm text-gray-600">Organization</label>
                  <p className="text-lg font-medium text-gray-900">{user.org_name}</p>
                </div>

                <div>
                  <label className="text-sm text-gray-600">Role</label>
                  <div className="mt-1">
                    <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Permissions */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6">Permissions</h2>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900 mb-4">
                  You have access to features based on your role:
                </p>
                
                <ul className="space-y-2 text-sm text-blue-800">
                  {user.role === 'bank' && (
                    <>
                      <li>✓ Issue Letters of Credit</li>
                      <li>✓ Process payments</li>
                      <li>✓ View all transactions</li>
                      <li>✓ Verify documents</li>
                    </>
                  )}
                  {user.role === 'corporate' && (
                    <>
                      <li>✓ Create Purchase Orders</li>
                      <li>✓ Upload Bills of Lading</li>
                      <li>✓ Create Invoices</li>
                      <li>✓ View transaction history</li>
                    </>
                  )}
                  {user.role === 'auditor' && (
                    <>
                      <li>✓ Verify documents</li>
                      <li>✓ View audit logs</li>
                      <li>✓ Access analytics</li>
                      <li>✓ Review risk scores</li>
                    </>
                  )}
                  {user.role === 'admin' && (
                    <>
                      <li>✓ Manage users</li>
                      <li>✓ View all transactions</li>
                      <li>✓ Access analytics</li>
                      <li>✓ Configure system</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>

          {/* Logout Button */}
          <div className="mt-8 pt-8 border-t">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-medium transition"
            >
              <LogOut size={20} />
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
