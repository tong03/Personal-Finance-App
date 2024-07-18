import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import Register from "./pages/Register";
import Login from "./pages/Login";
import { useEffect } from "react";

import { ColorModeContext, useMode } from "./theme";
import { CssBaseline, ThemeProvider } from "@mui/material";

function Logout() {
  localStorage.clear();
  return <Navigate to="/login" />;
}

function App() {
  const [theme, colorMode] = useMode();

  useEffect(() => {
    // Apply styles to the body element
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.boxSizing = "border-box";

    // Clean up the styles when the component is unmounted
    return () => {
      document.body.style.margin = "";
      document.body.style.padding = "";
      document.body.style.boxSizing = "";
    };
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ColorModeContext.Provider value={colorMode}>
                <ThemeProvider theme={theme}>
                  <CssBaseline />
                  <Home />
                </ThemeProvider>
              </ColorModeContext.Provider>
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
