import client from "./client";

export const getTransactions = async () => {
  const response = await client.get("/transactions/");
  return response.data;
};

export const updateTransactionStatus = async (
  transactionId: number,
  status: string
) => {
  const response = await client.put(
    `/transactions/${transactionId}/status`,
    { status }
  );
  return response.data;
};

export const expirePendingTransactions = async () => {
  const response = await client.post("/transactions/expire-pending");
  return response.data;
};