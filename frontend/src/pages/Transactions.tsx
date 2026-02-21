import { useEffect, useState } from "react";
import {
  getTransactions,
  updateTransactionStatus,
} from "../api/transactions";

interface Transaction {
  id: number;
  buyer_id: number;
  seller_id: number;
  amount: number;
  currency: string;
  status: string;
}

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const fetchTransactions = async () => {
    const data = await getTransactions();
    setTransactions(data);
  };

  const handleStatusChange = async (id: number, status: string) => {
    await updateTransactionStatus(id, status);
    fetchTransactions();
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Transactions</h1>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th>ID</th>
            <th>Buyer</th>
            <th>Seller</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Update</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id} className="text-center border-t">
              <td>{tx.id}</td>
              <td>{tx.buyer_id}</td>
              <td>{tx.seller_id}</td>
              <td>{tx.amount}</td>
              <td>{tx.status}</td>
              <td>
                <select
                  value={tx.status}
                  onChange={(e) =>
                    handleStatusChange(tx.id, e.target.value)
                  }
                  className="border p-1"
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="expired">Expired</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}