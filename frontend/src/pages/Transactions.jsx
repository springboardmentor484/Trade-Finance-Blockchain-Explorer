import { useEffect, useState } from "react";
import api from "../services/api";
import { Link } from "react-router-dom";

export default function Transactions() {
  const [txs, setTxs] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api.get("/transactions", {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => setTxs(res.data))
    .catch(() => alert("Failed to load transactions"));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">My Transactions</h2>

      {txs.length === 0 && (
        <p className="text-gray-600">No transactions found.</p>
      )}

      <div className="space-y-4">
        {txs.map(tx => (
          <Link to={`/transaction/${tx.id}`} key={tx.id}>
            <div className="border rounded p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex justify-between">
                <p className="font-medium">Transaction #{tx.id}</p>
                <span
                  className={`px-2 py-1 text-sm rounded ${
                    tx.status === "completed"
                      ? "bg-green-100 text-green-700"
                      : tx.status === "in_progress"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {tx.status}
                </span>
              </div>

              <p className="text-sm text-gray-600">
                Buyer: {tx.buyer_id} | Seller: {tx.seller_id}
              </p>
              <p className="text-sm text-gray-700">
                Amount: {tx.amount} {tx.currency}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
