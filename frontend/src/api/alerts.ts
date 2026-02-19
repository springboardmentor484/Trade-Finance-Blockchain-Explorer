import client from "./client";

export const getAlerts = async () => {
  const response = await client.get("/alerts/");
  return response.data;
};