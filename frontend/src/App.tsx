import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Documents from "./pages/Documents";
import UploadDocument from "./pages/UploadDocument";
import LedgerExplorer from "./pages/LedgerExplorer";
import Signup from "./pages/Signup";
import Transactions from "./pages/Transactions";
import Alerts from "./pages/Alerts";
import Riskscores from "./pages/Riskscores";
import AuditLogs from "./pages/AuditLogs";
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/upload" element={<UploadDocument />} />
        <Route path="/ledger/:id" element={<LedgerExplorer />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/transactions" element={<Transactions/>}/>
        <Route path="/alerts" element={<Alerts/>}/>
        <Route path="/Riskscores" element={<Riskscores/>}/>
        <Route path="/AuditLogs" element={<AuditLogs/>}/>
      </Routes>
    </BrowserRouter>
  );
}