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
  const [transactions, setTransactions] = useState([]);

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

  const handleGetTransactionsClick = async () => {
    try {
      const res = await api.post("/financeAccess/get_transactions/");
      const data = res.data;
      setTransactions(data);
    } catch (error) {
      console.log("Error:", error);
    }
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
        <Box gridColumn="span 6" backgroundColor={colors.primary[100]}>
          <button className="link-btn" onClick={handleLinkAccountClick}>
            Create Link
          </button>
          {showPlaidLink && <PlaidLinkComponent />}
        </Box>
        <Box gridColumn="span 6" backgroundColor={colors.primary[300]}>
          <button onClick={handleTesting}>Test Click</button>
          <div id="textField"></div>
        </Box>
        {/* ROW 2 */}
        <Box gridColumn="span 12" backgroundColor={colors.greenAccent[500]}>
          <button
            className="transaction-btn"
            onClick={handleGetTransactionsClick}
          >
            Get Transactions
          </button>
        </Box>
        {/* ROW 3 */}
        <Box gridColumn="span 12" backgroundColor={colors.blueAccent[500]}>
          <Typography variant="h6">Transactions:</Typography>
          <ul>
            {transactions.map((transaction, index) => (
              <li key={index}>
                {transaction.name}: {transaction.amount} - {transaction.date}
              </li>
            ))}
          </ul>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
