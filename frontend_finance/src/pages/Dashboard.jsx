import React, { useState, useEffect } from "react";
import { tokens } from "../theme";
import api from "../api";
import "../styles/Dashboard.css";
import PlaidLinkComponent from "../components/PlaidLinkComponent";

// MUI Stuffs
import { Box, useTheme, Typography } from "@mui/material";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [showPlaidLink, setShowPlaidLink] = useState(false);
  const [accounts, setAccounts] = useState([]);

  const [pageState, setPageState] = useState({
    isLoading: false,
    data: [],
    total: 0,
    page: 1,
    pageSize: 10,
  });

  const columns = [
    { field: "id", headerName: "ID" },
    {
      field: "name",
      headerName: "Name",
      flex: 1,
    },
    {
      field: "amount",
      headerName: "Amount",
      type: "decimal",
      flex: 1,
    },
    {
      field: "category",
      headerName: "Category",
      flex: 1,
    },
    {
      field: "date",
      headerName: "Date",
      flex: 1,
    },
  ];

  const fetchTransactions = async () => {
    console.log("Clicked!");
    try {
      setPageState((old) => ({ ...old, isLoading: true }));
      const res = await api.post(
        `/financeAccess/get_transactions/?page=${pageState.page}&per_page=${pageState.pageSize}`
      );
      const data = res.data;
      console.log(data);
      const formattedTransactions = data.transactions.map(
        (transaction, idx) => ({
          id: idx + 1 + (pageState.page - 1) * pageState.pageSize,
          name: transaction.name,
          amount: transaction.amount,
          category: transaction.category,
          date: transaction.date,
        })
      );
      setPageState((old) => ({
        ...old,
        isLoading: false,
        data: formattedTransactions,
        total: data.total,
      }));
    } catch (error) {
      console.log("Error:", error);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [pageState.page, pageState.pageSize]);

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

  const handleGetTransactionsClick = () => {
    fetchTransactions();
  };

  const handleGetAccountsClick = async () => {
    try {
      const res = await api.get("/financeAccess/get_accounts/");
      // Debug log
      console.log("Accounts Response:", res.data);
      const data = res.data.accounts;
      setAccounts(data);
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
        gridTemplateRows="250px 400px auto"
        gap="25px"
      >
        {/* ROW 1 */}
        <Box gridColumn="span 6" backgroundColor={colors.primary[100]}>
          <button className="link-btn" onClick={handleLinkAccountClick}>
            Create Link
          </button>
          {showPlaidLink && <PlaidLinkComponent />}
          <button
            className="transaction-btn"
            onClick={handleGetTransactionsClick}
          >
            Get Transactions
          </button>
        </Box>
        <Box gridColumn="span 4" backgroundColor={colors.primary[300]}>
          <button className="accounts-btn" onClick={handleGetAccountsClick}>
            Get Accounts
          </button>
          <div id="accountsField">
            <ul>
              {accounts.map((account, index) => (
                <li key={index}>
                  {account.name} - ${account.balances.available}{" "}
                  {account.balances.iso_currency_code}
                </li>
              ))}
            </ul>
          </div>
        </Box>
        <Box gridColumn="span 2" backgroundColor={colors.primary[300]}>
          <button onClick={handleTesting}>Test Click</button>
          <div id="textField"></div>
        </Box>
        {/* ROW 2 */}
        <Box
          gridColumn="span 12"
          backgroundColor={colors.primary[400]}
          className="transaction-container"
          sx={{
            p: "10px",
          }}
        >
          <Typography variant="h3" sx={{ p: "0 10px 10px 0" }}>
            Recent Transactions:
          </Typography>
          <Box
            flexGrow={1}
            overflow="auto"
            sx={{
              "& .MuiDataGrid-root": {
                border: "none",
              },
              "& .MuiDataGrid-cell": {
                borderBottom: "none",
              },
              "& .MuiDataGrid-columnHeaders": {
                backgroundColor: `${colors.blueAccent[700]} !important`,
                borderBottom: "none",
                "--DataGrid-containerBackground": "none",
              },
              "& .MuiDataGrid-virtualScroller": {
                backgroundColor: colors.primary[400],
              },
              "& .MuiDataGrid-footerContainer": {
                borderTop: "none",
                backgroundColor: colors.blueAccent[700],
              },
              "& .MuiDataGrid-toolbarContainer .MuiButton-text": {
                color: `${colors.grey[100]} !important`,
              },
            }}
          >
            <DataGrid
              rows={pageState.data}
              rowCount={pageState.total}
              getRowId={(row) => row.id}
              columns={columns}
              pageSizeOptions={[5, 10, 25, 100]}
              page={pageState.page - 1}
              pageSize={pageState.pageSize}
              onPageSizeChange={(newPageSize) =>
                setPageState((old) => ({ ...old, pageSize: newPageSize }))
              }
              onPaginationModelChange={(paginationModel) => {
                console.log("In onPaginationModelChange");
                setPageState((old) => ({
                  ...old,
                  page: paginationModel.page + 1,
                  pageSize: paginationModel.pageSize,
                }));
              }}
              pagination
              paginationMode="server"
              initialState={{
                pagination: {
                  paginationModel: { pageSize: 10, page: 0 },
                },
              }}
              loading={pageState.isLoading}
              slots={{ toolbar: GridToolbar }}
            />
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
