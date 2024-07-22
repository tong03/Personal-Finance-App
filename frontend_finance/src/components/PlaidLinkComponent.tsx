import React, { useEffect, useCallback, useState } from "react";
import api from "../api";
import { usePlaidLink } from "react-plaid-link";

interface LinkProps {
  linkToken: string | null;
}

const Link: React.FC<LinkProps> = (props: LinkProps) => {
  const onSuccess = useCallback((public_token: string, metadata: any) => {
    api
      .post("/financeAccess/exchange_public_token/", { public_token })
      .then((response) => {
        console.log("Access token set:", response.data);
      })
      .catch((error) => {
        console.log("Error setting access token:", error);
      });
  }, []);

  const config: Parameters<typeof usePlaidLink>[0] = {
    token: props.linkToken!,
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);
  return (
    <button onClick={() => open()} disabled={!ready}>
      Link Account
    </button>
  );
};

const PlaidLinkComponent: React.FC = () => {
  const [linkToken, setLinkToken] = useState(null);

  const generateToken = async () => {
    try {
      console.log("Inside generateToken!");
      const response = await api.post("/financeAccess/create_link_token/");
      console.log("Response:", response);
      const data = response.data;
      console.log("Response Data:", data); // Log the response data
      setLinkToken(data.link_token);
    } catch (error) {
      console.log("Error generating link token:", error);
    }
  };

  useEffect(() => {
    generateToken();
  }, []);

  console.log("Link Token:", linkToken);
  return linkToken ? <Link linkToken={linkToken} /> : null;
};

export default PlaidLinkComponent;
