import React, { useEffect } from "react";
import Navbar from "../components/Navbar";
import Topbar from "../global/Topbar";
import Sidebar from "../global/Sidebar";
import Dashboard from "./Dashboard";
import "../styles/Home.css";

import { Routes, Route, Navigate } from "react-router-dom";

const Home = () => {
  useEffect(() => {
    <Navigate path="/dash" />;
  }, []);

  return (
    <div className="app">
      <Sidebar />
      <main className="content">
        <Topbar />
        {/* <Navbar /> */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
};

export default Home;
