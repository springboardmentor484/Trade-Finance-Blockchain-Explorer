import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Documents from "./pages/Documents";
import DocumentDetail from "./pages/DocumentDetail";
import UploadDocument from "./pages/UploadDocument";
import Transactions from "./pages/Transactions";
import TransactionDetail from "./pages/TransactionDetail";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/document/:id" element={<DocumentDetail />} />
        <Route path="/upload" element={<UploadDocument />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/transaction/:id" element={<TransactionDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

