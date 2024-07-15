import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";

const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  // useEffect to run on load
  useEffect(() => {
    auth().catch(() => setIsAuthenticated(false));
  }, []);

  // refreshToken check
  const getRefreshToken = async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN);
    // try to use the refreshToken to get new ACCESS_TOKEN
    try {
      const res = await api.get("/api/token/refresh/", {
        refresh: refreshToken,
      });
      // if refreshToken is still valid, then set new ACCESS_TOKEN
      if (res.status == 200) {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
      alert(error);
      setIsAuthenticated(false);
    }
  };

  // auth
  const auth = async () => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      setIsAuthenticated(false);
      return;
    }

    // Checking ACCESS_TOKEN expiration
    decoded = jwtDecode(token);
    tokenExp = decoded.exp;
    current = Date.now() / 1000;

    // if token expired, must check and run refreshToken
    if (current > tokenExp) {
      await getRefreshToken();
    } else {
      setIsAuthenticated(true);
    }
  };

  // while isAuthenticated still null, display placeholder
  if (isAuthenticated == null) {
    return <div>Loading...</div>;
  }
  return isAuthenticated ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;
