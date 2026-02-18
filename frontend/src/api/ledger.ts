import api from "./client";

export const getLedgerForDocument = async (documentId: number|string) => {
  const res = await api.get(`/ledger/${documentId}`);
  return res.data;
};