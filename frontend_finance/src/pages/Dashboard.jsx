import React from "react";
import { Box, useTheme, Typography } from "@mui/material";
import { tokens } from "../theme";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

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
        <Box gridColumn="span 12" backgroundColor={colors.primary[100]}></Box>
        {/* ROW 2 */}
        <Box
          gridColumn="span 12"
          backgroundColor={colors.greenAccent[500]}
        ></Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
