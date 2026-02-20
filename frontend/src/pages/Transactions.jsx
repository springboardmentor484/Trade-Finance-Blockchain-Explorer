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

  const statusStyles = (status) => {
    if (status === "completed") {
      return {
        badge: "bg-green-100 text-green-700 border-green-300",
        border: "border-l-green-500",
      };
    }
    if (status === "in_progress") {
      return {
        badge: "bg-yellow-100 text-yellow-700 border-yellow-300",
        border: "border-l-yellow-500",
      };
    }
    if (status === "disputed") {
      return {
        badge: "bg-red-100 text-red-700 border-red-300",
        border: "border-l-red-500",
      };
    }
    return {
      badge: "bg-gray-100 text-gray-700 border-gray-300",
      border: "border-l-gray-400",
    };
  };

  return (
    <div className="p-8 max-w-5xl mx-auto bg-gray-50 min-h-screen">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold">🔁 Transactions</h2>
          <p className="text-sm text-gray-500">Track all your trade flows</p>
        </div>

        <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
          Total: {txs.length}
        </span>
      </div>

      {txs.length === 0 && (
        <div className="border rounded-lg p-8 text-center text-gray-600 bg-white shadow">
          No transactions found.
        </div>
      )}

      <div className="space-y-4">
        {txs.map(tx => {
          const styles = statusStyles(tx.status);

          return (
            <Link to={`/transaction/${tx.id}`} key={tx.id}>
              <div
                className={`border-l-4 ${styles.border} bg-white rounded-xl p-5 shadow-sm hover:shadow-md hover:scale-[1.01] transition transform cursor-pointer`}
              >
                <div className="flex items-center justify-between mb-3">
                  <p className="font-semibold text-lg">
                    Transaction #{tx.id}
                  </p>

                  <span
                    className={`px-3 py-1 text-xs font-semibold rounded-full border ${styles.badge}`}
                  >
                    {tx.status.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">
                  <p>
                    👤 <span className="font-medium text-gray-900">Buyer:</span>{" "}
                    {tx.buyer_name}
                  </p>

                  <p>
                    🏭 <span className="font-medium text-gray-900">Seller:</span>{" "}
                    {tx.seller_name}
                  </p>
                </div>

                <div className="mt-3 text-sm text-gray-800">
                  💰 <span className="font-medium text-gray-900">Amount:</span>{" "}
                  {tx.amount} {tx.currency}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
