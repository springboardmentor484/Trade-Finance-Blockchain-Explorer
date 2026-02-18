import api from "./client";

export const loginUser = async (data: {
  email: string;
  password: string;
}) => {
  const res = await api.post("/auth/login", data, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  return res.data;
};


export const getCurrentUser = async () => {
  const res = await api.get("/auth/user");
  return res.data;
};

export const signupUser = async (data: {
  name: string;
  email: string;
  password: string;
  org: string;
  role: "bank" | "coperate" | "auditor" | "admin";
}) => {
  const res = await api.post("/auth/signup", data);
  return res.data;
};