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
  const [monthlyTotal, setMonthlyTotal] = useState([]);

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
    try {
      setPageState((old) => ({ ...old, isLoading: true }));
      const res = await api.post(
        `/financeAccess/get_transactions/?page=${pageState.page}&per_page=${pageState.pageSize}`
      );
      const data = res.data;
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

  const fetchAllTransactionsForMonthlyTotal = async () => {
    try {
      let allTransactions = [];
      let currentPage = 1;
      let totalTransactions = 0;
      const pageSize = 10;

      while (true) {
        const res = await api.post(
          `/financeAccess/get_transactions/?page=${currentPage}&per_page=${pageSize}`
        );
        const data = res.data;
        totalTransactions = data.total;

        const transactions = data.transactions.map((transaction, idx) => ({
          id: idx + 1 + (currentPage - 1) * pageSize,
          name: transaction.name,
          amount: parseFloat(transaction.amount),
          category: transaction.category,
          date: transaction.date,
        }));

        allTransactions = [...allTransactions, ...transactions];

        if (allTransactions.length >= totalTransactions) {
          break;
        }

        currentPage++;
      }

      const monthlyTotalMap = allTransactions.reduce((acc, transaction) => {
        const date = new Date(transaction.date);
        const monthYear = `${date.getMonth() + 1}-${date.getFullYear()}`;
        if (!acc[monthYear]) {
          acc[monthYear] = 0;
        }
        acc[monthYear] += transaction.amount;
        return acc;
      }, {});

      const monthlyTotalArr = Object.entries(monthlyTotalMap).map(
        ([monthYear, total]) => ({ monthYear, total: total.toFixed(2) })
      );

      setMonthlyTotal(monthlyTotalArr);
    } catch (error) {
      console.log("Error:", error);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [pageState.page, pageState.pageSize]);

  useEffect(() => {
    fetchAllTransactionsForMonthlyTotal();
  }, []);

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
        {/* Link Account Box */}
        <Box gridColumn="span 3" backgroundColor={colors.primary[100]}>
          <button className="link-btn" onClick={handleLinkAccountClick}>
            Create Link
          </button>
          {showPlaidLink && <PlaidLinkComponent />}
        </Box>
        {/* Get Account Box */}
        <Box gridColumn="span 3" backgroundColor={colors.primary[300]}>
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
        {/* Delete All PlaidItems/Get Transactions Box */}
        <Box gridColumn="span 3" backgroundColor={colors.primary[300]}>
          <Box display="flex" justifyContent="space-between">
            <button onClick={handleTesting}>Test Click</button>
            <button
              className="transaction-btn"
              onClick={handleGetTransactionsClick}
            >
              Get Transactions
            </button>
          </Box>
          <div id="textField"></div>
        </Box>
        {/* Monthly Amount Summary */}
        <Box gridColumn="span 3" backgroundColor={colors.primary[100]}>
          <Box
            display="flex"
            flexDirection="column"
            height="100%"
            sx={{ p: "0 1rem 1rem 1rem" }}
          >
            <Typography
              variant="h4"
              color={colors.primary[500]}
              sx={{ pb: "0.5rem" }}
            >
              Monthly Spending
            </Typography>
            <Box backgroundColor={colors.primary[300]} flexGrow={1}>
              <ul>
                {monthlyTotal.map((item, index) => (
                  <li key={index}>
                    {item.monthYear}: ${item.total}
                  </li>
                ))}
              </ul>
            </Box>
          </Box>
        </Box>
        {/* ROW 2 -- Transaction Container */}
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
