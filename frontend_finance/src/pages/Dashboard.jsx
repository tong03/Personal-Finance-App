import React, { useState } from "react";
import { Box, useTheme, Typography } from "@mui/material";
import { tokens } from "../theme";
import api from "../api";
import "../styles/Dashboard.css";
import PlaidLinkComponent from "../components/PlaidLinkComponent";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [showPlaidLink, setShowPlaidLink] = useState(false);

  const handleTesting = async () => {
    try {
      const res = await api.get("/financeAccess/testing/");
      const data = res.data; // axios automatically parses JSON response
      const message = data.message;
      document.getElementById("textField").innerText = message;
    } catch (error) {
      console.log("Error: ", error);
    }
  };

  const handleLinkAccountClick = () => {
    setShowPlaidLink(true);
  };

  return (
    <Box m="20px">
      {/* GRIDS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="250px"
        gap="40px"
      >
        {/* ROW 1 */}
        <Box gridColumn="span 12" backgroundColor={colors.primary[100]}>
          <button className="link-btn" onClick={handleLinkAccountClick}>
            Create Link
          </button>
          {showPlaidLink && <PlaidLinkComponent />}
        </Box>
        {/* ROW 2 */}
        <Box gridColumn="span 12" backgroundColor={colors.greenAccent[500]}>
          <button className="transaction-btn" onClick={handleTesting}>
            Get Transactions
          </button>
          <div id="textField"></div>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
