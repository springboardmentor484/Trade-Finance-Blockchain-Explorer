import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

type User = {
  id: number;
  name: string;
  email: string;
  role: string;
  org: string;
};

const AuthContext = createContext<{ user: User | null }>({ user: null });

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api.get("/auth/user")
      .then(res => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  return (
    <AuthContext.Provider value={{ user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);