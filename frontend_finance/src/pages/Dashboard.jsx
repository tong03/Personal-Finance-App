import React from "react";
import { Box, useTheme, Typography } from "@mui/material";
import { tokens } from "../theme";
import api from "../api";
import "../styles/Dashboard.css";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

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
          <button className="link-btn" onClick={handleTesting}>
            Link Account
          </button>
          <div id="textField"></div>
        </Box>
        {/* ROW 2 */}
        <Box gridColumn="span 12" backgroundColor={colors.greenAccent[500]}>
          <button className="transaction-btn">Get Transactions</button>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
