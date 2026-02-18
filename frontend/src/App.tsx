import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Documents from "./pages/Documents";
import UploadDocument from "./pages/UploadDocument";
import LedgerExplorer from "./pages/LedgerExplorer";
import Signup from "./pages/Signup";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/upload" element={<UploadDocument />} />
        <Route path="/ledger/:id" element={<LedgerExplorer />} />
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </BrowserRouter>
  );
}