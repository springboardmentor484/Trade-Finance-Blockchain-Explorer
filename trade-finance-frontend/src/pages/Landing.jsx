import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, Lock, FileText, BarChart3 } from 'lucide-react';

export const Landing = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-blue-600">
              Trade Finance Blockchain Explorer
            </h1>
            <div className="flex gap-4">
              {isAuthenticated ? (
                <Link to="/documents" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link to="/login" className="px-4 py-2 text-gray-700 hover:text-gray-900">
                    Sign In
                  </Link>
                  <Link to="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Transparent Trade Finance on Blockchain
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            A comprehensive platform for managing letters of credit, purchase orders, bills of lading, and invoices with tamper-proof audit trails.
          </p>
          {!isAuthenticated && (
            <Link
              to="/login"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-medium"
            >
              Get Started <ArrowRight size={20} />
            </Link>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Key Features
          </h3>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-lg shadow-md">
              <Lock className="text-blue-600 mb-4" size={32} />
              <h4 className="text-xl font-bold text-gray-900 mb-2">
                Tamper-Proof Audit Trail
              </h4>
              <p className="text-gray-600">
                SHA-256 hashing ensures every document is immutable and verifiable
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-lg shadow-md">
              <FileText className="text-green-600 mb-4" size={32} />
              <h4 className="text-xl font-bold text-gray-900 mb-2">
                Complete Document Lifecycle
              </h4>
              <p className="text-gray-600">
                Track POs, LOCs, BOLs, Invoices, and more through their entire journey
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-lg shadow-md">
              <BarChart3 className="text-orange-600 mb-4" size={32} />
              <h4 className="text-xl font-bold text-gray-900 mb-2">
                Risk Scoring & Analytics
              </h4>
              <p className="text-gray-600">
                Real-time risk assessment and comprehensive transaction analytics
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trade Flow Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Complete Trade Flow
        </h3>
        
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-lg">
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
                1
              </div>
              <p className="font-semibold text-gray-900">Create PO</p>
              <p className="text-sm text-gray-600">Buyer initiates</p>
            </div>
            <div className="flex items-center justify-center">
              <div className="hidden md:block w-full h-1 bg-blue-300"></div>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
                2
              </div>
              <p className="font-semibold text-gray-900">Issue LOC</p>
              <p className="text-sm text-gray-600">Bank confirms</p>
            </div>
            <div className="flex items-center justify-center">
              <div className="hidden md:block w-full h-1 bg-blue-300"></div>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
                3
              </div>
              <p className="font-semibold text-gray-900">Ship BOL</p>
              <p className="text-sm text-gray-600">Seller ships goods</p>
            </div>
            <div className="flex items-center justify-center">
              <div className="hidden md:block w-full h-1 bg-blue-300"></div>
            </div>
            <div className="text-center">
              <div className="bg-green-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
                4
              </div>
              <p className="font-semibold text-gray-900">Pay Invoice</p>
              <p className="text-sm text-gray-600">Complete</p>
            </div>
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Multi-Role Support
          </h3>
          
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { title: 'Bank', desc: 'Issue LOCs, verify, process payments' },
              { title: 'Corporate', desc: 'Create POs, receive goods, settle invoices' },
              { title: 'Auditor', desc: 'Verify documents, ensure compliance' },
              { title: 'Admin', desc: 'Manage users, monitor system' }
            ].map((role, idx) => (
              <div key={idx} className="bg-white p-6 rounded-lg text-center border-l-4 border-blue-600">
                <h4 className="font-bold text-gray-900 mb-2">{role.title}</h4>
                <p className="text-sm text-gray-600">{role.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            Trade Finance Blockchain Explorer &copy; 2024. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};
