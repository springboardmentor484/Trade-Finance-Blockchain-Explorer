// import { BrowserRouter, Routes, Route } from "react-router-dom";
// import Login from "./pages/Login";
// import Profile from "./pages/Profile";
// import Documents from "./pages/Documents";
// import DocumentDetail from "./pages/DocumentDetail";
// import UploadDocument from "./pages/UploadDocument";
// import Transactions from "./pages/Transactions";
// import TransactionDetail from "./pages/TransactionDetail";
// import Dashboard from "./pages/Dashboard";
// import Navbar from "./pages/Navbar";


// function App() {
//   return (
//     <BrowserRouter>
      
//       <Routes>
//         <Route path="/" element={<Login />} />
//         <Route path="/profile" element={<Profile />} />
//         <Route path="/documents" element={<Documents />} />
//         <Route path="/document/:id" element={<DocumentDetail />} />
//         <Route path="/upload" element={<UploadDocument />} />
//         <Route path="/transactions" element={<Transactions />} />
//         <Route path="/transaction/:id" element={<TransactionDetail />} />
//         <Route path="/dashboard" element={<Dashboard />} />

//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;


import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Documents from "./pages/Documents";
import DocumentDetail from "./pages/DocumentDetail";
import UploadDocument from "./pages/UploadDocument";
import Transactions from "./pages/Transactions";
import TransactionDetail from "./pages/TransactionDetail";
import Dashboard from "./pages/Dashboard";
import ProtectedLayout from "./components/ProtectedLayout";
import AuditorVerification from "./pages/AuditorVerification";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<Login />} />

        {/* Protected */}
        <Route
          path="/dashboard"
          element={
            <ProtectedLayout>
              <Dashboard />
            </ProtectedLayout>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedLayout>
              <Profile />
            </ProtectedLayout>
          }
        />

        <Route
          path="/documents"
          element={
            <ProtectedLayout>
              <Documents />
            </ProtectedLayout>
          }
        />

        <Route
          path="/document/:id"
          element={
            <ProtectedLayout>
              <DocumentDetail />
            </ProtectedLayout>
          }
        />

        <Route
          path="/upload"
          element={
            <ProtectedLayout>
              <UploadDocument />
            </ProtectedLayout>
          }
        />

        <Route
          path="/transactions"
          element={
            <ProtectedLayout>
              <Transactions />
            </ProtectedLayout>
          }
        />

        <Route
          path="/transaction/:id"
          element={
            <ProtectedLayout>
              <TransactionDetail />
            </ProtectedLayout>
          }
        />

        <Route
          path="/auditor"
          element={
            <ProtectedLayout>
              {localStorage.getItem("role") === "auditor" ? (
                <AuditorVerification />
              ) : (
                <Navigate to="/dashboard" />
              )}
            </ProtectedLayout>
          }
        />



      </Routes>
    </BrowserRouter>
  );
}

export default App;
