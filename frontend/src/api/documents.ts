import api from "./client";

export const uploadDocument = async (data: FormData) => {
  const res = await api.post("/documents/upload", data, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  return res.data;
};


export const getDocumentById = async (id: number) => {
  const res = await api.get(`/documents/${id}`);
  return res.data;
};




export const takeAction = async (docId: number, action: string) => {
  const res = await api.post(`/actions/${docId}/${action}`);
  return res.data;
};